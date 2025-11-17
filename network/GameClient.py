import socket

class GameClient:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.bind(('', 5000))

    def receive_broadcast(self):
        data, address = self.sock.recvfrom(1024)
        print(f'Received {data} from {address}')
        return data

if __name__ == '__main__':
    client = GameClient()
    while True:
        rec_data = client.receive_broadcast()
        if rec_data == b'chess host':
            break
