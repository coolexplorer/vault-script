import datetime


class BackUpConfig(object):
    def __init__(self, option):
        self.file_path = option.file_path
        self.dir_path = option.dir_path
        self.compress_option = option.compress_option
        self.remote_address = option.remote_address
        self.username = option.username
        self.password = option.password
        self.local_path = option.local_path
        self.remote_path = option.remote_path
        self.copy_mode = "remote"

    def validate_options(self):
        if self.file_path is None:
            raise Exception("No value")
        else:
            self.add_file_name_postfix()

        if self.dir_path is None:
            raise Exception("No value")

        if self.compress_option is None:
            self.compress_option = True

        if self.remote_address is None:
            self.copy_mode = "local"
            self.remote_address = "apseo-qe-test2"

        if self.username is None:
            self.username = "eass-build"

        if self.password is None:
            self.password = 'Welcome2ea!!'

        if self.local_path is None:
            self.local_path = self.file_path

        if self.remote_path is None:
            self.remote_path = "/home/eass-build"

    def add_file_name_postfix(self):
        name = self.file_path.replace(".tar.gz", "")
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y%m%d_%H%M%S")
        print(formatted_date)
        self.file_path = name + "_" + formatted_date + ".tar.gz"