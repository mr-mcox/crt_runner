import re


class CRTLog(object):

    """Identify components of CRT run based on log results"""

    def __init__(self, log_file_handle):
        self.log_contents = log_file_handle.read()

    @property
    def successfully_completed(self):
        if re.search('Collab builder has successfully completed', self.log_contents) is not None:
            return True
        else:
            return False