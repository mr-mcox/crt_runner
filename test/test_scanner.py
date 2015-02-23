import os.path
from ..scanner import Scanner
from ..perl_execution import PerlCommand
from unittest.mock import patch

def test_call_runner_if_output_file_missing():
	canary_file = 'placement_reccomendations_and_cm_level_scoring.xls'
	with patch('os.path.isfile',return_value=False) as isfile_mock:
		with patch.object(PerlCommand,'run_crt') as run_crt_mock:
			s = Scanner()
			s.scan_folder('some_folder')
	isfile_mock.assert_called_with(os.path.join('some_folder',canary_file))
	run_crt_mock.assert_called_with()