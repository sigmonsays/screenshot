import os 
from screenshot.upload import Upload

class ShellUpload(Upload):

    upload_method = 'shell'

    def __init__(self, clipboard, cmd_template):
        Upload.__init__(self, clipboard)
        self.__dict__.update(locals())

    def upload(self, meta, filename, shortname):
        tmpl = {
         'filename': filename,
         'shortname': shortname,
        }
        cmd = self.cmd_template % tmpl
        self.log.debug("cmd %s", cmd)
        os.system(cmd)
        return True
        
