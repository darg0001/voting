import constants
import logger
import packet

import socket

class Client(object):

  def __init__(self, name, prefix):
    self.name = str(name)
    self.prefix = prefix
    self.logger = logger.Logger(self.prefix)
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def get_name(self):
    return self.name

  def connect_to_server(self, address):
    self.logger.log("Connecting to server at " + str(address))
    self.socket.connect(address)
    # Initiate handshake with server by sending client name
    # This name will be used to uniquely identify the client
    packet.Packet.send_raw("MessageServer", self.get_name(), self.socket)
    # The server will respond with a an "ack" if the client
    # was successfully added to the server's network
    self.logger.log("Waiting for server ack...")
    (name, ack) = packet.Packet.receive_packet(self.socket)
    assert(name == self.get_name())
    assert(ack == "ack")
    self.logger.log("Connected to server")

  def send_message(self, target, message):
    self.logger.log("Sending message (" + message + ") to " + target)
    packet.Packet.send_raw(target, message, self.socket)

class User(Client):

  def __init__(self, name, prefix):
    Client.__init__(self, name, prefix)

class Robot(Client):

  def __init__(self, name, prefix):
    Client.__init__(self, name, prefix)

  def serve(self):
    while True:
      (target, message) = packet.Packet.receive_packet(self.socket)
      assert(target == self.get_name())
      self.message = message
      self.logger.log("Message received (" + self.message + ")")
