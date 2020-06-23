import logging
import os

PREFIX    = 'python-appimage-{}'
HOME      = os.path.expanduser('~') 
LOCAL     = os.path.join( HOME, '.local' )
WATCHDIRS = ( os.path.join(HOME, 'Downloads'),
              os.path.join(HOME, '.local', 'bin'),
              os.path.join(HOME, 'Applications'),
              '/Applications',
              '/opt',
              '/usr/local/bin')

APPDIR   = os.path.join(HOME, 'Library', 'Application Support', __name__)
LOGDIR   = os.path.join(APPDIR, 'logs')

def makedirs( path ):
  if not os.path.isdir(path):
    os.makedirs( path, exist_ok=True )

makedirs(LOCAL)
makedirs(APPDIR)
makedirs(LOGDIR)

log      = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler( logging.StreamHandler() )
log.handlers[0].setLevel(logging.ERROR)
