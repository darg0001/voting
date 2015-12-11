import client
import constants
import crypto

import time

class Voter(client.User):

  def __init__(self, name):
    client.Client.__init__(self, name, constants.VOTER_TAG)

  def register_id(self):
    self.voter_id = crypto.Signature.hash(self.name)
    target = "Administrator"
    self.send_return_address(target)
    self.send_message(target, "register_id")
    self.send_message(target, self.voter_id)
    (target, response) = self.receive_message()
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

    seed = crypto.CryptoObject.random_bit_vector(n)
    self.logger.debug_log("Seed: " + str(crypto.CryptoObject.bit_vector_to_int(seed)))
    bit_commit = crypto.BitCommit(crypto.CryptoObject.bit_vector_to_int(seed))

    c = bit_commit.error_checking_encode(self.vote)
    self.logger.debug_log("Error checked code: " + str(crypto.CryptoObject.bit_vector_to_int(c)))

    commitment = bit_commit.commit(c, r)
    self.logger.debug_log("Commitment: " + str(crypto.CryptoObject.bit_vector_to_int(commitment)))
    return commitment

  def blind_vote(self, vote):
    blind_signature = crypto.BlindSignature(constants.BLIND_SIGNATURE_MODULUS)
    r = crypto.CryptoObject.bit_vector_to_int(crypto.CryptoObject.random_bit_vector(constants.ENCODED_VOTE_SIZE))
    blind_signature.set_r(r)
    blinded_vote = vote * pow(r, constants.BLIND_SIGNATURE_PUBLIC_KEY, constants.BLIND_SIGNATURE_MODULUS)
    signed_blind_vote = blind_signature.blind_sign(blinded_vote)
    self.logger.debug_log("Blinded vote: " + str(signed_blind_vote))
    return signed_blind_vote

  def sign_vote(self, vote):
    signer = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_VOTER)
    signature = signer.sign(vote)
    self.logger.debug_log("Signed blinded vote: " + str(signature))
    return signature

  def send_vote(self, vote, blinded_commitment):
    target = "Administrator"
    self.send_return_address(target)
    self.send_message(target, "request_signature")
    self.send_message(target, str(self.voter_id) + constants.PACKET_SPACE + str(vote) + constants.PACKET_SPACE + str(blinded_commitment))
    (target, response) = self.receive_message()
    return response

def main():
  voter = Voter("Voter")
  voter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  voter.register_id()
  voter.set_ballot(constants.BALLOT)
  voter.get_vote()
  commitment = crypto.CryptoObject.bit_vector_to_int(voter.commit_vote())
  blinded_commitment = voter.blind_vote(commitment)
  signed_blinded_commitment = voter.sign_vote(blinded_commitment)
  assert(voter.send_vote(signed_blinded_commitment, blinded_commitment))

if __name__ == "__main__":
  main()
