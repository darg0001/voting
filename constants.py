# Packet header size in characters
HEADER_SIZE=4096
# Payload size in characters
PAYLOAD_SIZE=4096
# Total packet size in characters
PACKET_SIZE=HEADER_SIZE+PAYLOAD_SIZE
# Pad character for packets
PACKET_PAD='@'
# Space character for packets to separate pieces of data
PACKET_SPACE='#'

# The maximum number of clients the server can handle
MESSAGE_SERVER_CAPACITY=3
# The server's socket address
MESSAGE_SERVER_ADDRESS=('localhost', 6610)
# The maximum amount of time the server spends accepting clients
MESSAGE_SERVER_TIMEOUT=10

# Logger tags
MESSAGE_SERVER_TAG="MessageServer"
COUNTER_TAG="Counter"
ADMINISTRATOR_TAG="Administrator"
VOTER_TAG="Voter"

# Ballot used in election
BALLOT="A\nB\nC"

# The number of bits to encode a vote into
# There should be no more than ENCODED_VOTE_SIZE 
# candidates on the ballot
ENCODED_VOTE_SIZE=8
