from .perl_execution import PerlCommand
import os.path
import re
from .messenger import Messenger


class Scanner(object):

    """Scan folders to determine whether CRT should be run"""

    def __init__(self, config=None):
        """

        .. todo:: Canary file should be replaced with more sophisticated run condtions
        """
        self.canary_file = 'placement_reccomendations_and_cm_level_scoring.xls'
        self.perl_command = PerlCommand()
        self.config = config
        self.files_to_check = ['cm', 'collab', 'user_settings']

    def scan_folder(self, folder):
        """Run CRT command if canary file missing from identified folder

        :param folder: Path to the folder to scan for the canary file
        :type folder: str
        """
        canary_file = self.canary_file
        if not os.path.isfile(os.path.join(folder, canary_file)):
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

    def send_message_for_missing_files(self, institute=None):
        """Send message for each missing file

        :param str institute: The institute to run this for
        """
        config = self.config

        for f in self.files_to_check:
            path = self.path_for_file(institute, f)
            if not os.path.isfile(path):
                m = Messenger()
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
