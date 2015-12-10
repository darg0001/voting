import constants

class Packet(object):

  def __init__(self, header, payload):
    # The header should contain packet metadata
    # For our purposes, the header will contain the
    # name of the packet's intended recipient
    self.header = header
    self.payload = payload

  @staticmethod
  def receive_packet(socket):
    packet = socket.recv(constants.PACKET_SIZE)
    header = packet[:constants.HEADER_SIZE].strip(constants.PACKET_PAD)
    payload = packet[constants.HEADER_SIZE:].strip(constants.PACKET_PAD)
    return (header, payload)

  @staticmethod
  def send_packet(packet, socket):
    Packet.send_raw(packet.header, packet.payload, socket)

  @staticmethod
  def send_raw(header, payload, socket):
    header = header + constants.PACKET_PAD * (constants.HEADER_SIZE - len(header))
    payload = payload + constants.PACKET_PAD * (constants.PAYLOAD_SIZE - len(payload))
    packet = header + payload
    socket.sendall(packet)
