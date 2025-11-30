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
        subdirectory = next((sub for sub in Constante.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)),None)

        if subdirectory:
            Constante.imagesPrevButton = [
                                os.path.join(subdirectory, f)
                                for f in os.listdir(subdirectory)
                                if f.lower().endswith(".png") and f.startswith("PreviousChapterButton")
                            ]

            Constante.imagesNextButton = [
                                os.path.join(subdirectory, f)
                                for f in os.listdir(subdirectory)
                                if f.lower().endswith(".png") and f.startswith("NextChapterButton")
                            ]
        else:
            raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")