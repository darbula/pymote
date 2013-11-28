from numpy import dot, concatenate, arctan2, nan, pi, mod, isnan, eye
from numpy.lib.type_check import real, imag
from pymote.utils.localization.stitchsubclusterselectors import \
            MaxCommonNodeSelector, StitchSubclusterSelectorBase
from pymote.logger import logger
from numpy import array, sqrt, outer, sin, cos
from numpy.linalg import eig, det


class BaseStitcher(object):
    """
    Base class for stitching two clusters.

    Subclasses should implement own methods for subcluster stitching named:
        stitch_subclusters_<name>
    These methods should take two subclusters as dictionary {node: position}
    where position is array([x,y,theta]) with at least one common node and
    return rotation matrix R, scaling factor s and translation vector t.

    If stitch_subclusters method can't be sure that all parameters are correct
    i.e. when common nodes are not in generic formation then it should return
    None for all parameters.

    """

    def __init__(self, method='horn', selector=None):
        """ Default method is horn for backward compatibility. """
        try:
            self.stitch_method = self.__getattribute__("stitch_subclusters_" +
                                                       method)
        except AttributeError:
            raise NotImplementedError("Stitch method %s not implemented" %
                                      method)
        self.selector = selector or MaxCommonNodeSelector()
        assert(isinstance(self.selector, StitchSubclusterSelectorBase))

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

        ###### externalStitch ######
        stitched = self._stitch(dst, src)

        # First remove incomplete stitches from stitched
        for k, v in stitched.items():
            if None in v:
                stitched.pop(k)
        # Then using stitched dictionary keys find out which subclusters are
        # not stitched and append them to dst.subclusters
        src_stitched = [s[1] for s in stitched.keys()]
        for src_sc_index in range(len(src)):
            if src_sc_index not in src_stitched:
                new_subcluster = {}
                for node, pos in src[src_sc_index].items():
                    new_subcluster[node] = pos
                dst.subclusters.append(new_subcluster)

        if do_intra:
            self.intrastitch(dst)

    def intrastitch(self, dst):
        self._stitch(dst, dst, is_intra=True)

    def _stitch(self, dst, src, is_intra=False):
        """
        Iteratively:
            * selects subclusters to stitch using self.selector
            * stitch - find out R, s and t
            * append transformed node positions from src to dst subcluster
        Return stitched dictionary where:
            keys - are pairs of indexes of all stitched subclusters
            values - are their R, s and t transformation parameters
                     or all of them are None if can't be calculated reliably
                     or () if src subcluster is subset of dst

        """
        stitched = {}
        while True:
            dstSubIndex, srcSubIndex = self.selector.select(dst, src, stitched,
                                                            is_intra)

            if dstSubIndex is None and srcSubIndex is None:
                break

            # stitch srcSub to dstSub using given method
            R, s, t = self.stitch_method(dst[dstSubIndex], src[srcSubIndex])

            if None in (R, s, t):  # skip unreliable stitches
                stitched[(dstSubIndex, srcSubIndex)] = (R, s, t)
                continue

            # merge subclusters: append src nodes in dst
            # TODO: apply flip ambiguity condition for new subcluster
            for node in src[srcSubIndex].keys():
                if not node in dst[dstSubIndex]:  # append only new
                    pos = src[srcSubIndex][node][:2]
                    try:
                        ori = src[srcSubIndex][node][2]
                    except IndexError:
                        ori = nan
                    dst[dstSubIndex][node] = self.transform(R, s, t, pos, ori)

            stitched[(dstSubIndex, srcSubIndex)] = (R, s, t)

            if is_intra:
                dst.subclusters.pop(srcSubIndex)  # remove stitched subclusters
                stitched = {}  # reset stitched since pop has changed indexes

        return stitched

    def align(self, dst, src):
        """ Align (modify) src w.r.t. dst. """

        for srcSubIndex in range(len(src)):
            R, s, t = self.stitch_method(dst[0], src[srcSubIndex])
            for node in src[srcSubIndex].keys():
                src_pos = src[srcSubIndex][node][:2]
                src[srcSubIndex][node] = self.transform(R, s, t, src_pos)

    def transform(self, R, s, t, pos, ori=nan):
        """ Transform node position based on params that are not None. """
        # assumption is that t is never None
        assert t is not None
        R = eye(2) if R is None else R
        s = 1 if s is None else s
        assert not imag(R).any()
        R = real(R)
        if not isnan(ori):
            # angle of rotation matrix R in ccw
            Rtheta = arctan2(R[1, 0], R[0, 0])
            ori = mod(ori - Rtheta, 2*pi)
        return concatenate((t + dot(dot(s, R), pos), [ori]))

    # ------------------ generic helper methods -------------------------------

    def _get_common_nodes(self, dstSubPos, srcSubPos):
        return list(set(dstSubPos.keys()) & set(srcSubPos.keys()))

    def _get_centroids(self, commonNodes, w_d, dstSubPos, srcSubPos, w_d=None):
        if w_d is None:
            w_d = {node: 1. / len(commonNodes) for node in commonNodes}
        p_s = array([0., 0.])
        p_d = array([0., 0.])
        for cn in commonNodes:
            p_s += srcSubPos[cn][:2] * w_d[cn]
            p_d += dstSubPos[cn][:2] * w_d[cn]
        return (p_s, p_d, w_d)

    def _get_rotation_matrix_2_nodes(self, commonNodes, dstSubPos, srcSubPos):
        """
        Calculates rotation matrix based only on two common nodes

        Warning: should be used cautiously when local systems could be
        reflected i.e. when they are formed by distance measurements.

        """
        vector1 = dstSubPos[commonNodes[0]] - dstSubPos[commonNodes[1]]
        vector2 = srcSubPos[commonNodes[0]] - srcSubPos[commonNodes[1]]
        theta1 = arctan2(vector1[1], vector1[0])
        theta2 = arctan2(vector2[1], vector2[0])
        theta = theta1 - theta2
        # in ccw direction
        R = array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        return R

    def _get_rotation_matrix_horn(self, commonNodes, dstSubPos, srcSubPos,
                                  p_d, p_s):
        """ Horn method for calculating rotation matrix. """
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
            commonNodes[0].log('M<0')
        return R
