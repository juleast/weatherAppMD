# imports
from json import dump
from json import load
from os import mkdir


# class that has methods to save user data
class rw():
    def __init__(self):
        self.filepath = "./data/userdata.json"

    # writes collected data into a json file
    def write(self, locs, unit):
        loc = ""
        # compares default to written variables to determine which data will be written
        if locs[0] == locs[1]:
            loc = locs[0]
        else:
            loc = locs[1]
        data = {
            'location': loc,
            'unit': unit
        }
        # multiple try and catch statements to avoid possible errors
        try:
            with open(self.filepath, 'w') as savefile:
                dump(data, savefile)
        except OSError:
            try:
                mkdir("./data")
                self.write(locs, unit)
            except OSError as ex:
                print(ex)

    # reads json user data and returns it in an organized way
    def read(self):
        with open(self.filepath, 'r') as savefile:
            userdata = load(savefile)
        return userdata
