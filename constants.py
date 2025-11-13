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
from datetime import date, timedelta

class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, screenHeight = pyautogui.size()
    VERSION_REACTIVE = False
    BLOG_TEXT_THRESHOLD = 1000 # Regarde si le blog a plus de 1000 caracteres avant de copier le lien

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