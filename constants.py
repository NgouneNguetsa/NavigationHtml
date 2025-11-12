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
from urllib.parse import urljoin
import win32api
import win32con

def on_suspend():
    exit(0)

win32api.SetConsoleCtrlHandler(on_suspend, True)

class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, screenHeight = pyautogui.size()
    VERSION_REACTIVE = False

    tl_group = [
            ["nobadnovel","shanghaifantasy","shinningnoveltranslations"], # First research method - First case
            ["brightnovels","otakutl"], # First research method - Second case
            ["botitranslation","zkytl"] # Third research method
        ]

    def InitVar():
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