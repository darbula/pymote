from numpy import dot
from pymote.utils.localization.basestitcher import BaseStitcher
from pymote.utils.localization.stitchsubclusterselectors import \
            MaxCommonNodeSelector, StitchSubclusterSelectorBase


class DistStitcher(BaseStitcher):
    """
    Class implementing subcluster stitching methods based on degrees of
    freedom given by localization using distance measurements i.e.
    translation, rotation/reflection.

    For reliable stitching there should be at least three common nodes.

    """

    def __init__(self, selector=None, **kwargs):
        super(DistStitcher, self).__init__(**kwargs)
        self.selector = selector or MaxCommonNodeSelector(cn_count_treshold=3)
        assert(isinstance(self.selector, StitchSubclusterSelectorBase))

    def stitch_subclusters_horn(self, dstSubPos, srcSubPos):
        commonNodes = self._get_common_nodes(dstSubPos, srcSubPos)
        assert len(commonNodes) > 2
        (p_s, p_d, w_d) = self._get_centroids(commonNodes, dstSubPos,
                                              srcSubPos)
        s = 1
        R = self._get_rotation_matrix_horn(self, commonNodes,
                                           dstSubPos, srcSubPos, p_d, p_s)
        # translation vector
        t = p_d - dot(R, p_s)

        return (R, s, t)
