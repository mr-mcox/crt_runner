from unittest.mock import patch, MagicMock
from ..perl_execution import PerlCommand
from ..messenger import Messenger
from ..crt_log import CRTLog
from ..config import Config
import tempfile
import pytest


@pytest.fixture
def config():

    def return_institute_field(institute, value):
        if value == 'ddm_name':
            return 'William'
        if value == 'ddm_email':
            return 'william@gmail.com'
    def return_email_field(email_type, value):
      if email_type == 'crt_started':
        if value == 'subject':
            return 'The Start Subject'
        if value == 'body':
            return 'The start body'
      if email_type == 'crt_success':
        if value == 'subject':
            return 'The Compl Subject'
        if value == 'body':
            return 'The Compl body'

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.from_email = 'nick@tfa.org'
        instance.email_from_name = 'Nick'
        instance.info_by_institute = MagicMock(side_effect=return_institute_field)
        instance.email_text = MagicMock(side_effect=return_email_field)

        return instance


def test_run_command_with_parameters():
    pc = PerlCommand()
    cms_file = 'some_cms_file.xls'
    collab_file = 'some_collab_file.xls'
    user_settings_file = 'some_user_settings_file.txt'
    output_directory = 'some_output_directory'
    path_to_crt = 'path_to_crt'
    log_file = 'dummy_log_file'

    with patch('subprocess.call') as subprocess_mock:
        pc.run_crt(path_to_crt=path_to_crt,cms_file=cms_file,
        collab_file=collab_file,user_settings_file=user_settings_file,
        output_directory=output_directory,log_file=log_file)
    expected_arguments = ['perl',
                          path_to_crt,
                          cms_file,
                          collab_file,
                          user_settings_file,
                          output_directory]
    subprocess_mock.assert_called_with(expected_arguments, stdout=log_file)


def test_successful_run_results_sends_mesage(config):
    pc = PerlCommand(config)
    log_file = tempfile.TemporaryFile()
    with patch.object(PerlCommand, 'run_crt'):
        with patch.object(Messenger, 'send_email') as send_email_mock:
            with patch.object(CRTLog, 'successfully_completed', return_value=True):
                pc.run_crt_with_notifications(log_file=log_file)

    send_email_mock.assert_any_call(from_email=config.from_email,
                                    from_name=config.email_from_name,
                                    to_name=config.info_by_institute(
                                        'ATL', 'ddm_name'),
                                    to_email=config.info_by_institute(
                                        'ATL', 'ddm_email'),
                                    subject=config.email_text(
                                        'crt_started', 'subject'),
                                    body=config.email_text(
                                        'crt_started', 'body'))


def test_send_message_when_run_starts(config):
    pc = PerlCommand(config)
    log_file = tempfile.TemporaryFile()
    with patch.object(PerlCommand, 'run_crt'):
        with patch.object(Messenger, 'send_email') as send_email_mock:
            with patch.object(CRTLog, 'successfully_completed', return_value=True):
                pc.run_crt_with_notifications(log_file=log_file)
    send_email_mock.assert_any_call(from_email=config.from_email,
                                    from_name=config.email_from_name,
                                    to_name=config.info_by_institute(
                                        'ATL', 'ddm_name'),
                                    to_email=config.info_by_institute(
                                        'ATL', 'ddm_email'),
                                    subject=config.email_text(
                                        'crt_success', 'subject'),
                                    body=config.email_text(
                                        'crt_success', 'body'))

def test_run_crt_updates_institute_run_time():
    config_input = dict()
    with patch.object(Config, '_yaml_from_file', 
        return_value=config_input), patch('subprocess.call'),patch.object(Config,
        'set_last_run') as last_run_mock:
        config = Config('file.yaml')
        pc = PerlCommand(config=config)
        pc.run_crt(institute='Atlanta')
        assert last_run_mock.called
