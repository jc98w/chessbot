import unittest
import threading

from network.GameClient import GameClient
from network.GameHoster import GameHoster

class NetworkTest(unittest.TestCase):
    def test_connection(self):
        server = GameHoster('user123')
        client = GameClient()

        server.establish_sockets('tcp')

        est_con_thread = threading.Thread(target=server.establish_connection)
        est_con_thread.start()

        client.receive_broadcast()
        client.connect('user123')
        est_con_thread.join()

        msg_sent = 'hello server!'
        client.send_data(msg_sent)
        msg_received = server.receive_data()
        self.assertEqual(msg_sent, msg_received)

        msg_sent = 'hello client!'
        server.send_data(msg_sent)
        msg_received = client.receive_data()
        self.assertEqual(msg_sent, msg_received)

        server.close_sockets()
        client.close_sockets()

        server.establish_sockets('tcp')

        est_con_thread = threading.Thread(target=server.establish_connection)
        est_con_thread.start()

        client.receive_broadcast()
        client.connect('user123')
        est_con_thread.join()

        msg_sent = 'hello server!'
        client.send_data(msg_sent)
        msg_received = server.receive_data()
        self.assertEqual(msg_sent, msg_received)

        msg_sent = 'hello client!'
        server.send_data(msg_sent)
        msg_received = client.receive_data()
        self.assertEqual(msg_sent, msg_received)

        server.close_sockets()
        client.close_sockets()


if __name__ == '__main__':
    unittest.main()
