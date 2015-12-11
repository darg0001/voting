import client
import constants
import crypto

class Administrator(client.Robot):

  def register_voter(self, voter):
    assert(self.state == constants.REGISTRATION_STATE)
    response = False
    if voter not in self.registered_voters:
      self.registered_voters.add(voter)
      response = True
    if len(self.registered_voters) == constants.MESSAGE_SERVER_CAPACITY - 2:
      self.logger.log("Reached registered voter limit")
      self.state = constants.ADMINISTRATION_STATE
    return response

  def broadcast(self, message):
    self.logger.debug_log("Broadcasting: " + str(message))
    for voter_id in self.registered_voters:
      self.send_message(voter_id, message)

  def finish_administration(self):
    self.state = constants.ADMINISTRATION_COMPLETE_STATE
    self.broadcast(len(self.applied_for_signature.keys()))
    for voter_id in self.applied_for_signature.keys():
      (vote, blinded_commitment) = self.applied_for_signature[voter_id]
      vote_line = str(voter_id) + constants.PACKET_SPACE + str(vote) + constants.PACKET_SPACE + str(blinded_commitment)
      self.broadcast(vote_line)

  def check_and_sign_vote(self, voter_id, vote, blinded_commitment):
    assert(self.state == constants.ADMINISTRATION_STATE)
    if voter_id not in self.registered_voters:
      self.logger.error("Voter ID has not been registered yet")
      return False
    self.logger.debug_log("Voter ID verified")
    if voter_id in self.applied_for_signature:
      self.logger.error("Voter has already requested a signature")
      return False
    self.applied_for_signature[voter_id] = (vote, blinded_commitment)
    if not self.check_vote_signature(vote, blinded_commitment):
      self.logger.error("Vote signature couldn't be verified")
      return False
    signer = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_ADMINISTRATOR)
    certificate = signer.sign(blinded_commitment)
    self.logger.debug_log("Signed blinded vote: " + str(certificate))
    self.num_votes_received += 1
    if self.num_votes_received == len(self.registered_voters):
      self.finish_administration()
      return certificate
    else:
      return "wait"

  def check_vote_signature(self, signature, verifier):
    signer = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_VOTER)
    return signer.verify(signature) == crypto.Signature.hash(verifier)

  def __init__(self, name):
    client.Robot.__init__(self, name, constants.ADMINISTRATOR_TAG)
    self.registered_voters = set()
    self.applied_for_signature = {}
    self.commands["register_id"] = self.register_voter
    self.commands["request_signature"] = self.check_and_sign_vote
    self.num_votes_received = 0
    self.state = constants.REGISTRATION_STATE

def main():
  administrator = Administrator("Administrator")
  administrator.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  administrator.serve()

if __name__ == "__main__":
  main()
