import os 
from screenshot.upload import UploadPlugin

class Shell(UploadPlugin):
    def upload(self, meta, filename, shortname, md):
        tmpl = {
         'filename': filename,
         'shortname': shortname,
        }
        cmd = self.config['template'] % tmpl
        self.log.info("cmd %s", cmd)
        os.system(cmd)
        return True
        
