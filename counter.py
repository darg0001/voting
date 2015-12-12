import client
import constants
import crypto

class Counter(client.Robot):

  def __init__(self, name):
    client.Robot.__init__(self, name, constants.COUNTER_TAG)
    self.commands["collect_vote"] = self.collect_vote
    self.commands["open_vote"] = self.open_vote
    self.verifier = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_ADMINISTRATOR)
    self.votes = []
    self.voters = set()
    self.results = [0] * len(constants.BALLOT.split('\n'))
    self.votes_opened = 0

  def get_winners(self):
    candidates = constants.BALLOT.split('\n')
    winners = []
    most_votes = 0
    for count in self.results:
      if count > most_votes:
        most_votes = count
    for i in range(len(self.results)):
      if self.results[i] == most_votes:
        winners.append(candidates[i])
    return winners

  def check_vote(self, vote):
    # In reality, we should decode the error checking value here
    # then check the validity of the vote
    return vote < len(constants.BALLOT.split('\n')) + 1

  def open_vote(self, voter, commit_key):
    commit_key = eval(commit_key)
    vote = int(self.votes[int(voter)][0])
    vote = crypto.BitCommit.check_commit(crypto.BitCommit.error_checking_encode(vote), commit_key)
    vote = crypto.CryptoObject.bit_vector_to_int(vote)
    if self.check_vote(vote) == False:
      self.logger.error("Vote is not valid")
      return None
    self.logger.log("Opened vote: " + str(vote))
    self.results[vote - 1] += 1
    self.votes_opened += 1
    if self.votes_opened == constants.VOTER_CAPACITY:
      self.broadcast("The winner(s): " + ', '.join(self.get_winners()), self.voters)
      return None
    else:
      return "wait"

  def collect_vote(self, voter_id, vote, signed_vote):
    if self.verifier.verify(signed_vote) != int(vote):
      self.logger.error("Could not verify administrator's signature on vote")
      return
    self.logger.log("Verified administrator's signature on vote")
    self.votes.append((vote, signed_vote))
    # technically, this process should be anonymous; we use the id's to
    # publish the list of votes, which could easily be done through
    # another medium
    self.voters.add(voter_id)
    if len(self.votes) == constants.VOTER_CAPACITY:
      self.broadcast(len(self.voters), self.voters)
      for (i, (vote, signed_vote)) in enumerate(self.votes):
        self.broadcast(str(i) + constants.PACKET_SPACE + vote + constants.PACKET_SPACE + signed_vote, self.voters)
      return None
    else:
      return "wait"

def main():
  counter = Counter("Counter")
  counter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  counter.serve()

if __name__ == "__main__":
  main()
