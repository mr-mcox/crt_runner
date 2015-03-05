import yaml


class Config(object):

    """Provide configuration options for the CRT Runner"""

    def __init__(self, config_file):
        """
        
        :param config_file: A YAML file in the expected format
        :type config_file: The path to a yaml file or a yaml stream
        """
        self._config = yaml.load(config_file)

    @property
    def path_to_perl_script(self):
        """Path to the perl script that can be executed"""
        return self._config['path_to_perl_script']

    @property
    def mandrill_api_key(self):
        """Path to the perl script that can be executed"""
        return self._config['mandrill_api_key']
