from pymote.logger import logger
from numpy import array, sqrt, dot, outer, concatenate, set_printoptions, \
                  arctan2, sin, cos, pi, mod, isnan
from numpy.linalg import eig, det
from numpy.dual import svd
from numpy.lib.type_check import imag, real
set_printoptions(precision=4)


# TODO: make BaseStitcher class as dist and aoa stitcher have much in common
class AoAStitcher(object):

    def __init__(self, method='horn', weight='', refine=''):
        # TODO: refactor to be compatible to diststitcher and Positions format
        raise(NotImplementedError)

        self.method = method
        self.weight = weight
        self.refine = refine

    def stitch(self, dst, src):
        """
        Stitch src cluster to dst cluster based on two or more common nodes
        between their subclusters. Stitching order is formed on maximum common
        nodes criteria. If number of common nodes is less than two src
        subcluster is only translated and rotated to dst cluster so it still
        remains independent subcluster. After each subcluster is stitched
        algorithm tries to stitch subclusters internally.
        Cluster is IniLoc dictionary with two keys:
        {'positions': {node1: array(x1,y1),
                       node2: array(x2,y2),
                       ...},
        'subclusters': [[node1 ... ]
                        [node6 ...]
                        ...]}
        If method is 'align' then only align (modify) src w.r.t. dst.
        """

        if self.method == 'horn' or self.method == 'align':
            stitch_method = self.stitch_subclusters_horn
        if self.method == 'arun':
            stitch_method = self.stitch_subclusters_arun

        # copy src['subclusters'] so it can be modified in while loop
        srcSubclusters = list(src['subclusters'])

        # while there are srcSubclusters do extraStitch and intraStitch
        while srcSubclusters:
            ###### extraStitch ######
            # find out which subclusters to stitch/add (max commonNodes)
            cnCount, srcSub, dstSub = \
                            self.get_stitch_subclusters(dst['subclusters'],
                                                        srcSubclusters)

            # stitch srcSub to dstSub using given method
            dstSubPos, srcSubPos = \
                stitch_method({k: v for k, v in dst['positions'].items()
                               if k in dstSub},
                              {k: v for k, v in src['positions'].items()
                               if k in srcSub})
            # update src node positions with aligned positions
            if cnCount > 1:
                if self.method == 'align':
                    for node, position in srcSubPos.items():
                        src['positions'][node] = position
                else:
                    # append new nodes to dstSub and set its position
                    for node, position in dstSubPos.items():
                        if not node in dstSub:  # only new nodes
                            dstSub.append(node)
                        dst['positions'][node] = position
            # delete srcSub from srcSubclusters
            # append new nodes and base (common node) to newSub
            else:
                newSub = []
                dst['subclusters'].append(newSub)
                for node, position in dstSubPos.items():
                    # only that is all of srcSub
                    if node in srcSub:
                        newSub.append(node)
                    dst['positions'][node] = position
                # align is not needed as size of minimum subcluster of
                # connected network is 2
            srcSubclusters.remove(srcSub)

            ###### intraStitch ######
            if self.method != 'align':
                self.intrastitch(dst)

    def intrastitch(self, dst):
        while 1:
            # find out if/which subclusters from dst to stitch to each other
            cnCount, srcDstSub, dstDstSub = \
                self.get_stitch_subclusters(dst['subclusters'],
                                            dst['subclusters'])
            if self.method == 'horn':
                stitch_method = self.stitch_subclusters_horn
            if self.method == 'arun':
                stitch_method = self.stitch_subclusters_arun

            if cnCount > 1:
                dstSubPos, _srcSubPos = \
                    stitch_method({k: v for k, v in dst['positions'].items()
                                        if k in dstDstSub},
                                  {k: v for k, v in dst['positions'].items()
                                        if k in srcDstSub},)
                # append new nodes to dstDstSub and set its positions
                for node, position in dstSubPos.items():
                    if not node in dstDstSub:  # only new nodes
                        dstDstSub.append(node)
                    dst['positions'][node] = position
                # delete srcDstSub from dst['subclusters']
                dst['subclusters'].remove(srcDstSub)
            else:
                # if there are no subclusters that could be intraStitched
                break

    def get_stitch_subclusters(self, dstSubclusters, srcSubclusters):
        """ Find out which subclusters to stitch based on max commonNodes
        criteria. Return subclusters to stitch and commonNode count. """
        if dstSubclusters == srcSubclusters and self.method != 'align':
            is_intra = True
        else:
            is_intra = False
        cn_count_max = 0
        dstSub = None
        srcSub = None
        for src_sc in srcSubclusters:
            for dst_sc in dstSubclusters:
                if (is_intra and src_sc != dst_sc) or not is_intra:
                    commonNodes = [node for node in dst_sc
                                   if node in src_sc]
                    cn_count = len(commonNodes)
                    if cn_count > cn_count_max:
                        cn_count_max = cn_count
                        dstSub = dst_sc
                        srcSub = src_sc

        # in intraStitch dst should be larger one
        if cn_count_max and is_intra and len(srcSub) > len(dstSub):
            tmp = dstSub
            dstSub = srcSub
            srcSub = tmp

        return cn_count_max, srcSub, dstSub

    def stitch_subclusters_horn(self, dstSubPos, srcSubPos):
        """ Take two subclusters as dictionary {node : position} where position
            is array([x,y,theta]) with at least one common node and return
            dstSubPos with appended missing nodes from srcSubPos. """
        commonNodes = list(set(dstSubPos.keys()) & set(srcSubPos.keys()))

        if self.weight == 'gdopdst':  # weight is gdop of dst nodes
            dstGdops = self.get_aoa_gdops(dstSubPos)
            # srcGdops = get_aoa_gdops(srcSubPos)
            # invert and normalize
            w_sum = sum([1. / gdop
                         for node, gdop in dstGdops.items()
                         if node in commonNodes])
            w_d = {node: 1. / gdop / w_sum
                   for node, gdop in dstGdops.items() if node in commonNodes}
        elif self.weight == 'gdopavg':  # sum of src and dst nodes gdops
            dstGdops = self.get_aoa_gdops(dstSubPos)
            srcGdops = self.get_aoa_gdops(srcSubPos)
            # sum gdops
            sumGdops = {}
            for node, gdop in dstGdops.items():
                if node in commonNodes:
                    sumGdops[node] = dstGdops[node] + srcGdops[node]
            # invert and normalize
            w_sum = sum([1. / gdop for node, gdop in sumGdops.items()])
            w_d = {node: 1. / gdop / w_sum for node, gdop in sumGdops.items()}
        else:
            w_d = {node: 1. / len(commonNodes) for node in commonNodes}

        # calculate centroids of both systems
        p_s = array([0., 0.])
        p_d = array([0., 0.])
        for cn in commonNodes:
            p_s += srcSubPos[cn][:2] * w_d[cn]
            p_d += dstSubPos[cn][:2] * w_d[cn]

        # scaling factor
        s = 1
        if len(commonNodes) > 1:
            s = sqrt(sum([sum((dstSubPos[cn][:2] - p_d) ** 2) * w_d[cn]
                          for cn in commonNodes]) /
                     sum([sum((srcSubPos[cn][:2] - p_s) ** 2) * w_d[cn]
                          for cn in commonNodes]))

        # rotation matrix
        if len(commonNodes) == 1:
            # rotate clockwise ori_src-ori_dst where ori are common node
            # estimated orientations in src and dst subclusters
            theta = dstSubPos[commonNodes[0]][2] - srcSubPos[commonNodes[0]][2]
            # in ccw direction
            R = array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        # for 2 commonNodes R must be calculated directly
        elif len(commonNodes) == 2:
            vector1 = dstSubPos[commonNodes[0]] - dstSubPos[commonNodes[1]]
            vector2 = srcSubPos[commonNodes[0]] - srcSubPos[commonNodes[1]]
            theta1 = arctan2(vector1[1], vector1[0])
            theta2 = arctan2(vector2[1], vector2[0])
            theta = theta1 - theta2
            # in ccw direction
            R = array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        else:
            M = sum([outer((dstSubPos[cn][:2] - p_d),
                           (srcSubPos[cn][:2] - p_s)) for cn in commonNodes])
            D, V = eig(dot(M.T, M))
            R = dot(M, (1 / sqrt(D[0]) * outer(V[:, 0], V[:, 0].conj().T) +
                        1 / sqrt(D[1]) * outer(V[:, 1], V[:, 1].conj().T)))
            # only rotation, if det(M)<0 it is reflection (Horn et.al)
            if det(M) < 0:
                # TODO: Umeyama
                assert det(R) < 0  # Umeyama1991
                logger.warning('M<0 indicates reflection not rotation, '
                               'check result')
                commonNodes[0].warnings = 'M<0'
        # translation vector
        t = p_d - dot(dot(s, R), p_s)

        logger.debug('R = %s', R.tolist())
        logger.debug('s = %f', s)
        logger.debug('t = %s', t.tolist())

        self.merge_subclusters(dstSubPos, srcSubPos, R, s, t)

        return dstSubPos, srcSubPos

    def stitch_subclusters_arun(self, dstSubPos, srcSubPos):
        """ Take two subclusters as dictionary {node : position} where position
            is array([x,y,theta]) with at least one common node and return
            dstSubPos with appended missing nodes from srcSubPos. """
        commonNodes = list(set(dstSubPos.keys()) & set(srcSubPos.keys()))

        if self.weight == 'gdopdst' or self.weight == 'gdopavg':
            logger.warning('Stitch weight not supported by arun stitch method')
            return

        # calculate centroids of both systems
        p_s = array([0., 0.])
        p_d = array([0., 0.])
        for cn in commonNodes:
            p_s += srcSubPos[cn][:2] / len(commonNodes)
            p_d += dstSubPos[cn][:2] / len(commonNodes)

        # rotation matrix
        if len(commonNodes) == 1:
            # rotate clockwise ori_src-ori_dst where ori are common node
            # estimated orientations in src and dst subclusters
            theta = dstSubPos[commonNodes[0]][2] - srcSubPos[commonNodes[0]][2]
            # in ccw direction
            R = array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        # for 2 commonNodes R must be calculated directly
        elif len(commonNodes) == 2:
            vector1 = dstSubPos[commonNodes[0]] - dstSubPos[commonNodes[1]]
            vector2 = srcSubPos[commonNodes[0]] - srcSubPos[commonNodes[1]]
            theta1 = arctan2(vector1[1], vector1[0])
            theta2 = arctan2(vector2[1], vector2[0])
            theta = theta1 - theta2
            # in ccw direction
            R = array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        else:
            H = dot(array([dstSubPos[cn][:2] - p_d for cn in commonNodes]).T,
                    array([srcSubPos[cn][:2] - p_s for cn in commonNodes]))
            # M = sum([outer((dstSubPos[cn][:2]-p_d),(srcSubPos[cn][:2]-p_s))
            #                for cn in commonNodes])
            U, D, Vh = svd(H)
            R = dot(U, Vh)
            # only rotation, if det(R)<0 it is reflection (Umeyama1991)
            if det(R) < 0:
                # TODO: Umeyama
                logger.warning('det(R)<0 indicates reflection not rotation, '
                               'check result')
                commonNodes[0].warnings = 'det(R)<0'

        # scaling factor
        s = sum(D) / sum([(srcSubPos[cn][0] - p_s[0]) ** 2 +
                        (srcSubPos[cn][1] - p_s[1]) ** 2
                        for cn in commonNodes])

        # translation vector
        t = p_d - dot(s * p_s, R.T)

        logger.debug('R_arun = %s', R.tolist())
        logger.debug('s_arun = %f', s)
        logger.debug('t_arun = %s', t.tolist())

        self.merge_subclusters(dstSubPos, srcSubPos, R, s, t)

        return dstSubPos, srcSubPos

    def merge_subclusters(self, dstSubPos, srcSubPos, R, s, t):
        """
        Append srcSubPos nodes to dstSubPos, optionally refine pos in dstSubPos
        """

        commonNodes = list(set(dstSubPos.keys()) & set(srcSubPos.keys()))
        assert not imag(R).any()
        R = real(R)
        # angle of rotation matrix R in ccw
        Rtheta = arctan2(R[1, 0], R[0, 0])

        if self.refine.startswith('gdop'):
            dstGdops = self.get_aoa_gdops(dstSubPos)
            srcGdops = self.get_aoa_gdops(srcSubPos)

        for node in srcSubPos.keys():
            if self.method == 'align':
                # only align position of source nodes
                srcSubPos[node] = \
        concatenate((t + dot(dot(s, R), srcSubPos[node][:2]),
                     array(mod([srcSubPos[node][2] - Rtheta], 2 * pi))))
            else:
                # set positions in destination subcluster
                if node in commonNodes:
                    if self.refine == 'average':
                        # calculate and take average for commonNodes
                        dstSubPos[node] = \
        concatenate(((dstSubPos[node][:2] +
                      (t + dot(dot(s, R), srcSubPos[node][:2]))) / 2,
                     array(mod([srcSubPos[node][2] - Rtheta], 2 * pi))))
                    elif self.refine == 'gdop':
                        # take gdop-weighted average for commonNodes
                        w_s = dstGdops[node]/(dstGdops[node] + srcGdops[node])
                        w_d = srcGdops[node]/(dstGdops[node] + srcGdops[node])
                        assert(not isnan(w_s) and not isnan(w_d))
                        dstSubPos[node] = \
        concatenate((dot(dstSubPos[node][:2], w_d) +
                     dot((t + dot(dot(s, R), srcSubPos[node][:2])), w_s),
                     array(mod([srcSubPos[node][2] - Rtheta], 2 * pi))))
                    elif self.refine == 'gdop_select':
                        # take gdop-weighted minumum node
                        w_s = dstGdops[node]/(dstGdops[node] + srcGdops[node])
                        w_d = srcGdops[node]/(dstGdops[node] + srcGdops[node])
                        assert(not isnan(w_s) and not isnan(w_d))
                        if w_s > w_d:
                            w_s = 1
                            w_d = 0
                        else:
                            w_s = 0
                            w_d = 1
                        dstSubPos[node] = \
        concatenate((dot(dstSubPos[node][:2], w_d) +
                     dot((t + dot(dot(s, R), srcSubPos[node][:2])), w_s),
                     array(mod([srcSubPos[node][2] - Rtheta], 2 * pi))))
                else:
                    dstSubPos[node] = \
        concatenate((t + dot(dot(s, R), srcSubPos[node][:2]),
                     array(mod([srcSubPos[node][2] - Rtheta], 2 * pi))))

    def get_aoa_gdops(self, pos):
        """
        Return dictionary {node : gdop} calculated from formation pos.
        """
        if len(pos) > 2:
            gdops = {}
            for node in pos.keys():
                gdops[node] = self\
                    .aoa_gdop(node, {k: v for k, v in pos.items()
                                     if k in node.network.neighbors(node) or
                                     k == node})
        else:  # if only two nodes in formation set gdop to large number
            gdops = {k: 1000 for k in pos.keys()}
        return gdops

    def aoa_gdop(self, node, pos, sigma=10):
        """
        Calculate geometric dilution of precision for node in formation pos.
        Node is in formation pos and all other nodes should be neighbors of
        node. If measurement sigmas are all equal gdop doesnt depend on sigma.
        """
        x, y = pos[node][:2]
        fi = []
        d = []

        for n, p in pos.items():
            xi, yi = p[:2]
            if n != node:
                fi.append(arctan2(y - yi, x - xi))
                d.append(sqrt((x - xi) ** 2 + (y - yi) ** 2))

        mi = ni = l = 0
        for fii, di in zip(fi, d):
            mi += (cos(fii) / di / sigma) ** 2
            l += (sin(fii) / di / sigma) ** 2
            ni += sin(fii) * cos(fii) / (di * sigma) ** 2

        sigma1 = sqrt(mi / (mi * l - ni ** 2))
        sigma2 = sqrt(l / (mi * l - ni ** 2))
        # sigma12 = sqrt(ni/(mi*l-ni**2))

        sigmad = sqrt(sum((di * sigma) ** 2 for di in d) / len(d))
        return sqrt((sigma1 ** 2 + sigma2 ** 2)) / sigmad
