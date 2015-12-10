import client
import constants
import cryptomath

import time

class Voter(client.User):

  def __init__(self, name):
    client.Client.__init__(self, name, constants.VOTER_TAG)

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
          self.vote = cryptomath.encode_int(vote)
          return self.vote

  def request_random_vector(self):
    target = "Administrator"
    self.send_return_address(target)
    self.send_message(target, "request_random_vector")
    self.send_message(target, str(2 * (2 ** constants.ENCODED_VOTE_SIZE)))
    (target, response) = self.receive_message()
    return eval(response)

  def commit_vote(self):
    # q is 2 * (2 ** constants.ENCODED_VOTE_SIZE)
    m = constants.ENCODED_VOTE_SIZE
    n = (m / 2) * 3
    random_vector = self.request_random_vector()
    self.logger.debug_log("Random vector from administrator:")
    self.logger.debug_log(str(random_vector))
    error_checked_code = cryptomath.error_checking_encode(self.vote)
    self.logger.debug_log("Error checked code")
    self.logger.debug_log(str(error_checked_code))
    seed = cryptomath.random_bit_vector(n)
    self.logger.debug_log("Seed")
    self.logger.debug_log(str(seed))
    key = cryptomath.get_commit_key(seed, random_vector)
    self.logger.debug_log("Key")
    self.logger.debug_log(str(key))
    commitment = cryptomath.commit_to_bits(error_checked_code, key)
    self.logger.debug_log("Commitment")
    self.logger.debug_log(str(commitment))
    return commitment

def main():
  voter = Voter("Voter")
  voter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  voter.set_ballot(constants.BALLOT)
  voter.get_vote()
  voter.commit_vote()

if __name__ == "__main__":
  main()
