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
        'Warning: (.*) column not found in CM input file',
        'Expected (.*) CMs but (.*) were found']

    def user_friendly_warnings(warning):
        if warning == crt_warnings[0]:
            return "Just so you know, column X is not there"
        if warning == crt_warnings[1]:
            return "You need X CMs but there were X"

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.crt_warnings = crt_warnings
        instance.user_friendly_warning = MagicMock(
            side_effect=user_friendly_warnings)

        return instance


@pytest.fixture
def config_for_warnings_message():

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
                return """Header
                WARNINGS_LIST
                Footer"""

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.from_email = 'nick@tfa.org'
        instance.email_from_name = 'Nick'
        instance.info_by_institute = MagicMock(
            side_effect=return_institute_field)
        instance.email_text = MagicMock(side_effect=return_email_field)

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
    Expected 500 CMs but 3 were found
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


def test_list_of_warnings_with_variable_elements(log_file_with_warning,
                                                 config_variable_warning):
    config = config_variable_warning
    log = CRTLog(log_file_with_warning, config=config, institute='Atlanta')
    expected_warnings = list()

    exp_warning = config.crt_warnings[0]
    exp_substitution = re.search(
        exp_warning, log.log_contents).group(1)
    friendly_warning_pattern = config.user_friendly_warning(exp_warning)
    exp_output = re.sub(r"\b(X)\b", exp_substitution, friendly_warning_pattern)
    assert exp_output in log.warnings_in_log()


def test_list_of_warnings_with_multiple_variable_elements(log_file_with_warning,
                                                          config_variable_warning):
    config = config_variable_warning
    log = CRTLog(log_file_with_warning, config=config, institute='Atlanta')
    expected_warnings = list()

    exp_warning = config.crt_warnings[1]
    exp_substitution_a = re.search(
        exp_warning, log.log_contents).group(1)
    exp_substitution_b = re.search(
        exp_warning, log.log_contents).group(2)
    friendly_warning_pattern = config.user_friendly_warning(exp_warning)
    exp_output_a = re.sub(
        r"\b(X)\b", exp_substitution_a, friendly_warning_pattern, count=1)
    exp_output_b = re.sub(
        r"\b(X)\b", exp_substitution_b, exp_output_a, count=1)
    assert exp_output_b in log.warnings_in_log()


def test_send_warning_message(log_file_with_warning,
                              config_for_warnings_message):
    config = config_for_warnings_message
    log = CRTLog(log_file_with_warning, config=config, institute='Atlanta')
    warning_messages = ['warn_1', 'warn_2']
    with patch.object(Messenger, 'send_email') as send_email_mock:
        with patch.object(CRTLog,'warnings_in_log', return_value=warning_messages):
            log.send_warnings_message()

    expected_warning_text = "\n".join(warning_messages)
    expected_body = re.sub('WARNINGS_LIST',
                           expected_warning_text,
                           config.email_text(
                               'crt_warning', 'body'))

    send_email_mock.assert_any_call(from_email=config.from_email,
                                    from_name=config.email_from_name,
                                    to_name=config.info_by_institute(
                                        'ATL', 'ddm_name'),
                                    to_email=config.info_by_institute(
                                        'ATL', 'ddm_email'),
                                    subject=config.email_text(
                                        'crt_warning', 'subject'),
                                    body=expected_body)
