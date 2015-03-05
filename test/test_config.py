from unittest.mock import patch
from ..config import Config


def test_topline_settings():
    config_yaml = {'path_to_perl_script': '/Example/Path/CRT.pl',
                   'from_email': 'me@example.com'}
    with patch('yaml.load', return_value=config_yaml):
        c = Config('config.yaml')
    for key in config_yaml.keys():
        assert getattr(c, key) == config_yaml[key]


def test_lookup_info_by_institute():
    config_yaml = {'institutes': {'Atlanta': {'ddm_name': 'Elliot'}}}
    with patch('yaml.load', return_value=config_yaml):
        c = Config('config.yaml')
        atlanta_ddm = config_yaml['institutes']['Atlanta']['ddm_name']
    assert c.info_by_institute('Atlanta', 'ddm_name') == atlanta_ddm


def test_lookup_email_by_type():
    config_yaml = {'emails': {'crt_started': {'subject': 'CRT started!',
                                           'body': 'It has begun'}}}
    with patch('yaml.load', return_value=config_yaml):
        c = Config('config.yaml')
    started_subject = config_yaml['emails']['crt_started']['subject']
    assert c.email_text('crt_started', 'subject') == started_subject
