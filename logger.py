class Logger(object):

  def __init__(self, prefix):
    self.prefix = str(prefix)
    self.debug = False

  def log(self, message):
    print("[" + self.prefix + "] " + str(message))

  def error(self, error):
    self.log("ERROR! " + str(error))

  def debug_log(self, message):
    if self.debug:
      self.log(message)

  def enable_debug_mode(self):
    self.debug = True

  def disable_debug_mode(self):
    self.debug = False
