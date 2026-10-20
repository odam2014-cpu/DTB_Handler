import DTB_Cfg
import secrets
import string
import hashlib

def get_token():
    _ln = DTB_Cfg.cfg.gi("TokenLenght")
    characters = string.digits
    tk = ''.join(secrets.choice(characters) for _ in range(_ln))
    return tk

def get_hash(_input):
    input_hash = hashlib.sha256(_input.encode('utf-8')).hexdigest()
    return input_hash
