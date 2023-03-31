import os
import time
import logging
import logging.config
from functools import wraps
from configparser import ConfigParser

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_CONF_PATH = os.path.join(BASEDIR, 'conf/logging.conf')

if not os.path.exists(os.path.join(BASEDIR, 'log')):
    os.makedirs(os.path.join(BASEDIR, 'log'))

config = ConfigParser()
config.read(LOG_CONF_PATH)
for key in config:
    if 'formatter' not in key:
        for k, v in config[key].items():
            if isinstance(v, str):
                config[key][k] = v.format(basedir = BASEDIR)
                
logging.config.fileConfig(config)

logger = logging.getLogger('log')
db_logger = logging.getLogger('database')
print_logger = logging.getLogger('print')

def debugger(t='cls'):
    if t == 'cls':
        def cls_debugger(func):
            @wraps(func)
            def flatten_args(*args, **kwargs):
                return ",".join([str(i) for i in args] + [f"{k}={v}" for k, v in kwargs.items()])
                    
            def wrapper(self, *args, **kwargs):
                logger.debug(f"{type(self).__name__:>12s}::{func.__name__:<12s} ({flatten_args(*args, **kwargs)})", extra={'submitId': self.submitId})
                t = time.time()
                result = func(self, *args, **kwargs)
                logger.debug(f"{type(self).__name__:>12s}::{func.__name__:<12s} |cost:{(time.time()-t):.2f}s| Return: {result}", extra={'submitId': self.submitId})
                return result
            return wrapper
        return cls_debugger
    else:
        def func_debugger(func):
            @wraps(func)
            def flatten_args(*args, **kwargs):
                return ",".join([str(i) for i in args] + [f"{k}={v}" for k, v in kwargs.items()])
                    
            def wrapper(*args, **kwargs):
                logger.debug(f"{'':>12s}::{func.__name__:<12s} ({flatten_args(*args, **kwargs)})")
                t = time.time()
                result = func(*args, **kwargs)
                logger.debug(f"{'':>12s}::{func.__name__:<12s} |cost:{(time.time()-t):.2f}s| Return: {result}")
                return result
            return wrapper
        return func_debugger