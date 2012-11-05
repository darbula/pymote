__all__ = ['read_npickle', 'write_npickle']

from pymote.logger import logger
import cPickle as pickle
import sys


def _get_fh(path, mode='r'):
    """
     Return a file handle for given path and attempt to uncompress/compress files ending in '.gz'
    """
    
    if path.endswith('.gz'):
        import gzip
        fh = gzip.open(path,mode=mode)
    else:
        fh = open(path,mode = mode)           
    return fh


def write_npickle(net, path):
    """
    Write network object in Python pickle format and save environment image in 
    separate file.
    """
    #TODO use normal pickling by implementing pickling protocol for Network class http://docs.python.org/library/pickle.html#the-pickle-protocol
    #TODO: find out origin of maximum recursion depth problem, hack solution:
    sys.setrecursionlimit(6000)
    fh = _get_fh(str(path),mode='wb')
    pickle.dump(net,fh,pickle.HIGHEST_PROTOCOL)
    fh.close()
    logger.info('net saved %s' % path)
    
def read_npickle(path):
    """
    Read network object in Python pickle format
    """
    fh = _get_fh(str(path),'rb')
    net = pickle.load(fh)
    return net

# scipy.stats.norm (scipy.stats.distributions.norm_gen) object has some bounded (instance) methods that needs to be pickled 
# this is solution for pickling instance methods found at http://stackoverflow.com/a/1816969/1247955
def _pickle_method(method):
    #print 'pickling',
    #print method
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)
    
def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)
        
import copy_reg
import types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)