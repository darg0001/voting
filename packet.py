import constants

class Packet(object):

  def __init__(self, return_address, target_address, payload):
    self.header = str(return_address) + constants.PACKET_SPACE + str(target_address)
    self.payload = payload

  @staticmethod
  def receive_packet(socket):
    packet = socket.recv(constants.PACKET_SIZE)
    if packet == None or packet == '':
      return (('', ''), '')
    header = packet[:constants.HEADER_SIZE].strip(constants.PACKET_PAD).split(constants.PACKET_SPACE)
    payload = packet[constants.HEADER_SIZE:].strip(constants.PACKET_PAD)
    return_address = header[0]
    target_address = header[1]
    return ((return_address, target_address), payload)

  @staticmethod
  def send_packet(packet, socket):
    Packet.send_raw(packet.header, packet.payload, socket)

  @staticmethod
  def send_raw(return_address, target_address, payload, socket):
    header = str(return_address) + constants.PACKET_SPACE + str(target_address)
    header += constants.PACKET_PAD * (constants.HEADER_SIZE - len(str(header)))
    payload = str(payload) + constants.PACKET_PAD * (constants.PAYLOAD_SIZE - len(str(payload)))
    packet = str(header) + str(payload)
    socket.sendall(packet)
