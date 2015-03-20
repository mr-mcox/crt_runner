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


class SyncedFile(object):

    """A file with both a local and Box copy"""

    def __init__(self,
                 name,
                 box_parent_folder,
                 local_parent_folder,
                 parent_modify_dates=None):
        self.name = name
        self.box_parent_folder = box_parent_folder
        self.local_parent_folder = local_parent_folder
        self.parent_modify_dates = parent_modify_dates
        box_modify_date = None
        local_modify_date = None

        # Set box and local modify dates if they exist
        if(parent_modify_dates is not None):
            assert type(parent_modify_dates) is dict()
            if name in parent_modify_dates:
                file_modify_info = parent_modify_dates[name]
                assert 'box_modify_date' in file_modify_info
                assert 'local_modify_date' in file_modify_info
                box_modify_date = file_modify_info['box_modify_date']
                local_modify_date = file_modify_info['local_modify_date']

    @property
    def modify_dates(self):
        return None

    @property
    def box_file(self):
        if not hasattr(self, '_box_file'):
            self._box_file = None
            for item in self.box_parent_folder.get_items(limit=100):
                if item.get()['name'] == self.name:
                    self._box_file = item
                    break
        return self._box_file

    @box_file.setter
    def box_file(self, value):
        self._box_file = value

    def _local_file_exists(self):
        return os.path.isfile(self.local_file_path)

    @property
    def local_file_path(self):
        return os.path.join(self.local_parent_folder, self.name)

    def _box_file_exists(self):
        if self.box_file is not None:
            return True
        else:
            return False

    def _local_file_more_recent(self):
        if (self.box_modify_date is not None
                and self.local_modify_date is not None):
            if self.local_modify_date > self.box_modify_date:
                return True
        return False

    def _box_file_more_recent(self):
        if (self.box_modify_date is not None
                and self.local_modify_date is not None):
            if self.box_modify_date > self.local_modify_date:
                return True
        return False

    def _download_box_file_to_local(self):
        self.box_file.download_to(self.local_file_path)

    def _upload_local_file_to_box_folder(self):
        self.box_parent_folder.upload(self.local_file_path)

    def _replace_box_file_with_local(self):
        self.box_file.update_contents(self.local_file_path)

    def sync_files(self):
        pass
