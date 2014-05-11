import os
import logging
import platform


class CaptureDetect:
   def __init__(self, platform_name=None):
      self.log = logging.getLogger(self.__class__.__name__)
      if platform_name == None:
          platform_name = platform.system()
      self.__dict__.update(locals())

   def detect_capture_methods(self):
      if self.platform_name == 'Linux':
         return ['imagemagick', 'gnome']
      elif self.platform_name == 'Darwin':
         return ['screencapture']
      self.log.warn("Unsupported platform %s", self.platform_name)
      return []


class CaptureBuilder():
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def build(self):
        detect = CaptureDetect()
        methods = detect.detect_capture_methods()
        if len(methods) == 0:
            return None

        first = methods[0]
        self.log.debug("selected capture method %s", first)

        klass = CaptureMethods.get(first)

        return klass()

def MakeCapture():
    return CaptureBuilder().build()

class CaptureMethod:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def capture(self, filename):
        raise NotImplemented

class NullCapture(CaptureMethod):
    def capture(self, filename):
        self.log.debug("filename %s", filename)
        return True

class ImageMagick(CaptureMethod):
    def capture(self, filename):
        self.log.info("capture %s", filename)
        os.system("import %s" % (filename))
        return True

class Gnome(CaptureMethod):
    def capture(self, filename):
        self.log.info("capture %s", filename)
        os.system("gnome-screenshot -a -f %s" % (filename))
        return True

class DarwinScreenCapture(CaptureMethod):
    def capture(self, filename):
        self.log.info("capture %s", filename)
        os.system("screencapture -s %s" % (filename))
        return True

CaptureMethods = {
    'imagemagick': ImageMagick,
    'null': NullCapture,
    'gnome': Gnome,
    'screencapture': DarwinScreenCapture,
}
