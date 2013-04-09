"""Default pymote settings.

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
ENVIRONMENT2D_SHAPE = (600,600)


ALGORITHMS = ()
#ALGORITHMS = ((ReadSensors,
#               {'sensorReadingsKey':'sensorReadings'}),
#              )

CHANNEL_TYPE = 'Udg'




##########
#  NODE  #
##########
SENSORS = ('NeighborsSensor')
#SENSORS = ('AoASensor','DistSensor')
ACTUATORS = ()
COMM_RANGE = 100

AOA_PF_PARAMS = {'pf': scipy.stats.norm,
                 'scale':10*pi/180} # in radians
DIST_PF_PARAMS = {'pf': scipy.stats.norm,
                 'scale':10}
