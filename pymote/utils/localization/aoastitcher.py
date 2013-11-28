from numpy import sqrt, dot, set_printoptions
from numpy.linalg import det
from pymote.utils.localization.stitchsubclusterselectors import \
            MaxCommonNodeSelector, StitchSubclusterSelectorBase
from pymote.utils.localization.basestitcher import BaseStitcher

set_printoptions(precision=4)


class AoAStitcher(BaseStitcher):
    """
    Class implementing subcluster stitching methods based on degrees of
    freedom given by localization using angle of arrival measurements i.e.
    translation, rotation/reflection and scaling.

    Reliable stitch with R, s and t that are not None is based on two or more
    common nodes between them.

    If rotation matrix includes reflection it is not reliable so return Nones.

    """

    def __init__(self, selector=None, **kwargs):
        super(AoAStitcher, self).__init__(**kwargs)
        self.selector = selector or MaxCommonNodeSelector(cn_count_treshold=2)
        assert(isinstance(self.selector, StitchSubclusterSelectorBase))

    def stitch_subclusters_horn(self, dstSubPos, srcSubPos):
        commonNodes = self._get_common_nodes(dstSubPos, srcSubPos)
        assert len(commonNodes) > 1
        (p_s, p_d, w_d) = self._get_centroids(commonNodes, dstSubPos,
                                              srcSubPos)

        s = sqrt(sum([sum((dstSubPos[cn][:2] - p_d) ** 2) * w_d[cn]
                      for cn in commonNodes]) /
                 sum([sum((srcSubPos[cn][:2] - p_s) ** 2) * w_d[cn]
                      for cn in commonNodes]))

        if len(commonNodes) == 2:
            R = self._get_rotation_matrix_2_common_nodes(self, commonNodes,
                                                  dstSubPos, srcSubPos)
        else:
            R = self._get_rotation_matrix_horn(self, commonNodes,
                                               dstSubPos, srcSubPos, p_d, p_s)
        t = p_d - dot(dot(s, R), p_s)

        # if rotation matrix reflects nodes then it is not reliable
        if det(R)<0:
            return (None, None, None)

        return (R, s, t)
