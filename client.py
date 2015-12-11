import constants
import crypto
import logger
import packet

import socket

class Client(object):

  def __init__(self, name, prefix):
    self.name = str(name)
    self.prefix = prefix
    self.logger = logger.Logger(self.prefix)
    self.logger.enable_debug_mode()
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
    (name, ack) = self.receive_message()
    assert(name == self.get_name())
    assert(ack == "ack")
    self.logger.log("Connected to server")

  def send_message(self, target, message):
    self.logger.log("Sending message (" + str(message) + ") to " + target)
    packet.Packet.send_raw(target, message, self.socket)

  def send_signed_message(self, target, message):
    self.send_return_address(target)
    self.send_message(target, message)

  def send_return_address(self, target):
    self.send_message(target, self.get_name())

  def receive_message(self):
    (target, payload) = packet.Packet.receive_packet(self.socket)
    assert(target == self.get_name())
    return (target, payload)

class User(Client):

  def __init__(self, name, prefix):
    Client.__init__(self, name, prefix)

class Robot(Client):

  def __init__(self, name, prefix):
    Client.__init__(self, name, prefix)
    self.commands = {}

  def serve(self):
    while True:
      (target, return_address) = self.receive_message()
      (target, command) = self.receive_message()
      (target, args) = self.receive_message()
      self.logger.log("Command received (" + command + ")")
      self.logger.log("Args received (" + args + ")")
      args = None if args == 'void' else args.split(constants.PACKET_SPACE)
      response = self.handle_command(command, args)
      self.send_message(return_address, str(response))

  def handle_command(self, command, args):
    if command not in self.commands.keys():
      self.logger.error("Command not recognized")
      return
    return self.commands[command](*args)
