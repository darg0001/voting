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
    # packet.Packet.send_raw("MessageServer", self.get_name(), self.socket)
    self.send_signed_message(str(constants.MESSAGE_SERVER_ADDRESS), self.get_name())
    # The server will respond with a an "ack" if the client
    # was successfully added to the server's network
    self.logger.log("Waiting for server ack...")
    ((return_address, target_address), ack) = self.receive_checked_message_from(str(constants.MESSAGE_SERVER_ADDRESS))
    assert(ack == "ack")
    self.logger.log("Connected to server")

  def send_message(self, return_address, target_address, message):
    self.logger.log("Sending message (" + str(message) + ") to " + target_address)
    packet.Packet.send_raw(return_address, target_address, message, self.socket)

  def send_signed_message(self, target_address, message):
    self.send_message(self.get_name(), target_address, message)

  def receive_message(self):
    return packet.Packet.receive_packet(self.socket)

  def receive_checked_message_from(self, verify_return_address):
    ((return_address, target_address), payload) = self.receive_message()
    assert(return_address == verify_return_address)
    assert(target_address == self.name)
    return((return_address, target_address), payload)

class User(Client):

  def __init__(self, name, prefix):
    Client.__init__(self, name, prefix)

  def send_command(self, target_address, command, args):
    if args == None:
      args = 'void'
    command_and_args = command + constants.PACKET_SPACE + constants.PACKET_SPACE.join(args)
    self.send_signed_message(target_address, command_and_args)

class Robot(Client):

  def __init__(self, name, prefix):
    Client.__init__(self, name, prefix)
    self.commands = {}

  def serve(self):
    while True:
      ((return_address, target_address), command_and_args) = self.receive_message()
      command_and_args = command_and_args.split(constants.PACKET_SPACE)
      command = command_and_args[0]
      self.logger.log("Command received (" + command + ")")
      args = None if command_and_args[1] == 'void' else command_and_args[1:]
      self.logger.log("Args received (" + str(args) + ")")
      response = self.handle_command(command, args)
      self.send_signed_message(return_address, str(response))

  def handle_command(self, command, args):
    if command not in self.commands.keys():
      self.logger.error("Command not recognized")
      return
    return self.commands[command](*args)
