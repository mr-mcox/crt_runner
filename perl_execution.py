"""
.. module:: perl_execution
    :synopsis: Handles the interface with the Perl CRT.pl command
"""

import subprocess
from .messenger import Messenger
from .crt_log import CRTLog


class PerlCommand(object):

    """Call the perl command"""

    def __init__(self, config=None):
        """
        Pass the config file for use
        """
        self.config = config

    def run_crt(self):
        """
        Run the CRT command

        .. note:: while there are no arguments, this relies on the object having several properties set which it does not currently check for
        """
        subprocess.call(['perl',
                         self.path_to_crt,
                         self.cms_file,
                         self.collab_file,
                         self.user_settings_file,
                         self.output_directory], stdout=self.log_file)

    def run_crt_with_notifications(self,institute="Atlanta"):
        """
        Run the CRT and notify send messages upon completion
        """
        m = Messenger()
        config = self.config
        m.send_email(from_email=config.from_email,
                     from_name=config.email_from_name,
                     to_name=config.info_by_institute(
                         'Atlanta', 'ddm_name'),
                     to_email=config.info_by_institute(
                         'Atlanta', 'ddm_email'),
                     subject=config.email_text('crt_started', 'subject'),
                     body=config.email_text('crt_started', 'body'))
        self.run_crt()
        log = CRTLog(self.log_file,institute=institute)
        if log.successfully_completed:
            m.send_email(from_email=config.from_email,
                     from_name=config.email_from_name,
                     to_name=config.info_by_institute(
                         institute, 'ddm_name'),
                     to_email=config.info_by_institute(
                         institute, 'ddm_email'),
                     subject=config.email_text('crt_success', 'subject'),
                     body=config.email_text('crt_success', 'body'))
