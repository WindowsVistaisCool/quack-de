from os import path

def isDev():
    return path.exists("../dev") or True
