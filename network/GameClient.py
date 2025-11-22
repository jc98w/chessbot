import socket
import re

# Regular expression for verifying proper format for incoming broadcasts
BROADCAST_PATTERN = re.compile(r"""
    ^(?P<tag>chess_host)
    :
    (?P<username>[0-9a-zA-Z]+)
    :
    (?P<port>\d+)$
    """, re.VERBOSE)

class GameClient:

    def __init__(self):
        self.broadcast_sock = None
        self.game_sock = None
        self.establish_sockets()

        self.server = None
        self.addr_book = {}

    def establish_sockets(self):
        """ Creates new socket for receiving UDP broadcast and TCP connection"""
        # establish socket to receive host broadcast
        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.broadcast_sock.settimeout(5)
        self.broadcast_sock.bind(('', 50000))

        # socket for in game communication
        self.game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_broadcast(self):
        """ Receives UDP broadcasts and updates username and address book"""
        try:
            data, address = self.broadcast_sock.recvfrom(1024)
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

        if username not in self.addr_book:
            # Add newly found user to address book
            self.addr_book[username] = (address[0], int(port))
        return True

    def get_users(self):
        """ Returns users in address book """
        return list(self.addr_book.keys())

    def connect(self, username):
        """ Connects to address associated with the username in the address book"""
        if username not in self.addr_book:
            return False

        try:
            self.game_sock.connect(self.addr_book[username])
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
        self.game_sock.send(data)

    def receive_data(self):
        """ Receives data from opponent through TCP socket"""
        return self.game_sock.recv(1024)

    def close_sockets(self):
        result = [1, 1]
        try:
            if self.broadcast_sock is not None:
                self.broadcast_sock.close()
        except OSError:
            result[0] = 0
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
    client.send_data(b'hello server!')
    client.close_sockets()
