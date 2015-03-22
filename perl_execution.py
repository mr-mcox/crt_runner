"""
.. module:: perl_execution
    :synopsis: Handles the interface with the Perl CRT.pl command
"""

import subprocess
from .messenger import Messenger
from .crt_log import CRTLog
from datetime import datetime


class PerlCommand(object):

    """Call the perl command"""

    def __init__(self, config=None):
        """
        Pass the config file for use
        """
        self.config = config

    def run_crt(self, institute=None,
        path_to_crt=None,cms_file=None,
        collab_file=None,user_settings_file=None,
        output_directory=None,log_file=None):
        """
        Run the CRT command

        .. note:: while there are no arguments, this relies on the object having several properties set which it does not currently check for
        """
        if self.config is not None:
            self.config.set_last_run(institute,datetime.now().timestamp())
        subprocess.call(['perl',
                         path_to_crt,
                         cms_file,
                         collab_file,
                         user_settings_file,
                         output_directory], stdout=log_file)

    def run_crt_with_notifications(self,institute=None,
        path_to_crt=None,cms_file=None,
        collab_file=None,user_settings_file=None,
        output_directory=None,log_file=None):
        """
        Run the CRT and notify send messages upon completion
        """
        config = self.config
        m = Messenger(config)
        m.send_email(from_email=config.from_email,
                     from_name=config.email_from_name,
                     to_name=config.info_by_institute(
                         'Atlanta', 'ddm_name'),
                     to_email=config.info_by_institute(
                         'Atlanta', 'ddm_email'),
                     subject=config.email_text('crt_started', 'subject'),
                     body=config.email_text('crt_started', 'body'))
        self.run_crt(institute=institute,
        path_to_crt=path_to_crt,cms_file=cms_file,
        collab_file=collab_file,user_settings_file=user_settings_file,
        output_directory=output_directory,log_file=log_file)
        log = CRTLog(log_file,institute=institute)
        if log.successfully_completed:
            m.send_email(from_email=config.from_email,
                     from_name=config.email_from_name,
                     to_name=config.info_by_institute(
                         institute, 'ddm_name'),
                     to_email=config.info_by_institute(
                         institute, 'ddm_email'),
                     subject=config.email_text('crt_success', 'subject'),
                     body=config.email_text('crt_success', 'body'))
