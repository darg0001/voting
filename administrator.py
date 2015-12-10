import client
import constants

class Administrator(client.Robot):

  def __init__(self, name):
    client.Client.__init__(self, name, constants.ADMINISTRATOR_TAG)

def main():
  administrator = Administrator("Administrator")
  administrator.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  administrator.serve()

if __name__ == "__main__":
  main()
