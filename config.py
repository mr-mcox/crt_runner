import yaml


class Config(object):

    """Provide configuration options for the CRT Runner"""

    def __init__(self, config_file):
        """

        :param config_file: A YAML file in the expected format
        :type config_file: The path to a yaml file or a yaml stream

        """
        self._config = yaml.load(config_file)

        # Create properties for the keys in the top level of the dictionary,
        # excluding certain special properties
        special_props = set(['institute', 'emails', 'warnings'])
        topline_properties = list(set(self._config.keys()) - special_props)
        for prop in topline_properties:
            self._add_topline_property(prop)

    def _add_topline_property(self, name):
        # create local fget
        fget = lambda self: self._get_property(name)

        # add property to self
        setattr(self.__class__, name, property(fget))

    def _get_property(self, name):
        return self._config[name]

    def info_by_institute(self, institute, field):
        """Provide requested information about the institute

        :param str institute: The institute information is desired for
        :param str field: The field desired for the above institute
        :return: The field value
        :raises AssertionError: if the institute or field is not in the config file
        """
        assert 'institutes' in self._config
        assert institute in self._config['institutes']
        assert field in self._config['institutes'][institute]
        return self._config['institutes'][institute][field]

    def email_text(self, email_type, field):
        """Provide text for a specific type of email

        :param str email_type: The email type that the information is desired for
        :param str field: The field desired for the above email
        :return: The field value
        :raises AssertionError: if the email_type or field is not in the config file
        """
        assert 'emails' in self._config
        assert email_type in self._config['emails']
        assert field in self._config['emails'][email_type]
        return self._config['emails'][email_type][field]

    @property
    def crt_warnings(self):
        """Provide list of crt warnings from config file

        :return: A list of regular expression search strings
        """
        assert 'warnings' in self._config
        assert type(self._config['warnings']) is list
        for item in self._config['warnings']:
            assert 'crt_warning' in item
        return [w['crt_warning'] for w in self._config['warnings']]

    def user_friendly_warning(self, warning):

        warning_dict = dict(zip(
            [w['crt_warning'] for w in self._config['warnings']],
            [w['user_friendly_warning'] for w in self._config['warnings']]
        ))
        return warning_dict[warning]
