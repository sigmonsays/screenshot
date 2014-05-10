import os
import logging
import platform

class Clipboard:
    def __init__(self, urls=[]):
        self.log = logging.getLogger(self.__class__.__name__)
        self.__dict__.update(locals())

    def add_url(self, url, weight=0):
        self.urls.append((weight, url))

    def copy(self, url):
        raise Exception(NotImplemented)

    def get_url(self):
        clipboard_url = None
        if len(self.urls) > 0:
           urls = sorted(self.urls, key=lambda x: x[0])
           weight, clipboard_url = urls[0]
           self.log.info("Clipboard URL %s", clipboard_url)
        return clipboard_url

class LinuxClipboard(Clipboard):
    def copy(self, url):
        r = os.popen('xclip -i', 'w')
        r.write(url + "\n")
        r.flush()
        r.close()
        self.log.info("xclip url %s" %(url))

class DarwinClipboard(Clipboard):
    def copy(self, url):
        r = os.popen('pbcopy', 'w')
        r.write(url + "\n")
        r.flush()
        r.close()
        self.log.info("pbcopy url %s" %(url))

class NoClipboard(Clipboard):
    def copy(self, url):
        self.log.debug("clipboard disabled for url %s", url)

def MakeClipboard():
    platform_name = platform.system()
    if platform_name == 'Linux':
        return LinuxClipboard()
    elif platform_name == 'Darwin':
        return DarwinClipboard()
    else:
        return NoClipboard()

    raise Exception("WTF")


