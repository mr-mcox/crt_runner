import yaml


class Config(object):

    """Provide configuration options for the CRT Runner"""

    def __init__(self, config_file):
        self._config = yaml.load(config_file)

    @property
    def path_to_perl_script(self):
        return self._config['path_to_perl_script']
