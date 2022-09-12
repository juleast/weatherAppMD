# import socket to make a test socket connection
import socket


# class that contains tools to check various conditions of the current environment
class internet:
    def __init__(self, host="8.8.8.8", port=53, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout

    def check(self):
        # checks if there is an active internet connection
        try:
            socket.setdefaulttimeout(self.timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            return True
        except socket.error as ex:
            print(ex)
            return False
