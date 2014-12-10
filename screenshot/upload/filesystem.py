"""Plugin for storing screen shots on a local filesystem"""
import os
import shutil

from screenshot.upload import UploadPlugin

class Disk(UploadPlugin):

   upload_method = 'filesystem'

   def upload(self, meta, localfile, shortname):
      basename = os.path.basename(localfile)

      for i in xrange(1000):
         saved_name = os.path.join(
            os.path.expanduser(self.config.disk_config['save_dir']),
            basename + i
         )
         if os.path.exists(saved_name) == False:
            break

      dirname = os.path.dirname(saved_name)
      self.log.info("Saving to disk at %s", saved_name)
      if not os.path.exists(dirname):
         os.makedirs(dirname)
      self.log.info("Creating directory %s", dirname)
      shutil.copyfile(localfile, saved_name)
      return True
