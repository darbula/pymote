from pymote.logger import logger
from numpy import array, sqrt, dot, outer, concatenate, set_printoptions, \
                  arctan2, sin, cos, nan
from numpy.linalg import eig, det
from numpy.lib.twodim_base import eye
from pymote.utils.localization.stitchsubclusterselectors \
                                        import MaxCommonNodeSelector
set_printoptions(precision=4)


class DistStitcher(object):

    def __init__(self, method='horn', weight='', refine=''):
        self.method = method
        self.weight = weight  # not used
        self.refine = refine  # not used
        if self.method == 'horn':
            self.stitch_method = self.stitch_subclusters_horn
        self.selector_class = MaxCommonNodeSelector

    def stitch(self, dst, src, do_intra=True):
        """
        Stitch src cluster to dst cluster based on selector and its criteria.
        
        1. Stitch all src subclusters to dst.
        2. Append unstitched source subclusters to dst cluster.
        3. If do_intra stitch subclusters internally.
        
        src and dst clusters are in format defined in
        pymote.utils.memory.positions.Positions.subclusters:
        [{node1: array(x1,y1), node2: array(x2,y2), ...}, ...]
        """

        ###### extraStitch ######
        selector = self.selector_class(dst, src, cn_count_treshold=2)
        stitched = self._stitch(dst, src, selector)

        ###### append unstitched ######
        src_stitched = [s[1] for s in stitched]
        for src_sc_index in range(len(src)):
            if src_sc_index not in src_stitched:
                new_subcluster = {}
                for node, pos in src[src_sc_index].items():
                    new_subcluster[node] = pos
                dst.subclusters.append(new_subcluster)

        if do_intra:
            self.intrastitch(dst)

    def intrastitch(self, dst):
        selector = self.selector_class(dst, dst, cn_count_treshold=2)
        self._stitch(dst, dst, selector, is_intra=True)

    def _stitch(self, dst, src, selector, is_intra=False):
        stitched = {}
        while True:
            dstSubIndex, srcSubIndex = selector.select(stitched, is_intra)

            if dstSubIndex is None and srcSubIndex is None:
                break

            # stitch srcSub to dstSub using given method
            R, s, t = self.stitch_method(dst[dstSubIndex], src[srcSubIndex])

            # merge subclusters: append/update src nodes in dst
            # TODO: apply flip ambiguity condition for new subcluster
            for node in src[srcSubIndex].keys():
                if not node in dst[dstSubIndex]:  # append only new
                    dst[dstSubIndex][node] = \
                        concatenate((t + dot(R, src[srcSubIndex][node][:2]),
                                     [nan]))

            stitched[(dstSubIndex, srcSubIndex)] = (R, s, t)

            if is_intra:
                dst.subclusters.pop(srcSubIndex)  # remove stitched subclusters
                stitched = {}  # reset stitched as it is not useful after pop

        return stitched

    def align(self, dst, src):
        """ Align (modify) src w.r.t. dst. """

        for srcSubIndex in range(len(src)):
            R, _s, t = self.stitch_method(dst[0], src[srcSubIndex])
            for node in src[srcSubIndex].keys():
                src[srcSubIndex][node] = \
                    concatenate((t+dot(R, src[srcSubIndex][node][:2]), [nan]))

    def stitch_subclusters_horn(self, dstSubPos, srcSubPos):
        """ Take two subclusters as dictionaries in format {node: position}
            where position is array([x,y,theta]) and return R, s and t. """

        commonNodes = list(set(dstSubPos.keys()) & set(srcSubPos.keys()))

        w_d = {node: 1. / len(commonNodes) for node in commonNodes}

        # calculate centroids of both systems
        p_s = array([0., 0.])
        p_d = array([0., 0.])
        for cn in commonNodes:
            p_s += srcSubPos[cn][:2] * w_d[cn]
            p_d += dstSubPos[cn][:2] * w_d[cn]

        # rotation matrix
        if len(commonNodes) == 1:
            R = eye(2)
        # for 2 commonNodes R is calculated directly
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
            if det(M) < 0:
                assert det(R) < 0  # Umeyama1991 M<0 indicates flip
        # translation vector
        t = p_d - dot(R, p_s)

        logger.debug('R = %s', R.tolist())
        logger.debug('t = %s', t.tolist())

        return (R, 1, t)
