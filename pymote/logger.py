LOG_CONFIG = {
              'version' : 1,
              'loggers': 
              {
                 'pymote': 
                 {
                    'level' : 'WARN',
                    'handlers' : ['fileHandler','consoleHandler']
                 },
                 'pymote.simulation': 
                 {
                    'level' : 'DEBUG',
                    'handlers' : ['simFileHandler'],
                    'propagate' : 1
                 }
               },
               'handlers':
               {
                    'fileHandler':
                    {
                        'class' : 'logging.FileHandler',
                        'level' : 'DEBUG',
                        'formatter' : 'fileFormatter',
                        'filename' : 'pymote.log'
                    },
                    'consoleHandler':
                    {
                        'class' : 'logging.StreamHandler',
                        'formatter' : 'consoleFormatter',
                        'stream' : 'ext://sys.stdout'
                    },
                    'simFileHandler':
                    {
                        'class' : 'logging.FileHandler',
                        'level' : 'DEBUG',
                        'formatter' : 'fileFormatter',
                        'filename' : 'simulation.log'
                    }
               },
               'formatters':
               {
                    'fileFormatter':
                    {
                        'format' : '%(asctime)s - %(levelname)s: [%(filename)s] %(message)s',
                        'datefmt' : '%Y-%m-%d %H:%M:%S'
                    },
                    'consoleFormatter':
                    {
                        'format' : '%(levelname)-8s [%(filename)s]: %(message)s',
                        'datefmt' : '%Y-%m-%d %H:%M:%S'
                    }
                }
              }
import logging.config
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('pymote')

