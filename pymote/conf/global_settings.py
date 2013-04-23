"""Default Pymote settings.

Override these with settings in the module pointed-to by the
PYMOTE_SETTINGS_MODULE environment variable or by using
settings.configure(**settings) or settings.load('path.to.settings')

"""

import scipy.stats
from numpy import pi

###########
# NETWORK #
###########
ENVIRONMENT = 'Environment2D'
ENVIRONMENT2D_SHAPE=(600, 600)
N_COUNT = 100

ALGORITHMS = ()
CHANNEL_TYPE = 'Udg'

##########
#  NODE  #
##########
SENSORS = ('NeighborsSensor',)
ACTUATORS = ()
COMM_RANGE = 100

AOA_PF_PARAMS = {'pf': scipy.stats.norm,
                 'scale': 10*pi/180}  # in radians
DIST_PF_PARAMS = {'pf': scipy.stats.norm,
                  'scale': 10}
