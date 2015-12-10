import client
import constants

import time

class Voter(client.Client):

  def __init__(self, name):
    client.Client.__init__(self, name, constants.VOTER_TAG)

def main():
  voter = Voter("Voter")
  voter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  while True:
    time.sleep(5)
    voter.send_message("Administrator", "hi")
    voter.send_message("Counter", "hi")

if __name__ == "__main__":
  main()
