from pymote.logger import logger
from numpy import array, sqrt, dot, outer, set_printoptions, arctan2, sin, cos
from numpy.linalg import eig, det
from numpy.lib.twodim_base import eye
from pymote.utils.localization.basestitcher import BaseStitcher
from pymote.utils.localization.stitchsubclusterselectors import \
            MaxCommonNodeSelector, StitchSubclusterSelectorBase
set_printoptions(precision=4)


class DistStitcher(BaseStitcher):

    def __init__(self, selector=None, **kwargs):
        super(DistStitcher, self).__init__(**kwargs)
        self.selector = selector or MaxCommonNodeSelector(cn_count_treshold=2)
        assert(isinstance(self.selector, StitchSubclusterSelectorBase))

    def stitch_subclusters_horn(self, dstSubPos, srcSubPos):
        """
        Take two subclusters as dictionaries in format {node: position}
        where position is array([x,y,theta]) and return R, s and t.

        """

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
