#!/usr/bin/env python3
import logging

import os, shutil
from configparser import ConfigParser
from subprocess import Popen, STDOUT, DEVNULL

from . import PREFIX, LOCAL 

CONFIG             = ConfigParser()
CONFIG.optionxform = str

PNGEXT      = '.png'
DESKTOP     = '.desktop'

getSquashfs = lambda root: os.path.join( root, 'squashfs-root' )
getUsrDir   = lambda root: os.path.join( root, 'usr' )
getIconDir  = lambda root: os.path.join( root, 'share', 'icons' )

def extract( path ):
  log      = logging.getLogger(__name__)
  path     = os.path.realpath( path )
  dirname  = os.path.dirname( path )
  squashfs = getSquashfs( dirname )

  log.info('Extracting AppImage : {}'.format(path))
  cmd  = [path, '--appimage-extract']
  proc = Popen(cmd, cwd = dirname, stdout = DEVNULL, stderr = STDOUT)
  proc.wait()
  if proc.returncode != 0:
    log.error( 'Error extracting AppImage : {}'.format(path) )
    squashfs = None 

  return path, squashfs

def getLauncherIcon( squashfs ):
  log     = logging.getLogger(__name__)
  log.info('Looking for launcher file and icons')
  desktop = None
  icon    = None
  for item in os.listdir( squashfs ):
    if item.endswith( DESKTOP ) and not desktop:
      desktop = os.path.join( squashfs, item )
    elif item.endswith( PNGEXT ) and not icon:
      icon    = os.path.join( squashfs, item )
      icon    = os.path.realpath( icon )
  
  if desktop:
    CONFIG.read( desktop )
  else:
    log.error( "Missing '{}' file".format(DESKTOP) )

  return desktop, icon 

def copyIcons( squashfs, icon ):
  log     = logging.getLogger(__name__)
  log.debug( 'Copying icons...' )
  usrDir  = getUsrDir(  squashfs )
  iconDir = getIconDir( usrDir   )
  for root, dirs, items in os.walk( iconDir ):
    for item in items:
      if item.endswith( PNGEXT ):
        imgSrc = os.path.join(root, item)
        imgDst = imgSrc.replace( usrDir, LOCAL )
        imgDstDir, imgDstBase = os.path.split( imgDst )
        try:
          os.makedirs( imgDstDir, exist_ok=True)
        except Exception as err:
          log.debug( 'Issue making directory : {}'.format( err ) )
          return False 
        imgDst = os.path.join( imgDstDir, PREFIX.format( imgDstBase ) )
        shutil.copy( imgSrc, imgDst )
        if icon and imgSrc == icon:
          icon = imgDst
  return icon

def install( appimage ):
  log    = logging.getLogger(__name__)
  status = False
  log.info('Attempting to install : {}'.format(appimage))
  path, squashfs = extract( appimage )
  if squashfs is not None:
  
    desktop, icon = getLauncherIcon( squashfs )
    if desktop is not None:
      CONFIG['Desktop Entry']['Exec'] = path
    
      icon = copyIcons( squashfs, icon )
      if icon:
        CONFIG['Desktop Entry']['Icon'] = icon
      
      desktop = PREFIX.format( os.path.basename( desktop ) )
      desktop = os.path.join( LOCAL, 'share', 'applications', desktop )
      with open(desktop, 'w') as fid:
        CONFIG.write( fid )
      status = True

    shutil.rmtree( squashfs )
  return status
