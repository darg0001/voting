import client
import constants
import crypto

import sys
import time

class Voter(client.User):

  def __init__(self, name):
    client.Client.__init__(self, crypto.Signature.hash(name), constants.VOTER_TAG)
    seed_size = (constants.ENCODED_VOTE_SIZE / 2) * 3
    self.seed = crypto.CryptoObject.random_bit_vector(seed_size)
    self.committer = crypto.BitCommit(crypto.CryptoObject.bit_vector_to_int(self.seed))
    self.blinder = crypto.Blinder(constants.RSA_P, constants.RSA_Q, constants.RSA_E_ADMINISTRATOR)
    self.signer = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_VOTER)
    self.verifier = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_ADMINISTRATOR)

  def register_id(self):
    target = "Administrator"
    self.send_command(target, "register_id", [self.name])
    ((return_address, target_address), response) = self.receive_checked_message_from(target)
    assert(eval(response))

  def get_vote(self, ballot):
    candidates = ballot.split('\n')
    num_candidates = len(candidates)
    while True:
      self.logger.log('Ballot')
      self.logger.log('------')
      for (i, candidate) in enumerate(candidates):
        self.logger.log(str(i + 1) + ': ' + candidate)
      self.logger.log("Enter vote below")
      vote = raw_input("[" + self.prefix + "] ")
      try:
        vote = int(vote)
      except ValueError:
        self.logger.error("Vote must be a number from 1 to " + str(num_candidates))
      else:
        if vote < 1 or vote > num_candidates:
          self.logger.error("Vote must be a number from 1 to " + str(num_candidates))
        else:
          self.logger.debug_log("Voted for candidate " + str(vote))
          self.vote = crypto.CryptoObject.encode_int(vote)
          return self.vote

  def commit_vote(self):
    q = 2 * (2 ** constants.ENCODED_VOTE_SIZE)
    m = constants.ENCODED_VOTE_SIZE
    n = (m / 2) * 3
    r = crypto.CryptoObject.random_bit_vector_proportion(q, q/2)
    c = self.committer.error_checking_encode(self.vote)
    self.commitment = crypto.CryptoObject.bit_vector_to_int(self.committer.commit(c, r)) % (constants.RSA_P * constants.RSA_Q)
    self.logger.debug_log("Commitment: " + str(self.commitment))
    return self.commitment

  def blind(self):
    self.blind_vote = self.blinder.blind(self.commitment)
    self.logger.debug_log("Blinded vote: " + str(self.blind_vote))
    return self.blind_vote

  def sign_vote(self):
    self.signed_blind_vote = self.signer.sign(self.blind_vote)
    self.logger.debug_log("Signed blind vote: " + str(self.signed_blind_vote))
    return self.signed_blind_vote

  def send_vote(self):
    target = "Administrator"
    self.send_command(target, "request_signature", [self.name, str(self.signed_blind_vote), str(self.blind_vote)])
    ((return_address, target_address), response) = self.receive_checked_message_from(target)
    if response == False:
      self.logger.error("Vote was rejected by administrator")
      return
    self.certificate = None
    while response.split(constants.PACKET_SPACE)[0] == "wait":
      self.certificate = response.split(constants.PACKET_SPACE)[1]
      ((return_address, target_address), response) = self.receive_checked_message_from(target)
    self.logger.log("Voter list")
    self.logger.log("ID Commitment Signature")
    for i in range(int(response)):
      ((return_address, target_address), vote_line) = self.receive_checked_message_from(target)
      vote_line = vote_line.split(constants.PACKET_SPACE)
      self.logger.log(vote_line[0] + " " + vote_line[1] + " " + vote_line[2])
    if self.certificate == None:
      ((return_address, target_address), response) = self.receive_checked_message_from(target)
      self.certificate = int(response)
    self.logger.debug_log("Administrator's certificate: " + str(self.certificate))
    return self.certificate

  def check_administrator_certificate(self):
    self.signed_unblinded_vote = self.blinder.retrieve(self.certificate)
    self.logger.debug_log("Signed vote: " + str(self.signed_unblinded_vote))
    unsigned_unblinded_vote = self.verifier.verify(self.signed_unblinded_vote)
    self.logger.debug_log("Unsigned vote: " + str(unsigned_unblinded_vote))
    if unsigned_unblinded_vote != self.commitment:
      self.logger.error("Could not verify administrator's certificate")
      return
    self.logger.log("Verified administrator's certificate")

def main():
  voter_suffix = str(sys.argv[1])
  voter_name = "Voter " + voter_suffix
  print("Joining as: " + voter_name)
  voter = Voter(voter_name)
  voter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  voter.register_id()
  voter.get_vote(constants.BALLOT)
  voter.commit_vote()
  voter.blind()
  voter.sign_vote()
  voter.send_vote()
  voter.check_administrator_certificate()

if __name__ == "__main__":
  main()
