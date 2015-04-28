from unittest.mock import patch
from ..config import Config
import os.path
import tempfile


def test_topline_settings():
    config_yaml = {'path_to_perl_script': '/Example/Path/CRT.pl',
                   'from_email': 'me@example.com'}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    for key in config_yaml.keys():
        assert getattr(c, key) == config_yaml[key]


def test_lookup_info_by_institute():
    config_yaml = {'institutes': {'Atlanta': {'ddm_name': 'Elliot'}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
        atlanta_ddm = config_yaml['institutes']['Atlanta']['ddm_name']
    assert c.info_by_institute('Atlanta', 'ddm_name') == atlanta_ddm


def test_lookup_folder_by_institute():
    config_yaml = {'root_local_folder': '/path/to/folder',
                   'institutes': {'Atlanta': {}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
        atlanta_path = os.path.join(
            config_yaml['root_local_folder'], 'Atlanta')
    assert c.info_by_institute('Atlanta', 'path_to_folder') == atlanta_path


def test_lookup_email_by_type():
    config_yaml = {'emails': {'crt_started': {'subject': 'CRT started!',
                                              'body': 'It has begun'}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    started_subject = config_yaml['emails']['crt_started']['subject']
    assert c.email_text('crt_started', 'subject') == started_subject


def test_crt_warnings():
    config_yaml = {'warnings': [
        {'crt_warning': 'Warning: No CMs listed in institute region',
         'user_friendly_warning': "Hey! There aren't any CMS"}
    ]}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    assert c.crt_warnings == [w['crt_warning']
                              for w in config_yaml['warnings']]


def test_user_friendly_warnings():
    config_yaml = {'warnings': [
        {'crt_warning': 'Warning: No CMs listed in institute region',
         'user_friendly_warning': "Hey! There aren't any CMS"},
        {'crt_warning': 'Warning: Your music is too loud',
         'user_friendly_warning': """The CRT is having trouble concentrating
                                     with how loud your music is"""}
    ]}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    for i, warning in enumerate(c.crt_warnings):
        user_warning = config_yaml['warnings'][i]['user_friendly_warning']
        c.user_friendly_warning(warning) == user_warning


def test_institute_list():
    config_yaml = {'institutes': {'Atlanta': {}, 'Houston': {}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
        assert c.institute_list == [
            inst for inst in config_yaml['institutes'].keys()]


def test_setting_config_value_triggers_dump():
    config_yaml = {'new_property': 'old_value'}
    with patch.object(Config, '_dump_config_to_yaml') as mock_dump, patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        config = Config('config.yaml')
        config.new_property = 'new_value'
    assert mock_dump.called

def test_last_run_for_institute_returns_none_if_non_existant():
    config_yaml = {'institutes': {'Atlanta': {}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    assert c.info_by_institute('Atlanta', 'last_run') is None

def test_set_last_run_for_institute():
    config_yaml = {'institutes': {'Atlanta': {}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
        c.set_last_run('Atlanta',1234)
    assert c.info_by_institute('Atlanta', 'last_run') == 1234


def test_if_email_field_ends_in_html_return_contents_of_the_file(request):
    config_yaml = {'emails': {'crt_started': {'subject': 'subject.html',
                                              'body': 'It has begun'}}}
    subj_file = open(config_yaml['emails']['crt_started']['subject'],'w')
    subj_file_contents = "Here's a subject!"
    subj_file.write(subj_file_contents)
    subj_file.close()

    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    assert c.email_text('crt_started', 'subject') == subj_file_contents

    def delete_subject_file():
        os.remove(config_yaml['emails']['crt_started']['subject'])
    request.addfinalizer(delete_subject_file)

def test_box_folder_for_institute_returns_none_if_non_existant():
    config_yaml = {'institutes': {'Atlanta': {}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
    assert c.info_by_institute('Atlanta', 'box_folder_id') is None

def test_set_box_folder_id_for_institute():
    config_yaml = {'institutes': {'Atlanta': {}}}
    with patch.object(Config, '_yaml_from_file', return_value=config_yaml):
        c = Config('config.yaml')
        c.set_box_folder_id('Atlanta',1234)
    assert c.info_by_institute('Atlanta', 'box_folder_id') == 1234
