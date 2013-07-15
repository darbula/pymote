from pymote.logger import logger
from numpy import asarray, array, sqrt, dot, outer, concatenate, \
                  set_printoptions, arctan2, sin, cos, pi, mod, \
                  isnan, trace, zeros, ones, eye, vstack, inf, diag, mean
from pymote.utils.localization.aoastitcher import AoAStitcher
from numpy.linalg import eig, det, inv, pinv
from copy import deepcopy
from pymote.utils.localization.diststitcher import DistStitcher


def align_clusters(dst, src, scale):
    """ Scale, rotate, translate srcLoc w.r.t. dst. """
    assert(isinstance(dst, list))
    if scale:
        stitcher = AoAStitcher()
    else:
        stitcher = DistStitcher()
    stitcher.align(dst, src)


def get_rms(truePos, estimated, align=False, scale=False):
    """ Return root mean square error of estimated positions.

    Set align if estimated positions need to be transformed (rotated and
    translated) before calculating rms error of localization. Set scale=True
    if it needs to be scaled also. """

    if not isinstance(truePos, list):
        truePos = [truePos]
    assert(len(truePos) == 1)

    if align:
        estimated = deepcopy(estimated)
        align_clusters(truePos, estimated, scale)

    suma = 0
    node_count = 0
    for estimated_subcluster in estimated:
        for n in estimated_subcluster:
            suma += (estimated_subcluster[n][0] - truePos[0][n][0]) ** 2 + \
                    (estimated_subcluster[n][1] - truePos[0][n][1]) ** 2
            node_count += 1

    rms = sqrt(suma / node_count)
    return rms


#TODO: only one per row -1 element in G?
def get_crb(net, sensor, compass='off', loc_type='anchor-free', anchors=[]):
    """
    Calculates Cramer-Rao lower bound on covariance matrix of unbiased multihop
    location estimator based on sensor (distance/angle) measurement between
    in-commrange neighbors.

    POS is n by 2 matrix of X and Y coordinates of n nodes
    SIGMA is standard deviation on measurement vector.

    Arguments:
     `compass` -- 'off' (default) or 'on' which means all nodes have compass
     `loc_type` -- 'anchor-free' (default) or 'anchored'
     `anchors` -- list of anchor nodes, used only when loc_type is 'anchored'
    """

    if loc_type == 'anchored' and not anchors:
        raise(Exception('Anchors not defined.'))
    if loc_type == 'anchor-free' and anchors:
        logger.warning('Anchors are ignored')
        anchors = []

    nodes = [node for node in net.nodes() if node not in anchors]

    if sensor.name() == 'AoASensor' and compass == 'off':
        u = 3  # x,y,theta
    else:  # DistSensor or AoASensor with compass on
        u = 2  # x,y

    # number of mesurments, number of unknowns times number of not anchor nodes
    G = zeros((2 * len(net.edges()), u * len(nodes)))
    m = 0
    for r, node in enumerate(nodes):
        (x_r, y_r) = net.pos[node]
        for neighbor in net.neighbors(node):
            t = nodes.index(neighbor)
            (x_t, y_t) = net.pos[neighbor]
            d = sqrt((x_r - x_t) ** 2 + (y_r - y_t) ** 2)
            if sensor.name() == 'DistSensor':
                G[m, r*u] = (x_r-x_t)/d
                G[m, r*u+1] = (y_r-y_t)/d
                G[m, t*u] = (x_t-x_r)/d
                G[m, t*u+1] = (y_t-y_r)/d
            elif sensor.name() == 'AoASensor':
                G[m, r*u] = (y_t-y_r)/d**2
                G[m, r*u+1] = (x_r-x_t)/d**2
                G[m, t*u] = (y_r-y_t)/d**2
                G[m, t*u+1] = (x_t-x_r)/d**2
                if u == 3:
                    G[m, t * u + 2] = -1.
            m += 1  # next row

    for s in nodes[0].compositeSensor.sensors:
        if s.name() == sensor.name():
            sigma = s.probabilityFunction.scale
            break
    else:
        raise(Exception('Sensor not found in nodes'))

    J = 1 / sigma ** 2 * (dot(G.T, G))

    #print matrix_rank(J)

    if loc_type == 'anchor-free':
        cov = pinv(J)
    elif loc_type=='anchored':
        cov = inv(J)

    di = diag(cov)
    # extract only position from cov
    di = concatenate((di[::3], di[1::3]))

    return sqrt(2*mean(di))


def show_subclusters(net, subclusters):
    """ Show colored subclusters. """
    colors = [node in subclusters[0] and 'g' or 'r' for node in net.nodes()]
    net.show(nodeColor=colors)


def show_localized(net, estimated, scale=False, align=True,\
                   display_loc_err=True, show_labels=True):
    """
    Display estimated positions.

    estimated should be a list of dictionaries.

    """
    from matplotlib.pylab import gca
    from matplotlib.collections import LineCollection

    # copy estimated so that passed estimated remains unchanged
    estimated = deepcopy(estimated)
    if align:
        # rotate, translate and if needed scale estimated w.r.t. true positions
        align_clusters([net.pos], estimated, scale)

    #TODO: implement display of all subclusters
    if len(estimated)>1:
        raise(NotImplementedError)
    else:
        estimated_sc = estimated[0]

        net.show(positions=estimated_sc, show_labels=show_labels)
        if display_loc_err:
            #TODO: not working in ipython notepad
            ax = gca()
            ax.set_title('Localized positions')
            ax.set_title('Localization error display')
            edge_pos = asarray([(net.pos[n], estimated_sc[n])
                                for n in estimated_sc.keys()])
            errorCollection = LineCollection(edge_pos, colors='r',
                                             transOffset=ax.transData)
            errorCollection.set_zorder(1)  # errors go behind nodes
            ax.add_collection(errorCollection)
            ax.figure.canvas.draw()
