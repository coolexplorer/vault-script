#!/usr/bin/env python3
import argparse
import os
import sys
from art import *
from pick import pick
import pyperclip
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config.config_parser import ConfigParserFactory
from vault.vault_client import VaultClient
from model.vault_config import VaultConfig
from utils.json_util import *
from vault.secret_type import SecretType

parser = argparse.ArgumentParser(prog='vctl',
                                 description='Command Line Interface for Vault')
subparsers = parser.add_subparsers(help='commands', dest='command')

# login command
parser_login = subparsers.add_parser('login')
parser_login.add_argument('-m', '-method', nargs='?', action='store', dest='method', help='Vault login method')
parser_login.add_argument('-a', '-address', nargs='?', action='store', dest='address', help='Vault server address')
parser_login.add_argument('-n', '-namespace', nargs='?', action='store',
                          dest='namespace', help='Vault Asia QE namespace')
parser_login.add_argument('-u', '-username', nargs='?', action='store', dest='username', help='Vault username')

# get command
parser_get = subparsers.add_parser('get')
parser_get.add_argument('-s', '-studio', nargs='?', action='store', dest='studio',
                        help='Secret location - eakr or eac')
parser_get.add_argument('-p', '-path', nargs='?', action='store', dest='path', help='Secret Path')
parser_get.add_argument('-c', '-connect', action='store_true',
                        dest='connect', help='Connect to VM after getting secrets')

# list command
parser_get = subparsers.add_parser('list')
parser_get.add_argument('-s', '-studio', nargs='?', action='store', dest='studio',
                        help='Secret location - eakr or eac')
parser_get.add_argument('-p', '-path', nargs='?', action='store', dest='path', help='Secret Path')
parser_get.add_argument('-c', '-connect', action='store_true',
                        dest='connect', help='Connect to VM after getting secrets')


class VaultCTL(object):
    def __init__(self, args):
        self.args = args
        self.CONFIG_LOGIN_SECTION = 'vault_login'
        self.CONFIG_KV_SECTION = 'vault_kv'
        self.parser = ConfigParserFactory('vault_config.ini')
        self.config = VaultConfig()
        self.get_config()
        self.vault = VaultClient(self.config.address, self.config.namespace)
        self.secret_type = self.check_secret_type(args)

    def login_flow(self):
        self.vault.login(self.config.method, self.config.username)

    def get_flow(self, sub_path=''):
        if not self.vault.is_token_login():
            self.login_flow()

        if sub_path is not '':
            path = self.secret_type.value + '/' + sub_path
        else:
            path = self.args.path
            sub_path = self.get_sub_path(path)

        secret_value = self.vault.get_secret_value(self.config.mount_point, self.config.studio, path)
        print(secret_value)

        if self.secret_type == SecretType.SVC_ACCOUNT:
            secret_obj = json2obj(secret_value)

            print("Password is copied on clip board. Just paste it.")
            pyperclip.copy(secret_obj.password)

            if self.config.connect:
                self.connect_linux_vm(secret_obj.username, sub_path)

    def list_flow(self):
        if not self.vault.is_token_login():
            self.login_flow()
        secret_list = self.vault.get_secret_list(self.config.mount_point, self.config.studio, args.path)

        if self.secret_type is not None and self.config.connect:
            sub_path = self.pick_secret(secret_list)
            self.get_flow(sub_path)
        else:
            print(secret_list)

    def connect_linux_vm(self, username, address):
        if self.config.studio == 'eakr':
            domain = address + '.aaa.ad.ea.com'
        else:
            domain = address
        print("Connect to " + domain)

        try:
            subprocess.call(['ssh', username + '@' + domain])
        except Exception as e:
            print("Connection Terminated. - " + str(e))

    def get_config(self):
        self.config.method = self.parser.get_value(self.CONFIG_LOGIN_SECTION, 'method')
        self.config.address = self.parser.get_value(self.CONFIG_LOGIN_SECTION, 'address')
        self.config.username = self.parser.get_value(self.CONFIG_LOGIN_SECTION, 'username')
        self.config.namespace = self.parser.get_value(self.CONFIG_LOGIN_SECTION, 'namespace')
        self.config.studio = self.parser.get_value(self.CONFIG_KV_SECTION, 'studio')
        self.config.mount_point = self.parser.get_value(self.CONFIG_KV_SECTION, 'mount_point')

        if self.args.command == 'login':
            if self.args.method is not None:
                self.config.method = self.args.method

            if self.args.address is not None:
                self.config.address = self.args.address

            if self.args.username is not None:
                self.config.username = self.args.username

            if self.args.namespace is not None:
                self.config.namespace = self.args.namespace

        if self.args.command == 'list' or self.args.command == 'get':
            if self.args.studio is not None:
                self.config.studio = self.args.studio

            if self.args.connect is not None:
                self.config.connect = self.args.connect

    def pick_secret(self, secret_list):
        title = 'Please choose secret (ENTER to continue) : '
        selected, index = pick(secret_list, title)
        return selected

    def check_secret_type(self, args):
        try:
            if args.command != "login":
                values = args.path.split("/")
                return SecretType(values[0])
            else:
                return None
        except ValueError:
            return None

    def get_sub_path(self, path):
        values = path.split("/")

        if len(values) > 1:
            return values[1]
        else:
            return None


def main(args):
    vctl = VaultCTL(args)

    print(args)

    if args.command == 'login':
        vctl.login_flow()
    elif args.command == 'get':
        vctl.get_flow()
    elif args.command == 'list':
        vctl.list_flow()


if __name__ == '__main__':
    tprint("vctl - VAULT Control CLI", "small")
    if not sys.argv[1:2]:
        print('Unrecognized command')
        parser.print_help()
        exit(1)

    args = parser.parse_args()
    main(args)
