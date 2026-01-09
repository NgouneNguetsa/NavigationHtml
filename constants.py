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
from pynput.keyboard import Key, KeyCode, Listener
import signal

class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, screenHeight = pyautogui.size()
    BLOG_TEXT_THRESHOLD = 2500 # Regarde si le blog a plus de 2500 caracteres avant de copier le lien
    ARBITRARY_LARGEST_CHAPTER = 2000 # Quand le programme test les liens, regarde si la valeur n'est pas supérieure à 2000 chapitres
    globalListener_disabled = threading.Event()
    interrupt_handler = threading.Event()
    tl_group = []
    tl_group_index = []

    def EnableGlobalListener():
        Constante.globalListener_disabled.clear()

    def DisableGlobalListener():
        Constante.globalListener_disabled.set()
        
    def ThreadInterrupt(self):
        time.sleep(2)
        try:
            keyboard.unblock_key("left")
        except KeyError:
            pass
        
        try:
            keyboard.unblock_key("right")
        except KeyError:
            pass

        os._exit(0)

    def InitVar():
        signal.signal(signal.SIGINT,Constante.ThreadInterrupt)

        with open(fr"{Constante.folder}/translationgroups.txt","rb") as f:
            for s in f:
                s = s.decode().strip()
                if not s.startswith("#") and s != "":
                    ind = f.tell()
                    Constante.tl_group_index.append(ind)
                    Constante.tl_group.append(s.split(","))

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
        
        if len(Constante.imagesPrevButton) != len(Constante.tl_group[-2]):
            pyautogui.alert("Groupe de traduction a rajouté")
        
    def update_tl_group(tl_group,index):

        buffer = open(fr"{Path(__file__).parent}/translationgroups.txt",'r').read()

        new_file = ""
        if index < len(Constante.tl_group) - 1:
            new_file = buffer[:Constante.tl_group_index[index]-(3*(index+1))] + f",{tl_group}" + buffer[Constante.tl_group_index[index]-(3*(index+1)):]
        elif index == len(Constante.tl_group) - 1:
            new_file = buffer[:Constante.tl_group_index[index]-2] + f",{tl_group}"
        else:
            pyautogui.alert("Il y a eu un problème dans le code")

        open(fr"{Path(__file__).parent}/translationgroups.txt",'w').write(new_file)
        
        Constante.tl_group_index.clear()
        Constante.tl_group.clear()
        with open(fr"{Constante.folder}/translationgroups.txt","rb") as f:
            for s in f:
                s = s.decode().strip()
                if not s.startswith("#") and s != "":
                    ind = f.tell()
                    Constante.tl_group_index.append(ind)
                    Constante.tl_group.append(s.split(","))

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")