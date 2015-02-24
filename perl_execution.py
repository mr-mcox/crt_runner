"""
.. module:: perl_execution
	:synopsis: Handles the interface with the Perl CRT.pl command
"""

import subprocess
from .messenger import Messenger
from .crt_log import CRTLog


class PerlCommand(object):

    """Call the perl command"""

    def __init__(self):
        """
        There is nothing in the init process for the moment
        """
        pass

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

    def run_crt_with_notifications(self):
        """
        Run the CRT and notify send messages upon completion
        """

        self.run_crt()
        log = CRTLog(self.log_file)
        if log.successfully_completed:
            m = Messenger()
            m.send_email('CRT Successfully completed!')
