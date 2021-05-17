import os
import hvac
from getpass import getpass

from hvac.exceptions import *


class VaultClient(object):
    def __init__(self, address='', namespace=''):
        self.address = address
        self.client = hvac.Client(url=self.address)
        self.token_path = ".vault-token"
        self.read_token_file(self.token_path)
        self.namespace = namespace

    def login(self, method, username):
        if not self.is_valid_token():
            if method == "okta":
                self.okta_login(username)
            else:
                raise ValueError
        else:
            self.token_login(self.client.token)
            print("Token is still valid.")

    def token_login(self, token):
        self.client = hvac.Client(url=self.address, namespace=self.namespace, token=token)

    def okta_login(self, username):
        password_prompt = 'Please enter your password for the Okta authentication backend: '
        okta_password = getpass(prompt=password_prompt)

        try:
            self.client.auth.okta.login(
                username=username,
                password=okta_password,
            )
            self.token_login(self.client.token)

            if self.is_valid_token():
                self.write_token_file(self.token_path)
            print("Successfully logged in!!!!!")
        except InvalidRequest as e:
            print("[Invalid Request Exception] : Request failed - " + str(e))
            exit(1)

    def get_token(self):
        return self.client.token

    def set_token(self, token):
        self.client.token = token

    def is_token_login(self):
        return self.client._adapter.namespace is not None

    def is_valid_token(self):
        return self.client.is_authenticated()

    def read_token_file(self, file_path):
        if os.path.exists(file_path):
            print("Read token file")
            with open(file_path, "r") as f:
                token = f.readline()
            self.client.token = token

    def write_token_file(self, file_path):
        print("Write token file")
        with open(file_path, "w") as f:
            f.write(self.client.token)

    def set_namespace(self, namespace):
        self.namespace = namespace

    def get_secret_list(self, mount_point, studio, path):
        try:
            return self.client.secrets.kv.v2.list_secrets(mount_point=mount_point, path=(studio + '/' + path))['data']['keys']
        except InvalidPath as e:
            print("[Invalid Path Exception] : Path is invalid - " + str(e))
            exit(1)

    def get_secret_value(self, mount_point, studio, path):
        try:
            return self.client.secrets.kv.v2.read_secret_version(mount_point=mount_point, path=(studio + '/' + path))['data']['data']
        except InvalidPath as e:
            print("[Invalid Path Exception] : Path is invalid - " + str(e))
            exit(1)

