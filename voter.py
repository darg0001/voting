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
    self.bit_commit = crypto.BitCommit(crypto.CryptoObject.bit_vector_to_int(self.seed))
    self.blind_signature = crypto.BlindSignature(constants.BLIND_SIGNATURE_MODULUS)
    self.signer = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_VOTER)

  def register_id(self):
    target = "Administrator"
    self.send_command(target, "register_id", [self.name])
    ((return_address, target_address), response) = self.receive_checked_message_from(target)
    assert(eval(response))

  def set_ballot(self, ballot):
    self.ballot = ballot

  def get_vote(self):
    candidates = self.ballot.split('\n')
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
    self.logger.debug_log("R vector: " + crypto.CryptoObject.bit_vector_to_string(r))

    self.logger.debug_log("Seed: " + str(crypto.CryptoObject.bit_vector_to_int(self.seed)))

    c = self.bit_commit.error_checking_encode(self.vote)
    self.logger.debug_log("Error checked code: " + str(crypto.CryptoObject.bit_vector_to_int(c)))

    commitment = self.bit_commit.commit(c, r)
    self.logger.debug_log("Commitment: " + str(crypto.CryptoObject.bit_vector_to_int(commitment)))
    return commitment

  def blind_vote(self, vote):
    r = crypto.CryptoObject.bit_vector_to_int(crypto.CryptoObject.random_bit_vector(constants.ENCODED_VOTE_SIZE))
    self.blind_signature.set_r(r)
    blinded_vote = vote * pow(r, constants.BLIND_SIGNATURE_PUBLIC_KEY, constants.BLIND_SIGNATURE_MODULUS)
    signed_blind_vote = self.blind_signature.blind_sign(blinded_vote)
    self.logger.debug_log("Blinded vote: " + str(signed_blind_vote))
    return signed_blind_vote

  def sign_vote(self, vote):
    signature = self.signer.sign(vote)
    self.logger.debug_log("Signed blinded vote: " + str(signature))
    return signature

  def send_vote(self, vote, blinded_commitment):
    target = "Administrator"
    self.send_command(target, "request_signature", [self.name, str(vote), str(blinded_commitment)])
    ((return_address, target_address), response) = self.receive_checked_message_from(target)
    if response == False:
      self.logger.error("Vote was rejected by administrator")
      return
    certificate = None
    while response.split(constants.PACKET_SPACE)[0] == "wait":
      certificate = response.split(constants.PACKET_SPACE)[1]
      ((return_address, target_address), response) = self.receive_checked_message_from(target)
    self.logger.log("Voter list")
    self.logger.log("ID Commitment Signature")
    for i in range(int(response)):
      ((return_address, target_address), vote_line) = self.receive_checked_message_from(target)
      vote_line = vote_line.split(constants.PACKET_SPACE)
      self.logger.log(vote_line[0] + " " + vote_line[1] + " " + vote_line[2])
    if certificate == None:
      ((return_address, target_address), certificate) = self.receive_checked_message_from(target)
    return certificate

  def check_administrator_certificate(self, certificate):
    pass

def main():
  voter_suffix = str(sys.argv[1])
  voter_name = "Voter " + voter_suffix
  print("Joining as: " + voter_name)
  voter = Voter(voter_name)
  voter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  voter.register_id()
  voter.set_ballot(constants.BALLOT)
  voter.get_vote()
  commitment = crypto.CryptoObject.bit_vector_to_int(voter.commit_vote())
  blinded_commitment = voter.blind_vote(commitment)
  signed_blinded_commitment = voter.sign_vote(blinded_commitment)
  certificate = voter.send_vote(signed_blinded_commitment, blinded_commitment)
  voter.check_administrator_certificate(certificate)

if __name__ == "__main__":
  main()
