"""Plugin for storing screen shots on a local filesystem"""
import os
import shutil

from screenshot.upload import UploadPlugin

class Disk(UploadPlugin):

   upload_method = 'filesystem'

   def upload(self, meta, localfile, shortname, md):
      basename = os.path.basename(localfile)
      bname, ext = os.path.splitext(basename)

      for i in xrange(100):

         if i == 0:
            saved_name = localfile
         else:
            saved_name = os.path.join(
               os.path.expanduser(self.config['save_dir']),
               bname + "-" + str(i) + ext
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
