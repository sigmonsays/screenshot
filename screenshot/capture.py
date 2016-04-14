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


class CaptureBuilder:
    def __init__(self, capture_method=None, capture_command=None):
        self.__dict__.update(locals())
        self.log = logging.getLogger(self.__class__.__name__)

    def build(self):
        if self.capture_method != None:
            self.log.info("using user defined capture method %s", self.capture_method)
            capture_method = CaptureMethods.get(self.capture_method)
            if capture_method == None:
                self.warn("user defined capture method not found: %s, proceeding to auto detect", self.capture_method)
            elif capture_method == CustomCapture:
                return capture_method(self.capture_command)

            else:
                return capture_method()

        detect = CaptureDetect()
        methods = detect.detect_capture_methods()
        if len(methods) == 0:
            return None

        first = methods[0]
        self.log.debug("selected capture method %s", first)

        klass = CaptureMethods.get(first)

        return klass()

def MakeCapture(**opts):
    return CaptureBuilder(**opts).build()

class CaptureMethod:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def capture(self, filename):
        raise NotImplemented

class NullCapture(CaptureMethod):
    def capture(self, filename):
        self.log.debug("filename %s", filename)
        return True

class ShellCapture(CaptureMethod):
    cmd = None

    def capture(self, filename):
        self.log.info("%s", filename)
        cmdline = "%s %s" % (self.cmd, filename)
        self.log.debug("cmdline %s", cmdline)
        os.system(cmdline)
        return True

class ImageMagick(ShellCapture):
    cmd = "import"

class Gnome(ShellCapture):
    cmd = "gnome-screenshot -a -f"

class DarwinScreenCapture(ShellCapture):
    cmd = "screencapture -s"

class CustomCapture(ShellCapture):
    def __init__(self, cmd):
        self.log = logging.getLogger(self.__class__.__name__)
        self.cmd = cmd

CaptureMethods = {
    'imagemagick': ImageMagick,
    'null': NullCapture,
    'gnome': Gnome,
    'screencapture': DarwinScreenCapture,
    'custom': CustomCapture,
}
