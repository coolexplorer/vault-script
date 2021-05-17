from enum import Enum


class SecretType(Enum):
    DB_ACCOUNT = 'db_account'
    SSH = 'ssh'
    SVC_ACCOUNT = 'svc_account'
    TOKEN = 'token'
    TSL = 'tsl'
    WEBHOOK = 'webhook'
