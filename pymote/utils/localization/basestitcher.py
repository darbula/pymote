from numpy import dot, concatenate, arctan2, nan, pi, mod, isnan
from numpy.lib.type_check import real, imag
from pymote.utils.localization.stitchsubclusterselectors import \
            MaxCommonNodeSelector, StitchSubclusterSelectorBase


class BaseStitcher(object):

    def __init__(self, method='horn', selector=None):
        self.method = method
        if self.method=='horn':
            self.stitch_method = self.stitch_subclusters_horn
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

        ###### append unstitched, that is new_subclusters to dst ######
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
        stitched = {}
        while True:
            dstSubIndex, srcSubIndex = self.selector.select(dst, src, stitched,
                                                            is_intra)

            if dstSubIndex is None and srcSubIndex is None:
                break

            # stitch srcSub to dstSub using given method
            R, s, t = self.stitch_method(dst[dstSubIndex], src[srcSubIndex])

            # merge subclusters: append/update src nodes in dst
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
                stitched = {}  # reset stitched as it is not useful after pop

        return stitched

    def align(self, dst, src):
        """ Align (modify) src w.r.t. dst. """

        for srcSubIndex in range(len(src)):
            R, s, t = self.stitch_method(dst[0], src[srcSubIndex])
            for node in src[srcSubIndex].keys():
                src_pos = src[srcSubIndex][node][:2]
                src[srcSubIndex][node] = self.transform(R, s, t, src_pos)

    def transform(self, R, s, t, pos, ori=nan):
        assert not imag(R).any()
        R = real(R)
        if not isnan(ori):
            print "usao"
            # angle of rotation matrix R in ccw
            Rtheta = arctan2(R[1, 0], R[0, 0])
            ori = mod(ori - Rtheta, 2*pi)
        """
        print ori
        print s
        print pos
        print R
        print t + dot(dot(s, R), pos)
        """
        
        return concatenate((t + dot(dot(s, R), pos), [ori]))
