# -*- coding: utf-8 -*-
"""Module for importing plugins

Base object for importing plugins and registering them all
"""
import logging

__all__ = ['couchdb', 'filesystem', 'imgur', 'null', 's3', 'tumblr', 'UPLOAD_PLUGINS']

UPLOAD_PLUGINS = []

class UploadPlugin(object):
   """Base object for a upload plugin"""
   class __metaclass__(type):
      def __init__(cls, name, base, attrs):
         if name != "UploadPlugin":
            UPLOAD_PLUGINS.append((name.lower(), cls))

   upload_method = None

   def __init__(self, config, gconfig, clipboard):
      self.log = logging.getLogger(self.__class__.__name__)
      self.config = config
      self.global_config = gconfig
      self.clipboard = clipboard

   def upload(self, meta, localfile, shortname):
      self.log.info("Upload %s shortname %s with meta %s", localfile, shortname, meta)
      raise Exception(NotImplemented)

   def set_url(self, url):
      self.log.debug("%s", url)
      self.url = url

   def get_filename(self):
      pass
      #return None if not self.config.filename_template

   def __str__(self):
      return "<%s>" % (self.__class__.__name__)
