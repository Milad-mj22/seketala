import os



def check_server():
    SERVER = None
    SERVER = os.getenv('SERVER')
    if SERVER is None:
        SERVER = 'False'
    SERVER = SERVER.strip().lower() in ("true", "1", "yes", "on")
    return SERVER