import client
import constants
import cryptomath

class Administrator(client.Robot):

  def __init__(self, name):
    client.Robot.__init__(self, name, constants.ADMINISTRATOR_TAG)
    self.commands["request_random_vector"] = self.get_random_vector

  def get_random_vector(self, n):
    n = int(n)
    assert(n % 2 == 0)
    return cryptomath.random_bit_vector_proportion(n, n/2)

def main():
  administrator = Administrator("Administrator")
  administrator.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  administrator.serve()

if __name__ == "__main__":
  main()
