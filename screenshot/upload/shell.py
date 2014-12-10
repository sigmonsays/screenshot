import os 
from screenshot.upload import UploadPlugin

class Shell(UploadPlugin):
    def upload(self, meta, filename, shortname):
        tmpl = {
         'filename': filename,
         'shortname': shortname,
        }
        cmd = self.cfg['cmd_template'] % tmpl
        self.log.info("cmd %s", cmd)
        os.system(cmd)
        return True
        
