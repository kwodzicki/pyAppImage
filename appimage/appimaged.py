import logging

import os, time
from threading import Thread, Lock

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from appimage import WATCHDIRS, utils

TIMEOUT = 1.0
SLEEP   = 2.0

class AppImaged( FileSystemEventHandler ):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__log = logging.getLogger(__name__)
    self.__log.info('AppImaged watchdog started')
    self.__running = True

    self.queue    = []
    self.Lock     = Lock()
    self.Observer = Observer()
    npaths = 0
    for path in WATCHDIRS:
      if os.path.isdir( path ):
        self.Observer.schedule( self, path, recursive = False )
        npaths += 1
    if npaths == 0:
      raise Exception('No standard paths exist!')
    self.Observer.start()
    self.Thread   = Thread(target = self.__run, daemon = True)
    self.Thread.start()

  def processEvent(self, event):
    if event.is_directory: return
    if event.src_path.endswith('.AppImage'):
      path = event.src_path
      with self.Lock:
        if path not in self.queue:
          self.queue.append( path )
          self.__log.info('AppImage created/modified : {}'.format(path))

  def on_created(self, event):
    self.__log.debug('File created event: {}'.format(event) )
    self.processEvent(event)

  def on_modified(self, event):
    self.__log.debug('File modified event: {}'.format(event) )
    self.processEvent(event)

  def join(self, *args, **kwargs):
    self.__log.debug('Joining watchdog observer')
    self.Observer.join()

  def stop(self, *args, **kwargs):
    self.__running = False
    self.Observer.stop()
    self.Thread.join()
    self.__log.info('AppImaged watchdog stopped')

  def __checkSize(self, path):
    self.__log.debug('Waiting for file to finish being created : {}'.format(path))
    prev = -1
    curr = os.path.getsize(path)
    while (prev != curr) and self.__running:
      time.sleep(SLEEP)
      prev = curr
      curr = os.path.getsize(path)
    return True

  def __run(self):
    while self.__running:
      with self.Lock:
        try:
          appimage = self.queue[0]
        except:
          appimage = None
      if appimage:
        self.__checkSize( appimage )
        status = utils.install( appimage )
        if not status:
          self.__log.error('Failed to install AppImage : {}'.format(appimage) )
        else:
          self.__log.info('Installed AppImage : {}'.format(appimage) )
        with self.Lock:
          self.queue.pop(0)
      else:
        time.sleep( TIMEOUT )
