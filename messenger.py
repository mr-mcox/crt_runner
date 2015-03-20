from .config import Config
import mandrill


class Messenger(object):

    """Coordinates the sending of messages"""

    def __init__(self, config=None):
        self.mandrill_client = mandrill.Mandrill(config.mandrill_api_key)

    def send_email(self,
                   from_name=None,
                   from_email=None,
                   to_name=None,
                   to_email=None,
                   subject=None,
                   body=None):
        """Stub for sending email

        .. todo:: This function should send an email to a particular address
        """
        self.mandrill_client.messages.send(message={'important': False,
                                                    'tags': ['password-resets'],
                                                    'from_name': from_name,
                                                    'from_email': from_email,
                                                    'to_name': to_name,
                                                    'to_email': to_email,
                                                    'subject': subject,
                                                    'text': body,
                                                    'headers': {'Reply-To': from_email},
                                                    'to': [{'email': to_email,
                                                            'name': to_name,
                                                            'type': 'to'
                                                            }]})
