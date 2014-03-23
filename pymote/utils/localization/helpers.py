from pymote.logger import logger
from numpy import asarray, sqrt, dot, concatenate, diag, mean, zeros, min, \
max, arctan2, sin, cos
from pymote.utils.localization.aoastitcher import AoAStitcher
from numpy.linalg import inv, pinv
from copy import deepcopy
from pymote.utils.localization.diststitcher import DistStitcher
from pymote.utils.memory.positions import Positions
from xml.dom import NotSupportedErr


def align_clusters(dst, src, scale):
    """ Scale, rotate, translate srcLoc w.r.t. dst. """
    assert(isinstance(src, Positions))
    assert(isinstance(dst, Positions))
    if scale:
        stitcher = AoAStitcher(reflectable=True)
    else:
        stitcher = DistStitcher()
    stitcher.align(dst, src)


def get_rms(truePos, estimated, align=False, scale=False):
    """
    Returns root mean square error of estimated positions.

    Set align if estimated positions need to be transformed (rotated and
    translated) before calculating rms error of localization. Set scale=True
    if they needs to be scaled also.

    """
    truePos = Positions.create(truePos)
    assert(len(truePos) == 1)
    estimated = Positions.create(estimated)

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

    References:
        Savvides2003 - Savvides et al,
                        On the Error Characteristics of Multihop Node
                        Localization in Ad-Hoc Sensor Networks, 2003
        Patwari2005 - Patwari et al,
                        Locating the nodes: cooperative localization in
                        wireless sensor networks
        Chang2006 - Chen Chang et al,
                        Cramer-Rao-Type Bounds for Localization, 2006
    """

    if loc_type == 'anchored' and not anchors:
        raise Exception('Anchors not defined.')
    if loc_type == 'anchor-free' and anchors:
        logger.warning('Anchors are ignored')
        anchors = []

    nodes = [node for node in net.nodes() if node not in anchors]

    if sensor.name()=='AoASensor' and compass=='off':
        u = 3  # x, y, theta
    else:  # DistSensor or AoASensor with compass on
        u = 2  # x, y

    # number of measurements x number of unknowns
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
            m += 1  # next measurement

    for s in nodes[0].compositeSensor.sensors:
        if s.name() == sensor.name():
            sigma = s.probabilityFunction.scale
            break
    else:
        raise Exception('Sensor not found in nodes')

    J = (dot(G.T, G)) / sigma ** 2

    #print matrix_rank(J)

    if loc_type == 'anchor-free':
        cov = pinv(J)
    elif loc_type=='anchored':
        cov = inv(J)

    # Chang2006 (28)
    di = diag(cov)
    # extract only position from cov
    di = concatenate((di[::3], di[1::3]))

    return sqrt(2*mean(di))


def get_aoa_gdop_node(net, estimated, node):
    """
    Calculate geometric dilution of precision for node in estimated formation.
    Node is in the formation and all other nodes should be neighbors of
    node.
    """
    if 'AoASensor' not in [sensor.name() for sensor in node.sensors]:
        raise NotSupportedErr('Only angle of arrival based gdop is supported')
    sensor = node.compositeSensor.get_sensor('AoASensor')
    sigma = sensor.probabilityFunction.scale
    neighbors = net.neighbors(node)
    for n in neighbors:
        sensor = n.compositeSensor.get_sensor('AoASensor')
        if sensor.probabilityFunction.scale!=sigma:
            raise NotSupportedErr('All nodes AoA sensors should have '
                                  'same scale')
    # Note from Torrieri, Statistical Theory of Passive Location Systems
    # if measurement sigmas are all equal gdop doesn't depend on sigma.
    x, y = estimated[node][:2]
    fi = []
    d = []

    for n in neighbors:
        xi, yi = estimated[n][:2]
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


def get_aoa_gdop(net, estimated):
    return sum([get_aoa_gdop_node(net, estimated, node) for node in estimated])


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

    truePos = Positions.create(net.pos)
    estimated = Positions.create(estimated)
    # copy estimated so that passed estimated remains unchanged
    estimated = deepcopy(estimated)
    if align:
        # rotate, translate and if needed scale estimated w.r.t. true positions
        align_clusters(truePos, estimated, scale)

    #TODO: implement display of all subclusters
    if len(estimated)>1:
        raise(NotImplementedError)
    else:
        estimated_sc = estimated[0]

        #net.show(positions=estimated_sc, show_labels=show_labels)
        fig = net.get_fig(positions=estimated_sc, show_labels=show_labels)
        ax = fig.gca()
        minpos = min(estimated_sc.values(), axis=0)
        maxpos = max(estimated_sc.values(), axis=0)
        minpos -= (maxpos-minpos)*0.1
        maxpos += (maxpos-minpos)*0.1

        ax.set_xlim(minpos[0], maxpos[0])
        ax.set_ylim(minpos[1], maxpos[1])
        #fig.show()
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
