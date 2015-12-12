import constants
import logger
import packet

import select
import socket
import time

class MessageServer(object):

  def __init__(self, address, capacity=constants.MESSAGE_SERVER_CAPACITY):
    self.logger = logger.Logger(constants.MESSAGE_SERVER_TAG)
    self.logger.enable_debug_mode()
    # Maps client names to sockets
    self.client_sockets = {}
    # Maps client file descriptors to sockets
    self.client_fds = {}
    self.num_clients = 0
    # The address of the socket clients should connect to
    self.address = address
    self.capacity = capacity
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Begin accepting clients until capacity is reached
    # or timeout occurs, whichever comes first
    self.socket.bind(self.address)
    self.logger.log("Listening...")
    self.socket.listen(self.capacity)
    timeout = time.time() + constants.MESSAGE_SERVER_TIMEOUT
    while True:
      if time.time() > timeout:
        self.logger.log("Listen timeout reached")
        break
      elif self.num_clients >= self.capacity:
        self.logger.log("Server capacity reached")
        break
      (client_socket, client_address) = self.socket.accept()
      ((_, target), client_name) = packet.Packet.receive_packet(client_socket)
      assert(target == str(self.get_address()))
      self.add_client(client_name, client_socket)
    # Complete the connection handshake with all clients
    # by sending an "ack"
    self.broadcast("ack")

  def add_client(self, client_name, client_socket):
    if client_name in self.client_sockets.keys():
      self.logger.error("A client with this name already exists on the network")
      return
    if self.num_clients + 1 > self.capacity:
      self._logger.error("The network is full")
      return
    self.num_clients += 1
    self.client_sockets[client_name] = client_socket
    self.client_fds[client_socket.fileno()] = client_socket
    self.logger.log("Added client (" + client_name + ")")

  def serve_forever(self):
    self.logger.log("Serving messages...")
    while True:
      ready_events = select.select(self.client_fds.keys(), [], [])[0]
      for ready_event in ready_events:
        client_socket = self.client_fds[ready_event]
        ((return_address, target_address), message) = packet.Packet.receive_packet(client_socket)
        if return_address == '' or target_address == '' or message == '':
          self.logger.error('Dropping invalid packet. One or more clients may have lost connection...')
          return
        print("sending message: " + return_address + " " + target_address + " " + message)
        self.send_message(return_address, target_address, message)

  def broadcast(self, message):
    for client_name in self.client_sockets.keys():
      self.send_message(str(self.get_address()), client_name, message)

  def send_message(self, return_address, target_address, message):
    self.logger.log("Sending message (" + message + ") to " + target_address)
    if target_address not in self.client_sockets.keys():
      self.logger.error("Could not find target client on network")
      return
    target_socket = self.client_sockets[target_address]
    # Send data to a client, typically this will be a
    # message sent from another client
    packet.Packet.send_raw(return_address, target_address, message, target_socket)

  def get_address(self):
    return self.address

g_server = MessageServer(constants.MESSAGE_SERVER_ADDRESS)

def main():
  g_server.serve_forever()

if __name__ == "__main__":
  main()
