######################################################
####
#### NOT TO BE RAN WITHOUT GENERATING A VCR FIRST
#### use ....
####
######################################################
import vcr
import unittest
import mock
import requests

from steam import webauth as wa

class WACase(unittest.TestCase):
    @mock.patch('steam.webauth.make_requests_session')
    def test_http_error(self, mrs_mock):
        mm = mrs_mock.return_value = mock.MagicMock()

        mm.post.side_effect = requests.exceptions.ConnectTimeout('test')

        with self.assertRaises(wa.HTTPError):
            wa.WebAuth('a', 'b').login()

        mm.post.reset_mock()
        mm.post.side_effect = requests.exceptions.ReadTimeout('test')

        with self.assertRaises(wa.HTTPError):
            wa.WebAuth('c', 'd').login()

    @vcr.use_cassette('vcr/webauth_user_pass_only_success.yaml', mode='none', serializer='yaml')
    def test_login_user_and_pass_only_ok(self):
        user = wa.WebAuth('testuser', 'testpass')
        s = user.login()

        self.assertTrue(user.logged_on)
        self.assertIsInstance(s, requests.Session)

        for domain in s.cookies.list_domains():
            self.assertEqual(s.cookies.get('steamLogin', domain=domain), '0%7C%7C{}'.format('A'*16))
            self.assertEqual(s.cookies.get('steamLoginSecure', domain=domain), '0%7C%7C{}'.format('B'*16))
            self.assertEqual(s.cookies.get('steamMachineAuth0', domain=domain), 'C'*16)

        self.assertEqual(s, user.login())

    @vcr.use_cassette('vcr/webauth_user_pass_only_fail.yaml', mode='none', serializer='yaml')
    def test_login_user_and_pass_only_fail(self):
        with self.assertRaises(wa.LoginIncorrect):
            wa.WebAuth('testuser', 'testpass').login()
            wa.WebAuth('testuser').login('testpass')
