class Logger(object):

  def __init__(self, prefix):
    self._prefix = str(prefix)

  def log(self, message):
    print("[" + self._prefix + "] " + str(message))

  def error(self, error):
    self.log("ERROR! " + str(error))
