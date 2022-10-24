# imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.list import IRightBodyTouch
from kivy.lang import Builder

from webbrowser import open as browser

Builder.load_file('dialogcontents.kv')

'''These are classes for popup dialog content_cls'''


# widget for location changer popup
class Picker(MDBoxLayout):
    pass


# widget for weather unit changer popup
class UnitChanger(MDBoxLayout):
    pass


# widget container to house the switch
class RightBox(IRightBodyTouch, MDSwitch):
    pass


# widget for fetch error message popup
class Error(MDBoxLayout):
    pass


# widget for internet error popup
class ConError(MDBoxLayout):
    pass


# widget for gps error popup
class GPSError(MDBoxLayout):
    pass


# widget for loading popup
class GPSLoading(MDBoxLayout):
    pass


# widget for credits popup
class Credits(MDBoxLayout):
    # method to open credit page to background image
    def open_img_credits(self):
        browser(
            "https://www.freepik.com/free-vector/gorgeous-clouds-background-with-blue-sky-design_8562848.htm#query"
            "=weather&position=31&from_view=search")

    def open_dev_credits(self):
        browser("https://www.github.com/juleast")


# widget for support popup
class Support(MDBoxLayout):
    # methods to open page related to support
    def dev_mail(self):
        browser("mailto:joseph15two@gmail.com")

    def privacy(self):
        browser("https://juleast.github.io/PrivacyPolicySW/")

