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
from datetime import date, timedelta
import threading
from pynput.keyboard import Key, Listener

class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, screenHeight = pyautogui.size()
    BLOG_TEXT_THRESHOLD = 2500 # Regarde si le blog a plus de 2500 caracteres avant de copier le lien
    listener_enabled = True

    tl_group = [
            ["nobadnovel","shanghaifantasy","shiningnoveltranslations"], # First research method - First case
            ["brightnovels","otakutl","zkytl","breaknovel"], # First research method - Second case
            ["botitranslation","dasuitl","foxaholic","readrift"] # Third research method
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