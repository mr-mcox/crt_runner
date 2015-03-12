import pytest
from unittest.mock import patch, MagicMock
import os
import re
from ..crt_log import CRTLog
from ..messenger import Messenger


@pytest.fixture
def config():

    def return_institute_field(institute, value):
        if value == 'ddm_name':
            return 'William'
        if value == 'ddm_email':
            return 'william@gmail.com'

    def return_email_field(email_type, value):
        if email_type == 'crt_warning':
            if value == 'subject':
                return 'The Start Subject'
            if value == 'body':
                return 'The start body'

    crt_warnings = ['Warning: No CMs listed in institute region']

    user_friendly_warning = "Hey! There aren't any CMS"

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.from_email = 'nick@tfa.org'
        instance.email_from_name = 'Nick'
        instance.crt_warnings = crt_warnings
        instance.user_friendly_warning = user_friendly_warning
        instance.info_by_institute = MagicMock(
            side_effect=return_institute_field)
        instance.email_text = MagicMock(side_effect=return_email_field)

        return instance


@pytest.fixture
def config_with_multiple_warnings():
    crt_warnings = ['Warning: No CMs listed in institute region',
                    'Here is another warning']

    def user_friendly_warnings(warning):
        if warning == crt_warnings[0]:
            return "Hey! There aren't any CMS"
        if warning == crt_warnings[1]:
            return "Another friendly warning"

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.crt_warnings = crt_warnings
        instance.user_friendly_warning = MagicMock(
            side_effect=user_friendly_warnings)
        return instance


@pytest.fixture
def config_variable_warning():
    crt_warnings = [
        'Warning: (.*) column not found in CM input file (but its not needed for this program to run)']

    user_friendly_warning = "Just so you know, column X is not there"

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.crt_warnings = crt_warnings
        instance.user_friendly_warning = user_friendly_warning

        return instance


@pytest.fixture
def successfully_completed_log_file(request):
    f = open('log_file.txt', 'w')
    file_contents = """
    We need between 377 and 410 CMs to fill collabs and there are 402 CMs
    Beginning computation of cm collab scores
    Now beginning CM placements
    There are currently 170 collabs to place. 3 cms have been placed so far.
    There are currently 160 collabs to place. 26 cms have been placed so far.
    There are currently 0 collabs to place. 375 cms have been placed so far.
    CMs are all placed
    After filling remaining collabs, 400 cms have been placed so far.
    After 0 swaps attempted there have been 0 swaps made
    There were 4 swaps made
    Collab builder has successfully completed. Please open the output files for the suggested CM placements.
    """
    f.write(file_contents)
    f.close()

    def delete_log_file():
        os.remove('log_file.txt')
    request.addfinalizer(delete_log_file)
    return open('log_file.txt')


@pytest.fixture
def log_file_with_warning(request):
    f = open('log_file.txt', 'w')
    file_contents = """
    Warning: No CMs listed in institute region
    Here is another warning
    Warning: Collab request column not found in CM input file (but its not needed for this program to run)
    We need between 377 and 410 CMs to fill collabs and there are 402 CMs
    Collab builder has successfully completed. Please open the output files for the suggested CM placements.
    """
    f.write(file_contents)
    f.close()

    def delete_log_file():
        os.remove('log_file.txt')
    request.addfinalizer(delete_log_file)
    return open('log_file.txt')


def test_crt_completed_successfully(successfully_completed_log_file):
    l = CRTLog(successfully_completed_log_file)
    assert l.successfully_completed


def test_generate_list_of_warnings_from_log_file(log_file_with_warning,
                                                 config_with_multiple_warnings):
    config = config_with_multiple_warnings
    log = CRTLog(log_file_with_warning, config=config, institute='Atlanta')
    expected_warnings = list()
    for warning in config.crt_warnings:
        if re.search(warning, log.log_contents) is not None:
            expected_warnings.append(config.user_friendly_warning(warning))

    assert set(expected_warnings) == set(log.warnings_in_log())

# def test_send_message_with_variable_elements(log_file_with_warning, config_variable_warning):
#     l = CRTLog(log_file_with_warning, config=config, institute='Atlanta')
#     with patch.object(Messenger, 'send_email') as send_email_mock:
#         l.send_emails_for_warnings()
