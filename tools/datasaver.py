# imports
from json import dump


# class that has methods to save user data
class save():
    def __init__(self, data):
        self.data = data

    def write(self):
        with open('./data/userdata.json', 'w') as savefile:
            dump(self.data, savefile)
        print("yee")
