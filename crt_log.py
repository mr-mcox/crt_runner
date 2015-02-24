import re


class CRTLog(object):

    """Identify components of CRT run based on log results"""

    def __init__(self, log_file_handle):
        """
        
        :param log_file_handle: File hindle for the log
        :type log_file_handle: file_like
        """
        self.log_contents = log_file_handle.read()

    @property
    def successfully_completed(self):
        """True if the log file indicates that the run completed successfully"""
        if re.search('Collab builder has successfully completed', self.log_contents) is not None:
            return True
        else:
            return False