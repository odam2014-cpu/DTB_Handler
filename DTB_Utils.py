import DTB_Cfg
import random
import hashlib

def get_token():
    _ln = DTB_Cfg.cfg.gi("TokenLenght")
    tk = ""
    while len(tk) < _ln:
        tk = tk + str(random.randint(0, 9))
    return tk

def get_hash(_input):
    input_hash = hashlib.sha256(_input.encode('utf-8')).hexdigest()
    return input_hash
