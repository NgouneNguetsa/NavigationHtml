import requests
from bs4 import BeautifulSoup
import keyboard
import pyautogui
import pyperclip
import time
import pygetwindow as gw
import os
from pathlib import Path
import re
import ctypes


class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, _ = pyautogui.size()
    VERSION_REACTIVE = False

    tl_group = [
            ["nobadnovel","shanghaifantasy","shinningnoveltranslations"], # First research method
            ["brightnovels","otakutl"], # Second research method
            ["botitranslation"] # Third research method
        ]

    def InitVal():
        subdirectory = [sub for sub in Constante.folder.iterdir() if sub.is_dir() and "git" not in str(sub)]

        Constante.imagesPrevButton = [
                            os.path.join(subdirectory[0], f)
                            for f in os.listdir(subdirectory[0])
                            if f.lower().endswith(".png") and f.startswith("PreviousChapterButton")
                        ]

        Constante.imagesNextButton = [
                            os.path.join(subdirectory[0], f)
                            for f in os.listdir(subdirectory[0])
                            if f.lower().endswith(".png") and f.startswith("NextChapterButton")
                        ]