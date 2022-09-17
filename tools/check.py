# imports
import socket
from os.path import exists


# class that contains a method to ping a popular dns address to check for a valid internet
class internet:
    def __init__(self, host="8.8.8.8", port=53, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout

    def ping(self):
        # checks if there is an active internet connection
        try:
            socket.setdefaulttimeout(self.timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            return True
        except socket.error as ex:
            print(ex)
            return False


# class that contains a method to check if a current save data exists
class filecheck:
    def __init__(self):
        self.filepath = "./data/userdata.json"

    def file(self):
        return exists(self.filepath)
