import os
import shutil

from screenshot.upload import Upload

class FilesystemUpload(Upload):

    upload_method = 'filesystem'

    def __init__(self, clipboard, save_dir):
        Upload.__init__(self, clipboard)
        self.__dict__.update(locals())

    def upload(self, meta, localfile, shortname):
        basename = os.path.basename(localfile)

        for n in xrange(1000):
            saved_name = os.path.join(self.save_dir, basename)
            if os.path.exists(saved_name) == False:
                break

        dirname = os.path.dirname(saved_name)
        self.log.info("Saving to disk at %s", saved_name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            self.log.info("Creating directory %s", dirname)
        shutil.copyfile(localfile, saved_name)
        return True
