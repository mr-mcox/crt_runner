from .perl_execution import PerlCommand
import os.path
import re
from .messenger import Messenger
from .box_sync import BoxSync


class Scanner(object):

    """Scan folders to determine whether CRT should be run"""

    def __init__(self, config=None):

        self.perl_command = PerlCommand()
        self.config = config
        self.files_to_check = ['cm', 'collab', 'user_settings']

    def sync_and_scan_institute_folders(self):
        """Scan all institute folders

        .. note:: Scan does not start if config file indicates that it is currently running
        """
        config = self.config
        if not config.is_running:
            config.is_running = True
            # Sync folders
            box_sync = BoxSync(config)
            box_sync.sync_institute_folders()

            # Scan folders
            for institute in config.institute_list:
                self.scan_folder(
                    config.info_by_institute(institute, 'path_to_folder'))
            config.is_running = False

    def scan_folder(self, institute):
        """Run CRT command if inputs are more recent than time of last run

        :param str institute: Institute to scan folder for
        """
        if self._most_recent_modify_timestamp_of_inputs(institute) > self.config.institute_last_run(institute):
            self.perl_command.run_crt()

    def path_for_file(self, institute=None, file=None):
        """Create path for given file type and institute

        :param str institute: Institute file needed for
        :param srt file: Type of file. Accepted values are 'cm','collab' and 'user_settings'
        :return str: Path to expected file
        """

        config = self.config
        base_name_map = {
            'collab': config.collab_file_base_name,
            'cm': config.cm_file_base_name,
            'user_settings': config.user_settings_base_name,
        }
        path = "".join([
            config.info_by_institute(institute, 'path_to_folder'),
            config.info_by_institute(institute, 'file_prefix'),
            base_name_map[file]])
        return path

    def _most_recent_modify_timestamp_of_inputs(self, institute):
        assert self.has_all_required_files(institute)

        files_to_check = ['collab', 'cm', 'user_settings']
        most_recent_timestamp = 0

        for file_type in files_to_check:
            ts = os.path.getmtime(self.path_for_file(institute, file_type))
            if ts > most_recent_timestamp:
                most_recent_timestamp = ts
        return most_recent_timestamp

    def send_message_for_missing_files(self, institute=None):
        """Send message for each missing file

        :param str institute: The institute to run this for
        """
        config = self.config

        for f in self.files_to_check:
            path = self.path_for_file(institute, f)
            if not os.path.isfile(path):
                m = Messenger(config)
                email_body = re.sub('FILE_PATH', path,
                                    config.email_text('file_missing', 'body'))
                m.send_email(from_email=config.from_email,
                             from_name=config.email_from_name,
                             to_name=config.info_by_institute(
                                 institute, 'ddm_name'),
                             to_email=config.info_by_institute(
                                 institute, 'ddm_email'),
                             subject=config.email_text(
                                 'file_missing', 'subject'),
                             body=email_body)

    def has_all_required_files(self, institute=None):
        """Indicate wheter all required files are present

        :param str institute: The institute to run this for
        :return bool: True if all files are present, False otherwise
        """
        for f in self.files_to_check:
            path = self.path_for_file(institute, f)
            if not os.path.isfile(path):
                return False
        return True
