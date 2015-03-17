import os.path
from ..scanner import Scanner
from ..perl_execution import PerlCommand
from unittest.mock import patch, MagicMock


def test_call_runner_if_output_file_missing():
    canary_file = 'placement_reccomendations_and_cm_level_scoring.xls'
    with patch('os.path.isfile', return_value=False) as isfile_mock:
        with patch.object(PerlCommand, 'run_crt') as run_crt_mock:
            s = Scanner()
            s.scan_folder('some_folder')
    isfile_mock.assert_called_with(os.path.join('some_folder', canary_file))
    run_crt_mock.assert_called_with()


def test_path_for_required_file():

    def return_institute_field(institute, value):
        if value == 'path_to_folder':
            return '/path/to/folder/'
        if value == 'file_prefix':
            return 'ATL'

    with patch('crt_runner.config.Config') as mock:
        config = mock.return_value
        config.cm_file_base_name = '_CMs.xls'
        config.collab_file_base_name = '_collabs.xls'
        config.user_settings_base_name = '_user_settings.txt'
        config.info_by_institute = MagicMock(
            side_effect=return_institute_field)

    expected_collab_path = "".join([
        config.info_by_institute('ATL','path_to_folder'),
        config.info_by_institute('ATL','file_prefix'),
        config.collab_file_base_name])
    expected_cm_path = "".join([
        config.info_by_institute('ATL','path_to_folder'),
        config.info_by_institute('ATL','file_prefix'),
        config.cm_file_base_name])
    expected_user_settings_path = "".join([
        config.info_by_institute('ATL','path_to_folder'),
        config.info_by_institute('ATL','file_prefix'),
        config.user_settings_base_name])
    s = Scanner(config=config)
    assert s.path_for_file(
        institute='Atlanta', file='collab') == expected_collab_path
    assert s.path_for_file(institute='Atlanta', file='cm') == expected_cm_path
    assert s.path_for_file(
        institute='Atlanta', file='user_settings') == expected_user_settings_path
