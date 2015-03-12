import re
from .messenger import Messenger


class CRTLog(object):

    """Identify components of CRT run based on log results"""

    def __init__(self, log_file_handle, institute='Atlanta', config=None):
        """

        :param log_file_handle: File hindle for the log
        :type log_file_handle: file_like
        """
        self.log_contents = log_file_handle.read()
        self.config = config
        self.institute = institute

    @property
    def successfully_completed(self):
        """True if the log file indicates that the run completed successfully"""
        if re.search('Collab builder has successfully completed', self.log_contents) is not None:
            return True
        else:
            return False

    # def send_emails_for_warnings(self):
    #     m = Messenger()
    #     config = self.config
    #     for warning in config.crt_warnings:
    #         if re.search(warning, self.log_contents) is not None:
    #             m.send_email(from_email=config.from_email,
    #                          from_name=config.email_from_name,
    #                          to_name=config.info_by_institute(
    #                              self.institute, 'ddm_name'),
    #                          to_email=config.info_by_institute(
    #                              self.institute, 'ddm_email'),
    #                          subject=config.email_text('crt_warning', 'subject'),
    # body=config.email_text('crt_warning', config.user_friendly_warning))

    def warnings_in_log(self):
        """
        List all warnings present in log

        :return: list of strings of user friendly warnings
        .. note:: source of warnings is from the config object
        """
        warning_list = list()
        config = self.config
        for warning in config.crt_warnings:
            if re.search(warning, self.log_contents) is not None:
                warning_list.append(config.user_friendly_warning(warning))
        return warning_list
