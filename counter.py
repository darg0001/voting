import client
import constants
import crypto

class Counter(client.Robot):

  def __init__(self, name):
    client.Robot.__init__(self, name, constants.COUNTER_TAG)
    self.commands["collect_vote"] = self.collect_vote
    self.verifier = crypto.Signature(constants.RSA_P, constants.RSA_Q, constants.RSA_E_ADMINISTRATOR)
    self.votes = set()
    self.voters = set()

  def collect_vote(self, voter_id, vote, signed_vote):
    if self.verifier.verify(signed_vote) != int(vote):
      self.logger.error("Could not verify administrator's signature on vote")
      return
    self.logger.log("Verified administrator's signature on vote")
    self.votes.add((vote, signed_vote))
    self.voters.add(voter_id)
    if len(self.votes) == constants.VOTER_CAPACITY:
      self.broadcast(len(self.voters), self.voters)
      for (vote, signed_vote) in self.votes:
        self.broadcast(vote + constants.PACKET_SPACE + signed_vote, self.voters)
      return None
    else:
      return "wait"

def main():
  counter = Counter("Counter")
  counter.connect_to_server(constants.MESSAGE_SERVER_ADDRESS)
  counter.serve()

if __name__ == "__main__":
  main()
