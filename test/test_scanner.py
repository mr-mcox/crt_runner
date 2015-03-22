import os.path
from ..scanner import Scanner
from ..perl_execution import PerlCommand
from ..messenger import Messenger
from ..config import Config
from ..box_sync import BoxSync
from unittest.mock import patch, MagicMock
import re
import pytest

@pytest.fixture
def config():

    def return_institute_field(institute,value):
        if value == 'path_to_folder':
            return '/path/to/folder/'
        if value == 'file_prefix':
            return 'ATL'

    with patch('crt_runner.config.Config') as mock:
        config = mock.return_value
        config.cm_file_base_name = '_CMs.xls'
        config.collab_file_base_name = '_collabs.xls'
        config.user_settings_base_name = '_user_settings.txt'
        config.path_to_perl_script = '/path/to/crt.pl'
        config.crt_log_base_name = 'log_file'
        config.info_by_institute = MagicMock(
            side_effect=return_institute_field)
    return config

def test_path_for_required_file(config):
    config = config
    

    expected_collab_path = "".join([
        config.info_by_institute('ATL', 'path_to_folder'),
        config.info_by_institute('ATL', 'file_prefix'),
        config.collab_file_base_name])
    expected_cm_path = "".join([
        config.info_by_institute('ATL', 'path_to_folder'),
        config.info_by_institute('ATL', 'file_prefix'),
        config.cm_file_base_name])
    expected_user_settings_path = "".join([
        config.info_by_institute('ATL', 'path_to_folder'),
        config.info_by_institute('ATL', 'file_prefix'),
        config.user_settings_base_name])
    s = Scanner(config=config)
    assert s.path_for_file(
        institute='Atlanta', file='collab') == expected_collab_path
    assert s.path_for_file(institute='Atlanta', file='cm') == expected_cm_path
    assert s.path_for_file(
        institute='Atlanta', 
        file='user_settings') == expected_user_settings_path


@pytest.fixture
def missing_cm_file_setup(request):
    f = open('collab_file.xls', 'w')
    f = open('user_settings.txt', 'w')

    def delete_files():
        os.remove('collab_file.xls')
        os.remove('user_settings.txt')
    request.addfinalizer(delete_files)


@pytest.fixture
def config_for_missing_file_message():

    def return_institute_field(institute, value):
        if value == 'ddm_name':
            return 'William'
        if value == 'ddm_email':
            return 'william@gmail.com'

    def return_email_field(email_type, value):
        if email_type == 'file_missing':
            if value == 'subject':
                return 'A file is missing'
            if value == 'body':
                return """A file FILE_PATH is missing"""

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.from_email = 'nick@tfa.org'
        instance.email_from_name = 'Nick'
        instance.info_by_institute = MagicMock(
            side_effect=return_institute_field)
        instance.email_text = MagicMock(side_effect=return_email_field)

        return instance


def test_send_message_for_missing_file(missing_cm_file_setup,
                                       config_for_missing_file_message):

    def return_file_path(institute, f):
        if f == 'cm':
            return 'cm_file.xls'
        if f == 'collab':
            return 'collab_file.xls'
        if f == 'user_settings':
            return 'user_settings.txt'
    config = config_for_missing_file_message

    with patch.object(Scanner, 'path_for_file', side_effect=return_file_path):
        with patch.object(Messenger, 'send_email') as send_email_mock:
            s = Scanner(config=config)
            s.send_message_for_missing_files('ATL')
            expected_body = re.sub('FILE_PATH',
                                   s.path_for_file('ATL', 'cm'),
                                   config.email_text('file_missing', 'body'))
    send_email_mock.assert_called_with(from_email=config.from_email,
                                       from_name=config.email_from_name,
                                       to_name=config.info_by_institute(
                                           'ATL', 'ddm_name'),
                                       to_email=config.info_by_institute(
                                           'ATL', 'ddm_email'),
                                       subject=config.email_text(
                                           'file_missing', 'subject'),
                                       body=expected_body)


def test_has_all_required_files(missing_cm_file_setup):
    def return_file_path(institute, f):
        if f == 'cm':
            return 'cm_file.xls'
        if f == 'collab':
            return 'collab_file.xls'
        if f == 'user_settings':
            return 'user_settings.txt'
    with patch.object(Scanner, 'path_for_file', side_effect=return_file_path):
        s = Scanner()
        assert s.has_all_required_files(institute='ATL') == False

def test_scanning_folders_sets_is_running():
    config_input = {'is_running': False, 'institutes': {
        'Atlanta': {}}, 'root_local_folder': '/path'}
    with patch.object(Config, '_yaml_from_file', 
        return_value=config_input), patch.object(Config, 
        '_set_property') as set_prop_mock, patch.object(Scanner, 
        'scan_folder'), patch.object(BoxSync, 
        'authenticate_client'), patch.object(BoxSync, 'sync_institute_folders'):
        config = Config('file.yaml')
        s = Scanner(config=config)
        s.sync_and_scan_institute_folders()
    set_prop_mock.assert_any_call('is_running', True)
    assert config.is_running is False

def test_scan_does_not_occur_if_is_running_true():
    config_input = {'is_running': True, 'institutes': {
        'Atlanta': {}}, 'root_local_folder': '/path'}
    with patch.object(Config, '_yaml_from_file', 
        return_value=config_input), patch.object(Config, 
        '_set_property') as set_prop_mock, patch.object(Scanner, 
        'scan_folder') as folder_scan_mock:
        config = Config('file.yaml')
        s = Scanner(config=config)
        s.sync_and_scan_institute_folders()
    assert folder_scan_mock.called is False

def test_call_runner_if_input_files_more_recent_than_last_run(config):
    config = config
    #Setup where files are more recent than last run
    with patch.object(PerlCommand, 'run_crt_with_notifications') as run_crt_mock, patch.object(Scanner,
        '_most_recent_modify_timestamp_of_inputs',return_value=100), patch.object(Config,
        'institute_last_run',return_value=90), patch.object(Config, '_yaml_from_file', 
        return_value=dict()):
        config.institute_last_run = MagicMock(return_value=90)
        s = Scanner(config=config)
        s.scan_folder('some_folder')
    assert run_crt_mock.called

    #Setup where files are mot more recent than last run
    with patch.object(PerlCommand, 'run_crt_with_notifications') as run_crt_mock, patch.object(Scanner,
        '_most_recent_modify_timestamp_of_inputs',return_value=100), patch.object(Config,
        'institute_last_run',return_value=110), patch.object(Config, '_yaml_from_file', 
        return_value=dict()):
        # config = Config('file.yaml')
        config.institute_last_run = MagicMock(return_value=110)
        scan = Scanner(config=config)
        scan.scan_folder('some_folder')
    assert run_crt_mock.called is False

def test_call_runner_if_conditions_right_for_first_run(config):
    with patch.object(PerlCommand, 'run_crt_with_notifications') as run_crt_mock:
            config.institute_last_run = MagicMock(return_value=None)
            scan = Scanner(config=config)
            scan.has_all_required_files = MagicMock(return_value=True)
            scan._most_recent_modify_timestamp_of_inputs = MagicMock(return_value=None)
            scan.scan_folder('some_folder')
    assert run_crt_mock.called
