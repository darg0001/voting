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
MESSAGE_SERVER_CAPACITY=4
# The server's socket address
MESSAGE_SERVER_ADDRESS=('localhost', 6610)
# The maximum amount of time the server spends accepting clients
MESSAGE_SERVER_TIMEOUT=60

# Logger tags
MESSAGE_SERVER_TAG="MessageServer"
COUNTER_TAG="Counter"
ADMINISTRATOR_TAG="Administrator"
VOTER_TAG="Voter"
BIT_COMMIT_TAG="BitCommit"
BLIND_SIGNATURE_TAG="BlindSignature"
SIGNATURE_TAG="Signature"

# Ballot used in election
BALLOT="A\nB\nC"

# The number of bits to encode a vote into
# There should be no more than ENCODED_VOTE_SIZE 
# candidates on the ballot
ENCODED_VOTE_SIZE=8

# Blind signature values
BLIND_SIGNATURE_MODULUS=961748941
BLIND_SIGNATURE_PUBLIC_KEY=448140714

# RSA signature values
RSA_P=941083987
RSA_Q=920419823
RSA_E_VOTER=65537
RSA_D_VOTER=238894468994265173
RSA_E_ADMINISTRATOR=13
RSA_D_ADMINISTRATOR=133260362289410845

REGISTRATION_STATE=0
ADMINISTRATION_STATE=1
ADMINISTRATION_COMPLETE_STATE=2
