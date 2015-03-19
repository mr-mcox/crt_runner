from boxsdk import OAuth2, Client
import os

class BoxSync(object):

    """Sycronize Box and local files"""

    def __init__(self, config):
        self.config = config
        self.client = self.authenticate_client()

    def store_tokens(self, access_token, refresh_token):
        """
        Store tokens in local file when they are modified
        Assumes that the following are present in the config file
        box_access_token_file
        box_refresh_token_file
        """

        at = open(self.config.box_access_token_file, 'w')
        rt = open(self.config.box_refresh_token_file, 'w')
        at.write(access_token)
        rt.write(refresh_token)
        at.close()
        rt.close()

    def authenticate_client(self):
        """Return client
        Assumes that the following are present in the config file
        box_access_token_file
        box_refresh_token_file
        box_client_id
        box_client_secret
        :return: Box Client
        """
        assert os.path.isfile(self.config.box_access_token_file)
        assert os.path.isfile(self.config.box_refresh_token_file)
        at = open(self.config.box_access_token_file)
        access_token = at.readline()
        rt = open(self.config.box_refresh_token_file)
        refresh_token = rt.readline()

        oauth = OAuth2(
            client_id=self.config.box_client_id,
            client_secret=self.config.box_client_secret,
            access_token=access_token,
            refresh_token=refresh_token,
            store_tokens=self.store_tokens)
        oauth.refresh(oauth.access_token)
        return Client(oauth)
