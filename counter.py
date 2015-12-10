import client
import constants

class Counter(client.Robot):

  def __init__(self, name):
    client.Client.__init__(self, name, constants.COUNTER_TAG)

def main():
  counter = Counter("Counter")
  counter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  counter.serve()

if __name__ == "__main__":
  main()
