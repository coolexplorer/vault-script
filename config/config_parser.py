import os
from configparser import ConfigParser


class ConfigParserFactory(object):
    def __init__(self, config_filename):
        self.filename = os.path.join(os.path.split(__file__)[0], config_filename)
        self.config = ConfigParser(allow_no_value=True)
        self.load_config(self.filename)

    def load_config(self, config_filename):
        if not os.path.exists(config_filename):
            raise Exception("%s file does not exist. \n" % config_filename)

        self.config.read(config_filename)

    def get_value(self, section, option):
        return self.config[section][option]

    def set_value(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][option] = str(value)

        if not hasattr(self, section):
            setattr(self, section)
        current_section = getattr(self, section)
        setattr(current_section, option, value)

    def check_value_exist(self, section, option):
        value = self.get_value(section, option)
        if not value:
            return value
        else:
            return False

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
            print("Saved Config : " + self.filename)

    def get_sections(self):
        return self.config.sections()