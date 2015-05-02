from boxsdk import OAuth2, Client
import boxsdk
import os
import yaml
import dateutil.parser
import logging
import sys
from datetime import datetime


class BoxSync(object):

    """Sycronize Box and local files"""

    def __init__(self, config):
        self.config = config

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

    @property
    def box_client(self):
        if not hasattr(self, '_box_client'):
            self._box_client = self.authenticate_client()
        return self._box_client

    @property
    def modify_dates(self):
        if not hasattr(self, '_modify_dates'):
            self._modify_dates = dict()
        return self._modify_dates

    @property
    def root_box_folder(self):
        if not hasattr(self, '_root_box_folder'):
            root_folder = self.box_client.folder(folder_id='0')
            expected_name = self.config.root_box_folder_name
            for folder in root_folder.get_items(limit=100):
                folder_name = folder.get()['name']
                if folder_name == expected_name:
                    self._root_box_folder = folder
                    break
            else:
                assert False, 'Root box folder "' + \
                    expected_name + '" not found'
        return self._root_box_folder

    @property
    def institute_folders(self):
        if not hasattr(self, '_institute_folders'):
            institute_folders = list()
            self._institute_folder_by_name = dict()
            for institute in self.config.institute_list:
                # Pass box folder if it exists
                institute_box_folder_id = self.config.info_by_institute(
                    institute, 'box_folder_id')
                box_folder = None
                if institute_box_folder_id is not None:
                    box_folder = self.box_client.folder(
                        folder_id=str(institute_box_folder_id))

                sf = SyncedFolder(name=institute,
                                  box_parent_folder=self.root_box_folder,
                                  local_parent_folder=self.config.root_local_folder,
                                  parent_modify_dates=self.modify_dates,
                                  box_folder=box_folder)
                institute_folders.append(sf)
                self._institute_folder_by_name[institute] = sf

                self.config.set_box_folder_id(institute, sf.box_folder_id)

            self._institute_folders = institute_folders
        return self._institute_folders

    def institute_folder_by_name(self, institute):
        assert institute in self._institute_folder_by_name
        return self._institute_folder_by_name[institute]

    def sync_institute_folders(self, institute=None):
        """Sync folder or folders

        :param str institute: (Optional) Institute name
        """
        if institute is None:
            for inst_folder in self.institute_folders:
                inst_folder.sync_folder()
        else:
            self.institute_folder_by_name(institute).sync_folder()
        self.refresh_modify_dates()

        # Save sync records
        sync_file = open(self.config.box_sync_modify_dates, 'w')
        yaml.dump(self.modify_dates, sync_file)
        sync_file.close()

    def refresh_modify_dates(self):
        for inst_folder in self.institute_folders:
            self._modify_dates[inst_folder.name] = inst_folder.modify_dates


class SyncedFolder(object):

    """A folder with both a local and Box copy"""

    def __init__(self,
                 name,
                 box_parent_folder,
                 local_parent_folder,
                 parent_modify_dates=dict(),
                 box_folder=None):
        self.name = name
        self.box_parent_folder = box_parent_folder
        self.local_parent_folder = local_parent_folder
        self.parent_modify_dates = parent_modify_dates
        self.passed_box_folder = box_folder

    @property
    def box_folder(self):
        if not hasattr(self, '_box_folder'):
            self._box_folder = None
            if self.passed_box_folder is not None:
                self._box_folder = self.passed_box_folder
                return self._box_folder
            for item in self.box_parent_folder.get_items(limit=100):
                if item.get()['name'] == self.name:
                    self._box_folder = item
                    break
            else:
                # Create new box folder if it hasn't been found
                self._box_folder = self.box_parent_folder.create_subfolder(
                    self.name)
                self.parent_modify_dates[self.name] = dict()
        return self._box_folder

    @property
    def box_folder_id(self):
        if not hasattr(self, '_box_folder_id'):
            self._box_folder_id = self.box_folder.get()['id']
        return self._box_folder_id

    @property
    def local_file_path(self):
        path = os.path.join(self.local_parent_folder, self.name)
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    @property
    def files_in_folder(self):
        if not hasattr(self, '_files_in_folder'):
            local_path = self.local_file_path
            local_files = [f for f in os.listdir(
                local_path) if os.path.isfile(os.path.join(local_path, f))]
            box_files = list()
            for item in self.box_folder.get_items(limit=100):
                if type(item) is boxsdk.object.file.File:
                    box_files.append(item.get()['name'])
            self._files_in_folder = list(set(local_files + box_files))
        return self._files_in_folder

    @property
    def modify_dates(self):
        if not hasattr(self, '_modify_dates'):
            if self.name in self.parent_modify_dates:
                self._modify_dates = self.parent_modify_dates[self.name]
            else:
                self._modify_dates = dict()
        return self._modify_dates

    @property
    def synced_files(self):
        if not hasattr(self, '_synced_files'):
            synced_files = list()
            for name in self.files_in_folder:
                sf = SyncedFile(name=name,
                                box_parent_folder=self.box_folder,
                                local_parent_folder=self.local_file_path,
                                parent_modify_dates=self.modify_dates)
                synced_files.append(sf)
            self._synced_files = synced_files
        return self._synced_files

    def refresh_modify_dates(self):
        for sf in self.synced_files:
            self._modify_dates[sf.name] = sf.modify_dates
        return self.modify_dates

    def sync_folder(self):
        logging.debug(
            "{0}: Syncing folder {1}".format(datetime.utcnow(), self.name))
        for sf in self.synced_files:
            sf.sync_files()
        self.refresh_modify_dates()


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
            assert type(parent_modify_dates) is dict
            if name in parent_modify_dates:
                file_modify_info = parent_modify_dates[name]
                assert 'box_modify_date' in file_modify_info
                assert 'local_modify_date' in file_modify_info
                box_modify_date = file_modify_info['box_modify_date']
                local_modify_date = file_modify_info['local_modify_date']
        self.stored_box_modify_date = box_modify_date
        self.local_modify_date = local_modify_date

    @property
    def modify_dates(self):
        """Modify dates for this SyncedFile

        :return: A dictionary with 'box_modify_date' and 'local_modify_date'
        :rtype: dict
        """
        return {'box_modify_date': self.box_modify_date,
                'local_modify_date': self.local_modify_date, }

    @property
    def box_modify_date(self):
        if not hasattr(self, '_box_modify_date'):
            if self.box_file is None:
                self._box_modify_date
            else:
                self.update_box_modify_date()
                assert hasattr(self, '_box_modify_date')
        return self._box_modify_date

    def update_box_modify_date(self):
        logging.debug(
            "{0}: Retrieving box modified date for {1}".format(datetime.utcnow(), self.name))
        self._box_modify_date = dateutil.parser.parse(
            self.box_file.get()['modified_at']).timestamp()

    @box_modify_date.setter
    def box_modify_date(self, value):
        self._box_modify_date = value

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

    @property
    def _local_file_exists(self):
        return os.path.isfile(self.local_file_path)

    @property
    def local_file_path(self):
        path = os.path.join(self.local_parent_folder, self.name)
        if os.path.isfile(path):
            self.local_modify_date = os.path.getmtime(path)
        return path

    @property
    def _box_file_exists(self):
        if self.box_file is not None:
            return True
        else:
            return False

    @property
    def _local_file_more_recent(self):
        if (self.box_modify_date is not None
                and self.local_modify_date is not None):
            if self.local_modify_date > self.box_modify_date:
                logging.debug(
                    'local copy of file {0} is more recent: local {1} vs  box {2}'.format(self.name, self.local_modify_date, self.box_modify_date))
                return True
        return False

    @property
    def _box_file_more_recent(self):
        if (self.box_modify_date is not None
                and self.local_modify_date is not None):
            if self.box_modify_date > self.local_modify_date:
                logging.debug(
                    'box copy of file {0} is more recent: box {1} vs local {2}'.format(self.name, self.box_modify_date, self.local_modify_date))
                return True
        return False

    def _syncronize_box_local_modify_times(self):
        self.update_box_modify_date()
        self.local_modify_date = self.box_modify_date
        os.utime(
            self.local_file_path, (self.box_modify_date, self.box_modify_date))

    def _download_box_file_to_local(self):
        file_to_write = open(self.local_file_path, 'wb')
        try:
            self.box_file.download_to(file_to_write)
        except:
            logging.error(
                'Error while downloading file {0}: {1}'.format(self.name, sys.exc_info()[0]))
        file_to_write.close()
        self._syncronize_box_local_modify_times()
        logging.debug('downloaded {0} from box. Copies should be synchronized to {1}'.format(
            self.name, self.box_modify_date))

    def _upload_local_file_to_box_folder(self):
        try:
            self.box_file = self.box_parent_folder.upload(self.local_file_path)
        except:
            logging.error(
                'Error while uploading file {0}: {1}'.format(self.name, sys.exc_info()[0]))
        self._syncronize_box_local_modify_times()
        logging.debug('uploaded {0} to box. Copies should be synchronized to {1}'.format(
            self.name, self.local_modify_date))

    def _replace_box_file_with_local(self):
        try:
            self.box_file.update_contents(self.local_file_path)
        except:
            logging.error(
                'Error while replacing file {0}: {1}'.format(self.name, sys.exc_info()[0]))
        self._syncronize_box_local_modify_times()
        logging.debug('replaced {0} to box. Copies should be synchronized to {1}'.format(
            self.name, self.local_modify_date))

    def sync_files(self):
        if self._box_file_exists and not self._local_file_exists:
            self._download_box_file_to_local()
        if self._local_file_exists and not self._box_file_exists:
            self._upload_local_file_to_box_folder()
        if self._box_file_exists and self._local_file_exists:
            if self._box_file_more_recent:
                self._download_box_file_to_local()
            if self._local_file_more_recent:
                self._replace_box_file_with_local()
