import yaml
import os.path


class Config(object):

    """Provide configuration options for the CRT Runner"""

    def __init__(self, config_file):
        """

        :param config_file: A YAML file in the expected format
        :type config_file: The path to a yaml file or a yaml stream

        """
        self.config_file = config_file
        self._config = self._yaml_from_file(config_file)

        # Create properties for the keys in the top level of the dictionary,
        # excluding certain special properties
        special_props = set(['institute', 'emails', 'warnings'])
        topline_properties = list(set(self._config.keys()) - special_props)
        for prop in topline_properties:
            self._add_topline_property(prop)

    def _yaml_from_file(self, yaml_file):
        stream = open(yaml_file, 'r')
        yaml_contents = yaml.load(stream)
        stream.close()
        return yaml_contents

    def _add_topline_property(self, name):
        # create local fget
        fget = lambda self: self._get_property(name)
        fset = lambda self, value: self._set_property(name, value)

        # add property to self
        setattr(self.__class__, name, property(fget, fset))

    def _get_property(self, name):
        return self._config[name]

    def _set_property(self, name, value):
        self._config[name] = value
        self._dump_config_to_yaml()

    def _dump_config_to_yaml(self):
        yaml_file = open(self.config_file, 'w')
        yaml.dump(self._config, yaml_file)
        yaml_file.close()

    def info_by_institute(self, institute, field):
        """Provide requested information about the institute

        :param str institute: The institute information is desired for
        :param str field: The field desired for the above institute
        :return: The field value
        :raises AssertionError: if the institute or field is not in the config file
        """
        assert 'institutes' in self._config
        assert institute in self._config['institutes']

        if field == 'path_to_folder':
            return self.path_to_institute_folder(institute)

        if field == 'last_run':
            return self.institute_last_run(institute)

        assert field in self._config['institutes'][institute]
        return self._config['institutes'][institute][field]

    def path_to_institute_folder(self, institute):
        """Provide path to local institute folder"""
        assert 'root_local_folder' in self._config
        return os.path.join(self._config['root_local_folder'], institute)

    def institute_last_run(self, institute):
        """Provide timestamp for when the CRT.pl was last run"""
        if 'last_run' in self._config['institutes'][institute]:
            return self._config['institutes'][institute]['last_run']
        else:
            return None

    def set_last_run(self, institute, value):
        self._config['institutes'][institute]['last_run'] = value

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
        """Provide user friendly warning for a given warning

        :param str crt_warning: The warning regular expression string
        :return: The user friendly text associated with that input warning
        """
        assert 'warnings' in self._config
        assert type(self._config['warnings']) is list
        for item in self._config['warnings']:
            assert 'user_friendly_warning' in item

        warning_dict = dict(zip(
            [w['crt_warning'] for w in self._config['warnings']],
            [w['user_friendly_warning'] for w in self._config['warnings']]
        ))
        return warning_dict[warning]

    @property
    def institute_list(self):
        """List of institutes
        :return: List of institutes
        :rtype: list
        """

        assert 'institutes' in self._config
        return [inst for inst in self._config['institutes'].keys()]
