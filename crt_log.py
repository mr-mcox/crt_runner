import re
from .messenger import Messenger


def next_sub(sub_iter):
    return next(sub_iter)


class CRTLog(object):

    """Identify components of CRT run based on log results"""

    def __init__(self, log_file_handle, institute='Atlanta', config=None):
        """

        :param log_file_handle: File hindle for the log
        :type log_file_handle: file_like
        """
        if type(log_file_handle) is str:
            log_file_handle = open(log_file_handle)
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

    def send_warnings_message(self):
        """
        Send message based on warnings in the log

        .. note:: Only sends message when there is at least one warning to send.
        .. note:: Expects there to be a crt_warning message in config
        .. note:: Expects the body of the message to have the text WARNINGS_LIST
        """
        warning_list = self.warnings_in_log()
        if len(warning_list) > 0:
            m = Messenger(self.config)
            config = self.config
            joined_warnings = "\n".join(warning_list)
            full_body = re.sub('WARNINGS_LIST', joined_warnings,
                               config.email_text('crt_warning', 'body'))
            m.send_email(from_email=config.from_email,
                         from_name=config.email_from_name,
                         to_name=config.info_by_institute(
                             self.institute, 'ddm_name'),
                         to_email=config.info_by_institute(
                             self.institute, 'ddm_email'),
                         subject=config.email_text('crt_warning', 'subject'),
                         body=full_body)


    def warnings_in_log(self):
        """
        List all warnings present in log

        :return: list of strings of user friendly warnings
        .. note:: source of warnings is from the config object
        """
        warning_list = list()
        config = self.config
        for warning in config.crt_warnings:
            warning_list = warning_list + \
                self._user_friendly_warning_from_log(warning)
        return warning_list



    def _user_friendly_warning_from_log(self, warning):
        config = self.config
        warning_re = re.compile(warning)
        if re.search(warning_re, self.log_contents) is not None:
            # If warning has groups, then substitute in the user friendly
            # string
            if warning_re.groups > 1:
                warn_pat = config.user_friendly_warning(warning)
                groups = warning_re.findall(self.log_contents)
                uf_warnings = list()
                for group in groups:
                    iter_groups = iter(group)
                    uf_warnings.append(re.sub(
                        r"\b(X)\b", lambda p: next_sub(iter_groups), warn_pat))
                return uf_warnings
            if warning_re.groups > 0:
                groups = warning_re.findall(self.log_contents)
                uf_warnings = list()
                for group in groups:
                    uf_warnings.append(re.sub(
                        r"\b(X)\b", group, config.user_friendly_warning(warning)))
                return uf_warnings
            else:
                return [config.user_friendly_warning(warning)]
        else:
            # Return empty list if no matches found
            return list()
