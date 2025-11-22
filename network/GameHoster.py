from random import randint
import socket
from time import sleep
import threading


class GameHoster:

    def __init__(self, username=f'user{randint(1000, 9999)}'):
        self.username = username
        self.broadcast_sock = None
        self.game_sock = None
        self.game_sock_port = None
        self.establish_sockets()
        self.broadcasting = False

        self.client_sock = None

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def establish_sockets(self):
        """ Establishes UDP and TCP sockets"""
        # UDP broadcasting socket to make host visible on local network
        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, socket.SO_REUSEADDR)

        # TCP socket for in game communication
        self.game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_sock.bind(('0.0.0.0', 0))
        self.game_sock_port = str(self.game_sock.getsockname()[1])

    def _broadcast(self):
        """ UDP broadcast on local network to search for potential pairs
            Should be used in a background thread"""
        # Port 50000 is known to Host and Client for broadcasting purposes
        broadcast_address = ('255.255.255.255', 50000)
        message = f'chess_host:{self.username}:{self.game_sock_port}'
        self.broadcasting = True
        while self.broadcasting:
            try:
                if self.broadcast_sock is None:
                    self.broadcasting = False
                else:
                    self.broadcast_sock.sendto(message.encode('utf-8'), broadcast_address)
                sleep(3)
            except OSError:
                self.broadcasting = False

    def end_broadcast(self):
        """ Turns off self.broadcasting flag to end UPD broadcast """
        self.broadcasting = False

    def establish_connection(self):
        """ Links sockets to allow in game communication"""
        # Start broadcast
        broadcast_thread = threading.Thread(target=self._broadcast)
        broadcast_thread.start()

        # Wait for connection
        try:
            self.game_sock.listen()
            self.client_sock, cli_addr = self.game_sock.accept()
        except OSError:
            self.close_sockets()

        # End broadcast
        self.broadcasting = False
        broadcast_thread.join()

    def receive_data(self):
        """ Receive data from opponent"""
        return self.client_sock.recv(1024)

    def send_data(self, data):
        """ Sends data to opponent"""
        self.client_sock.send(data)

    def close_sockets(self):
        result = [1, 1, 1]
        try:
            if self.broadcast_sock is not None:
                self.broadcast_sock.close()
        except OSError:
            result[0] = 0
        try:
            if self.game_sock is not None:
                self.game_sock.close()
        except OSError as e:
            print(e)
            result[1] = 0
        try:
            if self.client_sock is not None:
                self.client_sock.shutdown(socket.SHUT_RDWR)
                self.client_sock.close()
        except OSError:
            result[2] = 0
        return result

    def __del__(self):
        self.close_sockets()


if __name__ == '__main__':
    server = GameHoster('user123')
    server.establish_connection()
    print(server.receive_data())
    server.close_sockets()