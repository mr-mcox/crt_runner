from unittest.mock import patch
from ..config import Config


def test_path_to_crt_script():
    config_yaml = {'path_to_perl_script': '/Example/Path/CRT.pl'}
    with patch('yaml.load', return_value=config_yaml):
        c = Config('config.yaml')
    assert c.path_to_perl_script == config_yaml['path_to_perl_script']