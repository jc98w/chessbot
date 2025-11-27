import socket
import re
import traceback
from time import time

# Regular expression for verifying proper format for incoming broadcasts
BROADCAST_PATTERN = re.compile(r"""
    ^(?P<tag>chess_host)
    :
    (?P<username>[0-9a-zA-Z]+)
    :
    (?P<port>\d+)
    """, re.VERBOSE)

class GameClient:

    def __init__(self):
        self.broadcast_sock = None
        self.game_sock = None

        self.addr_book = {}

    def establish_sockets(self, sock_type='both'):
        """ Creates new socket for receiving UDP broadcast and TCP connection"""
        print(f'Client: Opening {sock_type} sockets')
        # establish socket to receive host broadcast
        if sock_type in ('udp', 'both'):
            self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.broadcast_sock.settimeout(5)
            self.broadcast_sock.bind(('', 50000))

        # socket for in game communication
        if sock_type in ('tcp', 'both'):
            self.game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.game_sock.settimeout(1)

    def receive_broadcast(self):
        """ Receives UDP broadcasts and updates username and address book"""
        try:
            data, address = self.broadcast_sock.recvfrom(1024)
            # print(f'data: {data} from {address}')
        except AttributeError:
            return False
        except TimeoutError:
            return False
        except OSError:
            return False

        decoded_data = data.decode('utf-8')
        match = BROADCAST_PATTERN.match(decoded_data)
        if not match:
            # Ignore invalid broadcasts (should be 'chess host:username:port')
            return False
        username = match.group('username')
        port = match.group('port')

        # Add/update user to address book
        self.addr_book[username] = {'addr': (address[0], int(port)), 'time': time()}

        return True

    def refresh_addr_book(self):
        """ Removes stale usernames from the address book and returns it """
        now = time()
        for username in list(self.addr_book.keys()):
            # User considered stale if broadcast was >5 seconds ago
            if now - self.addr_book[username]['time'] > 5:
                del self.addr_book[username]
        return [host_user for host_user in self.addr_book]

    def get_users(self):
        """ Returns users in address book """
        return list(self.addr_book.keys())

    def connect(self, username):
        """ Connects to address associated with the username in the address book"""
        self.establish_sockets('tcp')
        if username not in self.addr_book:
            return False

        try:
            addr = self.addr_book[username]['addr']
            print(f'Connecting to {self.addr_book[username]}')
            self.game_sock.connect(addr)
        except OSError:
            return False
        try:
            self.broadcast_sock.close()
            self.broadcast_sock = None
        except OSError:
            return False

        return True

    def send_data(self, data):
        """ Sends data to opponent through TCP socket"""
        self.game_sock.send(data.encode('utf-8'))

    def receive_data(self):
        """ Receives data from opponent through TCP socket"""
        msg = self.game_sock.recv(1024).decode('utf-8')
        print(f'Client received {msg}')
        return msg

    def close_sockets(self, sock_type='both'):
        result = [1, 1]
        print(f'Client: Closing {sock_type} sockets')
        if sock_type in ('udp', 'both'):
            try:
                if self.broadcast_sock is not None:
                    self.broadcast_sock.close()
            except OSError:
                result[0] = 0
        if sock_type in ('tcp', 'both'):
            try:
                if self.game_sock is not None:
                    self.game_sock.shutdown(socket.SHUT_RDWR)
                    self.game_sock.close()
            except OSError:
                result[1] = 0
        return result

    def __del__(self):
        self.close_sockets()


if __name__ == '__main__':
    client = GameClient()
    client.receive_broadcast()
    user = input('username?')
    client.connect(user)
    client.send_data('hello server!')
    client.close_sockets()
