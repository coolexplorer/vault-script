import paramiko
from scp import SCPClient, SCPException


class SCPUtil(object):
    def __init__(self):
        self.ssh_client = None

    def create_ssh_client(self, hostname, username, password):
        if self.ssh_client is None:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname=hostname, username=username, password=password)
        else:
            print("SSH client already exist")

    def close_ssh_client(self):
        self.ssh_client.close()

    def send_command(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.readlines()

    def send_file(self, local_path, remote_path):
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(local_path, remote_path, recursive=True, preserve_times=True)
        except SCPException:
            raise Exception(SCPException.message)

    def receive_file(self, remote_path, local_path):
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.get(remote_path, local_path, recursive=True, preserve_times=True)
        except SCPException:
            raise Exception(SCPException.message)
