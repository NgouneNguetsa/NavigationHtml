import keyboard
import pyautogui
import time
import os
from pathlib import Path
import re
import ctypes
import threading
import signal

from DirectoryManagement import Directory

class Constante:

    user32 = ctypes.windll.user32
    BLOG_TEXT_THRESHOLD = 2600 # Regarde si le blog a plus de 2600 caracteres avant de copier le lien
    ARBITRARY_LARGEST_CHAPTER = 2000 # Quand le programme test les liens, regarde si la valeur n'est pas supérieure à 2000 chapitres
    ARBITRARY_SECONDS_BEFORE_DENYING_SEARCH = 10
    navigatorsList = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe","brave.exe", "safari.exe"]
    translatorsGroup = []
    lastAddedTranslatorGroup = ""

    globalListenerDisabled = threading.Event()
    pauseResumeListenerDisabled = threading.Event()

    interruptHandler = threading.Event()
    reloadHandler = threading.Event()
    testHandler = threading.Event()
    displayHandler = threading.Event()

    ADD = False
    REMOVE = True

    screenWidth, screenHeight = pyautogui.size()
    screenRegion = [0, int(0.1 * screenHeight), screenWidth, int(0.9 * screenHeight)]
    screenYOffset = screenRegion[1]
    halfScreenHeight = screenHeight / 2
    halfScreenWidth = screenWidth / 2
    minScreenWidth = 0.989 * screenWidth
    minScreenHeight = 0.35 * screenHeight
    limitScreenWidth = 0.95 * screenWidth

    def EnableGlobalListener():
        Constante.globalListenerDisabled.clear()

    def DisableGlobalListener():
        Constante.globalListenerDisabled.set()

    def EnablePauseResumeListener():
        Constante.pauseResumeListenerDisabled.clear()

    def DisablePauseResumeListener():
        Constante.pauseResumeListenerDisabled.set()
        
    def ThreadInterruption(self):
        time.sleep(5)

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
        signal.signal(signal.SIGINT, Constante.ThreadInterruption)

        with open(fr"{Directory.folder}/translationgroups.txt", "r") as file:
            groups = []

            for string in file:
                string = string.strip()

                if not string.startswith("#") and string != "":
                    
                    for translator in string.split(","):
                        groups.append(translator)

                elif string.startswith("#"):
                    
                    if len(groups) > 0:
                        Constante.translatorsGroup.append([translator for translator in groups])
                        groups.clear()

            Constante.translatorsGroup.append([translator for translator in groups])

        Directory.processSingleMissingGroup(Directory.subdirectory)

        if Directory.subdirectory:
            Constante.imagesPrevButton = [
                                os.path.join(Directory.subdirectory, file)
                                for file in os.listdir(Directory.subdirectory)
                                if file.lower().endswith(".png") and file.startswith("PreviousChapterButton")
                            ]

            Constante.imagesNextButton = [
                                os.path.join(Directory.subdirectory, file)
                                for file in os.listdir(Directory.subdirectory)
                                if file.lower().endswith(".png") and file.startswith("NextChapterButton")
                            ]
            
        else:
            raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")
        
        if len(Constante.imagesPrevButton) != len(Constante.imagesNextButton):
            pyautogui.alert("Image Next/Previous Button a rajouté")
            os._exit(0)

    def reloadTranslatorsGroupList():
        Constante.reloadHandler.set()
        Constante.translatorsGroup.clear()
        
        with open(fr"{Directory.folder}/translationgroups.txt", "r") as file:
            groups = []

            for string in file:
                string = string.strip()

                if not string.startswith("#") and string != "":
                    
                    for translator in string.split(","):
                        groups.append(translator)

                elif string.startswith("#"):
                    
                    if len(groups) > 0:
                        Constante.translatorsGroup.append([translator for translator in groups])
                        groups.clear()

            Constante.translatorsGroup.append([translator for translator in groups])

        Directory.subdirectory = next((sub for sub in Directory.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)), None)

        if Directory.subdirectory:
            Constante.imagesPrevButton = [
                                os.path.join(Directory.subdirectory, file)
                                for file in os.listdir(Directory.subdirectory)
                                if file.lower().endswith(".png") and file.startswith("PreviousChapterButton")
                            ]

            Constante.imagesNextButton = [
                                os.path.join(Directory.subdirectory, file)
                                for file in os.listdir(Directory.subdirectory)
                                if file.lower().endswith(".png") and file.startswith("NextChapterButton")
                            ]
        else:
            raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")
        
        if len(Constante.imagesPrevButton) != len(Constante.imagesNextButton):
            pyautogui.alert("Image Next/Previous Button a rajouté")
            os._exit(0)

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")