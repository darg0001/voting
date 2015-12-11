import client
import constants
import crypto

class Administrator(client.Robot):

  def register_voter(self, voter):
    response = False
    if voter not in self.registered_voters:
      self.registered_voters.add(voter)
      response = True
    return response

  def check_and_sign_vote(self, voter_id, vote, blinded_commitment):
    if voter_id not in self.registered_voters:
      self.logger.error("Voter ID has not been registered yet")
      return False
    self.logger.debug_log("Voter ID verified")
    if voter_id in self.applied_for_signature:
      self.logger.error("Voter has already requested a signature")
      return False
    return True

  def __init__(self, name):
    client.Robot.__init__(self, name, constants.ADMINISTRATOR_TAG)
    self.registered_voters = set()
    self.applied_for_signature = set()
    self.commands["register_id"] = self.register_voter
    self.commands["request_signature"] = self.check_and_sign_vote

def main():
  administrator = Administrator("Administrator")
  administrator.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  administrator.serve()

if __name__ == "__main__":
  main()
