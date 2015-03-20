import mandrill

from .config import Config

class Messenger(object):

    """Coordinates the sending of messages"""

    def __init__(self,config=None):
    	pass    
	
    def send_email(self, message):
        """Stub for sending email
        
        .. todo:: This function should send an email to a particular address
        """
        mandrill_client = mandrill.Mandrill('ejBA1qPIlAU6c6UA-0mdwg')
        result = mandrill_client.messages.send(message=message)