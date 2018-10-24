from steam.steamid import SteamID
from steam.enums import EResult
from steam.enums.emsg import EMsg
from steam.core.msg import Msg, MsgProto


class Account(object):
    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

    def request_validation_mail(self):
        """Request validation email

        :return: result
        :rtype: :class:`.EResult`
        """
        message = Msg(EMsg.ClientRequestValidationMail, extended=True)

        resp = self.send_job_and_wait(message, timeout=10)

        if resp is None:
            return EResult.Timeout
        else:
            return EResult(resp.eresult)

    def request_password_change_mail(self, password):
        """Request password change mail

        :param password: current account password
        :type  password: :class:`str`
        :return: result
        :rtype: :class:`.EResult`
        """
        message = Msg(EMsg.ClientRequestChangeMail, extended=True)
        message.body.password = password

        resp = self.send_job_and_wait(message, timeout=10)

        if resp is None:
            return EResult.Timeout
        else:
            return EResult(resp.eresult)

    def change_password(self, password, new_password, email_code):
        """Change account's password

        :param password: current account password
        :type  password: :class:`str`
        :param new_password: new account password
        :type  new_password: :class:`str`
        :param email_code: confirmation code from email
        :type  email_code: :class:`str`
        :return: result
        :rtype: :class:`.EResult`

        .. note::
            First request change mail via :meth:`request_password_change_mail()`
            to get the email code
        """
        message = Msg(EMsg.ClientPasswordChange3, extended=True)
        message.body.password = password
        message.body.new_password = new_password
        message.body.code = email_code

        resp = self.send_job_and_wait(message, timeout=10)

        if resp is None:
            return EResult.Timeout
        else:
            return EResult(resp.eresult)

    def change_email(self, password, email, code=''):
        """Change account's email address

        :param password: current account password
        :type  password: :class:`str`
        :param email: new email address
        :type  email: :class:`str`
        :param code: email code
        :type  code: :class:`str`
        :return: result
        :rtype: :class:`.EResult`

        .. note::
            To change email, first call without ``code``
            and then with, to finalize the change
        """
        message = MsgProto(EMsg.ClientEmailChange4)
        message.body.password = password
        message.body.email = email

        if code:
            message.body.code = code

        message.body.final = not not code
        message.body.newmethod = True
        message.body.client_supports_sms = True

        resp = self.send_job_and_wait(message, timeout=10)

        if resp is None:
            return EResult.Timeout
        else:
            return EResult(resp.eresult)
