import keyboard
import pyautogui
import time
import os
from pathlib import Path
import re
import ctypes
import threading
import signal

class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, screenHeight = pyautogui.size()
    BLOG_TEXT_THRESHOLD = 2500 # Regarde si le blog a plus de 2500 caracteres avant de copier le lien
    ARBITRARY_LARGEST_CHAPTER = 2000 # Quand le programme test les liens, regarde si la valeur n'est pas supérieure à 2000 chapitres
    navigators_list = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe","brave.exe", "safari.exe"]
    globalListener_disabled = threading.Event()
    pauseResumeListener_disabled = threading.Event()
    interrupt_handler = threading.Event()
    reload_handler = threading.Event()
    test_handler = threading.Event()
    tl_group = []
    tl_group_index = []
    ADD = False
    REMOVE = True

    def EnableGlobalListener():
        Constante.globalListener_disabled.clear()

    def DisableGlobalListener():
        Constante.globalListener_disabled.set()

    def EnablePauseResumeListener():
        Constante.pauseResumeListener_disabled.clear()

    def DisablePauseResumeListener():
        Constante.pauseResumeListener_disabled.set()
        
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
        signal.signal(signal.SIGINT,Constante.ThreadInterruption)

        with open(fr"{Constante.folder}/translationgroups.txt","rb") as f:
            for s in f:
                s = s.decode().strip()
                if not s.startswith("#") and s != "":
                    ind = f.tell()
                    Constante.tl_group_index.append(ind)
                    Constante.tl_group.append(s.split(","))

        subdirectory = next((sub for sub in Constante.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)),None)

        Constante.rename_chapter_buttons(subdirectory)

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
        
        if len(Constante.imagesPrevButton) != len(Constante.imagesNextButton):
            pyautogui.alert("Image Next/Previous Button a rajouté")
            os._exit(0)

    def rename_chapter_buttons(directory_path):
        if not os.path.isdir(directory_path):
            raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")

        os.chdir(directory_path)
        files = os.listdir('.')

        next_pattern = re.compile(r'^NextChapterButton(\d+)')
        existing_numbers = [0]

        for f in files:
            match = next_pattern.match(f)

            if match:
                existing_numbers.append(int(match.group(1)))

        current_number = max(existing_numbers) + 1

        unprocessed_files = [
            f for f in files 
            if os.path.isfile(f) 
            and not f.startswith("NextChapterButton") 
            and not f.startswith("PreviousChapterButton")
        ]

        unprocessed_files.sort(key=os.path.getmtime)

        if not unprocessed_files:
            return

        for i in range(0, len(unprocessed_files), 2):
            file_next = unprocessed_files[i]
            ext_next = os.path.splitext(file_next)[1]
            new_name_next = f"NextChapterButton{current_number}{ext_next}"
            
            os.rename(file_next, new_name_next)

            if i + 1 < len(unprocessed_files):
                file_prev = unprocessed_files[i + 1]
                ext_prev = os.path.splitext(file_prev)[1]
                new_name_prev = f"PreviousChapterButton{current_number}{ext_prev}"
                
                os.rename(file_prev, new_name_prev)

            else:
                pyautogui.alert("Image Next/Previous Button a rajouté")
                os._exit(0)

            current_number += 1

    def update_tl_group(tl_group,index,addremove):
        buffer = open(fr"{Path(__file__).parent}/translationgroups.txt",'r').read()

        new_file = ""
        if index < len(Constante.tl_group) - 1 and addremove == Constante.ADD:
            new_file = buffer[:Constante.tl_group_index[index]-(3*(index+1))] + f",{tl_group}" + buffer[Constante.tl_group_index[index]-(3*(index+1)):]
        
        elif index < len(Constante.tl_group) - 1 and addremove == Constante.REMOVE:
            index_to_delete = Constante.tl_group[index].index(tl_group)
            new_string = ",".join(Constante.tl_group[index][:index_to_delete])
            new_string = new_string + "," + ",".join(Constante.tl_group[index][index_to_delete+1:]) if index_to_delete != len(Constante.tl_group[index])-1 else new_string

            new_file = buffer[:Constante.tl_group_index[index]-(3*(index+1)) - len(",".join(Constante.tl_group[index]))] + new_string + buffer[Constante.tl_group_index[index]-(3*(index+1)):]
        
        elif index == len(Constante.tl_group) - 1:
            new_file = buffer[:Constante.tl_group_index[index]-2] + f",{tl_group}"
        
        else:
            pyautogui.alert("Il y a eu un problème dans le code")

        open(fr"{Path(__file__).parent}/translationgroups.txt",'w').write(new_file)

        Constante.reload_tl_group_list()

    def reload_tl_group_list():
        Constante.reload_handler.set()
        Constante.tl_group_index.clear()
        Constante.tl_group.clear()
        
        with open(fr"{Constante.folder}/translationgroups.txt","rb") as f:
            for s in f:
                s = s.decode().strip()
                
                if not s.startswith("#") and s != "":
                    ind = f.tell()
                    Constante.tl_group_index.append(ind)
                    Constante.tl_group.append(s.split(","))

        subdirectory = next((sub for sub in Constante.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)),None)

        Constante.rename_chapter_buttons(subdirectory)

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
        
        if len(Constante.imagesPrevButton) != len(Constante.imagesNextButton):
            pyautogui.alert("Image Next/Previous Button a rajouté")
            os._exit(0)

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")