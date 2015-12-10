# Packet header size in characters
HEADER_SIZE=512
# Payload size in characters
PAYLOAD_SIZE=512
# Total packet size in characters
PACKET_SIZE=HEADER_SIZE+PAYLOAD_SIZE
# Pad character for packets
PACKET_PAD='@'

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
