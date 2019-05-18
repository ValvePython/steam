import unittest
from mock import patch
import gevent
import gevent.queue

from steam.core.cm import CMClient

class CMClient_Scenarios(unittest.TestCase):
    test_channel_key = b'SESSION KEY LOL'

    def setUp(self):
        # mock out crypto
        patcher = patch('steam.core.crypto.generate_session_key')
        self.addCleanup(patcher.stop)
        self.gen_skey = patcher.start()
        self.gen_skey.return_value = (self.test_channel_key, b'PUBKEY ENCRYPTED SESSION KEY')

        patcher = patch('steam.core.crypto.symmetric_encrypt')
        self.addCleanup(patcher.stop)
        self.s_enc = patcher.start()
        self.s_enc.side_effect = lambda m, k: m
        patcher = patch('steam.core.crypto.symmetric_encrypt_HMAC')
        self.addCleanup(patcher.stop)
        self.s_enc_hmac = patcher.start()
        self.s_enc_hmac.side_effect = lambda m, k, mac: m

        patcher = patch('steam.core.crypto.symmetric_decrypt')
        self.addCleanup(patcher.stop)
        self.s_dec = patcher.start()
        self.s_dec.side_effect = lambda c, k: c
        patcher = patch('steam.core.crypto.symmetric_decrypt_HMAC')
        self.addCleanup(patcher.stop)
        self.s_dec_hmac = patcher.start()
        self.s_dec_hmac.side_effect = lambda c, k, mac: c

        # mock out TCPConnection
        patcher = patch('steam.core.cm.TCPConnection', autospec=True)
        self.addCleanup(patcher.stop)
        self.conn = patcher.start().return_value

        self.conn_in = gevent.queue.Queue()
        self.conn.__iter__.return_value = self.conn_in

        # mock out CMServerList
        patcher = patch('steam.core.cm.CMServerList', autospec=True)
        self.addCleanup(patcher.stop)
        self.server_list = patcher.start().return_value
        self.server_list.__iter__.return_value = [(127001, 20000+i) for i in range(10)]
        self.server_list.bootstrap_from_webapi.return_value = False
        self.server_list.bootstrap_from_dns.return_value = False

    @patch.object(CMClient, 'emit')
    @patch.object(CMClient, '_recv_messages')
    def test_connect(self, mock_recv, mock_emit):
        # setup
        self.conn.connect.return_value = True
        self.server_list.__len__.return_value = 10

        # run
        cm = CMClient()

        with gevent.Timeout(2, False):
            cm.connect(retry=1)

        gevent.idle()

        # verify
        self.conn.connect.assert_called_once_with((127001, 20000))
        mock_emit.assert_called_once_with('connected')
        mock_recv.assert_called_once_with()

    @patch.object(CMClient, 'emit')
    @patch.object(CMClient, '_recv_messages')
    def test_connect_auto_discovery_failing(self, mock_recv, mock_emit):
        # setup
        self.conn.connect.return_value = True
        self.server_list.__len__.return_value = 0

        # run
        cm = CMClient()

        with gevent.Timeout(3, False):
            cm.connect(retry=1)

        gevent.idle()

        # verify
        self.server_list.bootstrap_from_webapi.assert_called_once_with()
        self.server_list.bootstrap_from_dns.assert_called_once_with()
        self.conn.connect.assert_not_called()

    @patch.object(CMClient, 'emit')
    @patch.object(CMClient, '_recv_messages')
    def test_connect_auto_discovery_success(self, mock_recv, mock_emit):
        # setup
        self.conn.connect.return_value = True
        self.server_list.__len__.return_value = 0

        def fake_servers(*args, **kwargs):
            self.server_list.__len__.return_value = 10
            return True

        self.server_list.bootstrap_from_webapi.side_effect = fake_servers

        # run
        cm = CMClient()

        with gevent.Timeout(3, False):
            cm.connect(retry=1)

        gevent.idle()

        # verify
        self.server_list.bootstrap_from_webapi.assert_called_once_with()
        self.server_list.bootstrap_from_dns.assert_not_called()
        self.conn.connect.assert_called_once_with((127001, 20000))
        mock_emit.assert_called_once_with('connected')
        mock_recv.assert_called_once_with()

    def test_channel_encrypt_sequence(self):
        # setup
        self.conn.connect.return_value = True

        # run ------------
        cm = CMClient()
        cm.connected = True
        gevent.spawn(cm._recv_messages)

        # recieve ChannelEncryptRequest
        self.conn_in.put(b'\x17\x05\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x01\x00\x00\x00')
        gevent.idle(); gevent.idle(); gevent.idle(); gevent.idle()

        self.conn.put_message.assert_called_once_with(b'\x18\x05\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x80\x00\x00\x00PUBKEY ENCRYPTED SESSION KEY\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00h-\xc4@\x00\x00\x00\x00')

        # recieve ChannelEncryptResult (OK)
        self.conn_in.put(b'\x19\x05\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00')

        cm.wait_event('channel_secured', timeout=2, raises=True)

        
