import unittest
import threading

from network.GameClient import GameClient
from network.GameHoster import GameHoster

class NetworkTest(unittest.TestCase):
    def test_connection(self):
        server = GameHoster('user123')
        client = GameClient()

        print('Starting establish_connection thread...')
        est_con_thread = threading.Thread(target=server.establish_connection)
        est_con_thread.start()

        print('Receiving broadcast...')
        client.receive_broadcast()
        print('Attempting connection with user123...')
        if client.connect('user123'):
            print('connected')
        est_con_thread.join()

        msg_sent = 'hello server!'
        client.send_data(msg_sent)
        msg_received = server.receive_data()
        print(f'Asserting {msg_sent} == {msg_received}')
        self.assertEqual(msg_sent, msg_received)

        msg_sent = 'hello client!'
        server.send_data(msg_sent)
        msg_received = client.receive_data()
        self.assertEqual(msg_sent, msg_received)

        print('Shutting down sockets...')
        print(f'Server closed sockets:{server.close_sockets()}')
        print(f'Client closed sockets: {client.close_sockets()}')


if __name__ == '__main__':
    unittest.main()
