import optparse
import os
import sys
from shutil import copyfile
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config.backup_config import BackUpConfig
from utils.compress_utils import CompressUtil
from utils.scp_util import SCPUtil


parser = optparse.OptionParser()
parser.add_option('-f', '--file', action='store', dest='file_path',
                  type="string", help="tar file name")
parser.add_option('-d', '--dir', action='store', dest='dir_path',
                  type="string", help="compressed directory path")
parser.add_option('-c', '--compass', action="store_true", dest='compress_option',
                  help="Compress files")
parser.add_option('-x', '--extract', action="store_false", dest='compress_option',
                  help="Compress files")
parser.add_option('-a', '--address', action="store", dest='remote_address',
                  type="string", help="remote address")
parser.add_option('-u', '--user', action="store", dest='username',
                  type="string", help="remote host user name")
parser.add_option('-p', '--password', action="store", dest='password',
                  type="string", help="remote host user password")
parser.add_option('-l', '--local', action="store", dest='local_path',
                  type="string", help="local path of send file")
parser.add_option('-r', '--remote', action="store", dest='remote_path',
                  type="string", help="remote path of send file")


def main(option):
    config = BackUpConfig(option)
    config.validate_options()
    tar_file(config)
    copy_file(config)


def tar_file(config):
    compress = CompressUtil(config.file_path, config.compress_option)
    if config.compress_option:
        compress.compress(config.dir_path)
    else:
        compress.extract(config.dir_path)
    compress.close()


def copy_file(config):
    if config.copy_mode == "remote":
        scp_manager = SCPUtil()
        scp_manager.create_ssh_client(config.remote_address, config.username, config.password)
        scp_manager.send_command("mkdir -p " + config.remote_path)

        try:
            scp_manager.send_file(config.local_path, config.remote_path)
        except Exception as e:
            print("SCP Send File Terminated. - " + str(e))

        scp_manager.close_ssh_client()
    else:
        copyfile(config.local_path, config.remote_path)


if __name__ == '__main__':
    option, args = parser.parse_args()
    main(option)
