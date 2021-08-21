from hashlib import md5

def encriptar(valor:str):
    return (md5(valor.encode('utf-8')).hexdigest())
