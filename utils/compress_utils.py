import tarfile
import os


class CompressUtil(object):
    def __init__(self, file_name, compress_option):
        self.file_name = file_name
        if compress_option:
            self.tar_instance = tarfile.open(self.file_name, "w:gz")
        else:
            self.tar_instance = tarfile.open(self.file_name, "r:gz")

    def compress(self, dir_path):
        self.tar_instance.add(dir_path,  arcname=os.path.basename(dir_path), recursive=True, exclude=None)

    def extract(self, dir_path):
        for tarInfo in self.tar_instance:
            self.tar_instance.extract(tarInfo, dir_path)

    def close(self):
        self.tar_instance.close()

    def __del__(self):
        self.tar_instance.close()

