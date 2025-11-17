import socket

class GameHoster():

    def __init__(self, username):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def broadcast(self):
        address = ('255.255.255.255', 5000)
        message = b'chess host'

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.sendto(message, address)

    def close_sock(self):
        self.sock.close()


if __name__ == '__main__':
    server = GameHoster('jim')
    server.broadcast()
    server.close_sock()
