from unittest.mock import patch
from ..perl_execution import PerlCommand
from ..messenger import Messenger
from ..crt_log import CRTLog
import tempfile

def test_run_command_with_parameters():
    pc = PerlCommand()
    pc.cms_file = 'some_cms_file.xls'
    pc.collab_file = 'some_collab_file.xls'
    pc.user_settings_file = 'some_user_settings_file.txt'
    pc.output_directory = 'some_output_directory'
    pc.path_to_crt = 'path_to_crt'
    pc.log_file = 'dummy_log_file'

    with patch('subprocess.call') as subprocess_mock:
      pc.run_crt()
    expected_arguments = ['perl',
                          'path_to_crt',
                          'some_cms_file.xls',
                          'some_collab_file.xls',
                          'some_user_settings_file.txt',
                          'some_output_directory']
    subprocess_mock.assert_called_with(expected_arguments,stdout=pc.log_file)

def test_successful_run_results_sends_mesage():
  pc = PerlCommand()
  pc.log_file = tempfile.TemporaryFile()
  with patch.object(PerlCommand,'run_crt') as run_crt_mock:
    with patch.object(Messenger,'send_email') as send_email_mock:
      with patch.object(CRTLog,'successfully_completed',return_value=True):
        pc.run_crt_with_notifications()
  
  send_email_mock.assert_called_with('CRT Successfully completed!')