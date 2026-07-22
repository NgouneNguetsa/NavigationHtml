import keyboard
import pyautogui
import time
import os
from pathlib import Path
import re
import ctypes
import threading
import signal
import pyperclip

from DisplayManagement import Display, focusWindow
from UrlManagement import Url

class Constante:

    user32 = ctypes.windll.user32
    folder = Path(__file__).parent
    screenWidth, screenHeight = pyautogui.size()
    BLOG_TEXT_THRESHOLD = 2500 # Regarde si le blog a plus de 2500 caracteres avant de copier le lien
    ARBITRARY_LARGEST_CHAPTER = 2000 # Quand le programme test les liens, regarde si la valeur n'est pas supérieure à 2000 chapitres
    navigatorsList = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe","brave.exe", "safari.exe"]
    globalListenerDisabled = threading.Event()
    pauseResumeListenerDisabled = threading.Event()
    interruptHandler = threading.Event()
    reloadHandler = threading.Event()
    testHandler = threading.Event()
    displayHandler = threading.Event()
    translatorsGroup = []
    ADD = False
    REMOVE = True

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

        with open(fr"{Constante.folder}/translationgroups.txt", "r") as file:
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


        subdirectory = next((sub for sub in Constante.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)), None)

        renameChapterButtons(subdirectory)

        if subdirectory:
            Constante.imagesPrevButton = [
                                os.path.join(subdirectory, file)
                                for file in os.listdir(subdirectory)
                                if file.lower().endswith(".png") and file.startswith("PreviousChapterButton")
                            ]

            Constante.imagesNextButton = [
                                os.path.join(subdirectory, file)
                                for file in os.listdir(subdirectory)
                                if file.lower().endswith(".png") and file.startswith("NextChapterButton")
                            ]
            
        else:
            raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")
        
        if len(Constante.imagesPrevButton) != len(Constante.imagesNextButton):
            pyautogui.alert("Image Next/Previous Button a rajouté")
            os._exit(0)

    def updateTranslatorsGroup(translatorGroup : str, index : int, addremove : bool):
            filePath = os.path.join(Constante.folder, "translationgroups.txt")
            maxColumns = 130

            with open(filePath, 'r', encoding='utf-8') as file:
                lines = file.read().splitlines()

            headerIndices = [
                i for i, line in enumerate(lines) 
                if line.strip().startswith("#")
            ]

            if index >= len(headerIndices):
                pyautogui.alert("L'index demandé dépasse les groupes configurés.")
                return

            targetHeaderIndex = headerIndices[index]
            nextHeaderIndex = len(lines)

            for headerIndex in headerIndices:
                if headerIndex > targetHeaderIndex:
                    nextHeaderIndex = headerIndex
                    break

            if addremove == Constante.ADD:
                targetLineIndex = nextHeaderIndex - 1

                while targetLineIndex > targetHeaderIndex and lines[targetLineIndex].strip() == "":
                    targetLineIndex -= 1

                if targetLineIndex == targetHeaderIndex:
                    lines.insert(targetHeaderIndex + 1, translatorGroup)

                else:
                    lastDataLine = lines[targetLineIndex].strip()
                    potentialtranslatorGroup = f",{translatorGroup}"
                    
                    if len(lastDataLine) + len(potentialtranslatorGroup) > maxColumns:
                        lines.insert(targetLineIndex + 1, translatorGroup)

                    else:
                        lines[targetLineIndex] = lastDataLine + potentialtranslatorGroup

            elif addremove == Constante.REMOVE:

                for idx in range(targetHeaderIndex + 1, nextHeaderIndex):

                    if translatorGroup in lines[idx]:
                        elements = [element.strip() for element in lines[idx].split(",") if element.strip()]

                        if translatorGroup in elements:
                            elements.remove(translatorGroup)
                            
                            if not elements:
                                lines.pop(idx)

                            else:
                                lines[idx] = ",".join(elements)
                            
                            break

            else:
                pyautogui.alert("Il y a eu un problème dans le code")
                return

            with open(filePath, 'w', encoding='utf-8') as file:
                file.write("\n".join(lines) + "\n")

            Constante.reloadTranslatorsGroupList()

    def reloadTranslatorsGroupList():
        Constante.reloadHandler.set()
        Constante.translatorsGroup.clear()
        
        with open(fr"{Constante.folder}/translationgroups.txt", "r") as file:
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

        subdirectory = next((sub for sub in Constante.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)), None)

        renameChapterButtons(subdirectory)

        if subdirectory:
            Constante.imagesPrevButton = [
                                os.path.join(subdirectory, file)
                                for file in os.listdir(subdirectory)
                                if file.lower().endswith(".png") and file.startswith("PreviousChapterButton")
                            ]

            Constante.imagesNextButton = [
                                os.path.join(subdirectory, file)
                                for file in os.listdir(subdirectory)
                                if file.lower().endswith(".png") and file.startswith("NextChapterButton")
                            ]
        else:
            raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")
        
        if len(Constante.imagesPrevButton) != len(Constante.imagesNextButton):
            pyautogui.alert("Image Next/Previous Button a rajouté")
            os._exit(0)

    def changeTranslatorGroupsList():
        os.system("cls")
        flushStdin()

        methodDict = {1 : "First research method - First case", 
                      2 : "First research method - Second case", 
                      3 : "Second research method", 
                      4 : "To skip"}

        focusWindow(Display.browser["handle"])
        Url.copyPaste()
        url = pyperclip.paste()
        pyautogui.hotkey('alt','tab')

        partUrl = url.split("/")[2]
        if partUrl == "":
            translatorGroup = input("\nQuel est le groupe de traduction (symbolique)?\n")
            translatorGroup = translatorGroup.lower()

            index = input("\nDans quelle méthode de recherche voulez-vous le mettre ?"
                         f"\n{methodDict[3]} (3)"
                         f"\n{methodDict[4]} (4)"
                          "\nTapez un chiffre (3 ou 4) : ")
            intIndex = int(index)

            while intIndex < 3 or intIndex > 4:
                index = input("Entrée invalide. Tapez un nouveau chiffre (3 ou 4) : ")
                intIndex = int(index)

            Constante.updateTranslatorsGroup(translatorGroup, intIndex - 1, Constante.ADD)

        else:
            translatorGroup = ""
            if partUrl.count(".") > 1:
                indexFirstPoint = partUrl.index(".")
                indexSecondPoint = partUrl.index(".", indexFirstPoint + 1)
                translatorGroup = partUrl[indexFirstPoint + 1 : indexSecondPoint]

            else:
                translatorGroup = partUrl[ : partUrl.index(".")]

            groupIndex = -1
            found = False
            for n in range(len(Constante.translatorsGroup)):

                for group in Constante.translatorsGroup[n]:

                    if translatorGroup == group:
                        groupIndex = n
                        found = True
                        break

                if found == True:
                    break

            searchAndChangeTranslatorGroup(methodDict, translatorGroup, groupIndex)

        Display.pauseStateMessage()
        print("\nNouvelle liste de groupe de traduction\n")
        Display.showTranslatorGroupsList()
        
        return False

def renameChapterButtons(directoryPath : Path):

    if not os.path.isdir(directoryPath):
        raise FileNotFoundError("Je n'ai pas l'air de trouver le dossier nécessaire")

    os.chdir(directoryPath)
    files = os.listdir('.')

    nextPattern = re.compile(r'^NextChapterButton(\d+)')
    existingNumbers = [0]

    for file in files:
        match = nextPattern.match(file)

        if match:
            existingNumbers.append(int(match.group(1)))

    currentNumber = 0
    currentNumbers = list()

    if len(existingNumbers) != max(existingNumbers):
        currentNumbers = list(set(range(existingNumbers[0], existingNumbers[-1] + 1)) - set(existingNumbers))
    
    else:
        currentNumber = max(existingNumbers) + 1

    unprocessedFiles = [
        file for file in files 
        if os.path.isfile(file) 
        and not file.startswith("NextChapterButton") 
        and not file.startswith("PreviousChapterButton")
    ]

    unprocessedFiles.sort(key=os.path.getmtime)

    if not unprocessedFiles:
        return

    if currentNumbers:
        
        for i in range(0, len(unprocessedFiles), 2):
            nextFile = unprocessedFiles[i]
            extension = os.path.splitext(nextFile)[1]
            newNameNextFile = f"NextChapterButton{currentNumbers[i / 2]}{extension}"
            
            os.rename(nextFile, newNameNextFile)

            if i + 1 < len(unprocessedFiles):
                previousFile = unprocessedFiles[i + 1]
                extension = os.path.splitext(previousFile)[1]
                newNamePreviousFile = f"PreviousChapterButton{currentNumbers[i / 2]}{extension}"
                
                os.rename(previousFile, newNamePreviousFile)

            else:
                pyautogui.alert("Image Next/Previous Button a rajouté")
                os._exit(0)

    else:

        for i in range(0, len(unprocessedFiles), 2):
            nextFile = unprocessedFiles[i]
            extension = os.path.splitext(nextFile)[1]
            newNameNextFile = f"NextChapterButton{currentNumber}{extension}"
            
            os.rename(nextFile, newNameNextFile)

            if i + 1 < len(unprocessedFiles):
                previousFile = unprocessedFiles[i + 1]
                extension = os.path.splitext(previousFile)[1]
                newNamePreviousFile = f"PreviousChapterButton{currentNumber}{extension}"
                
                os.rename(previousFile, newNamePreviousFile)

            else:
                pyautogui.alert("Image Next/Previous Button a rajouté")
                os._exit(0)

            currentNumber += 1

def searchAndChangeTranslatorGroup(methodDict : dict, translatorGroup : str, groupIndex : int):
    flushStdin()

    if groupIndex != -1:
        choice = input("Voulez-vous enlever (r) ou changer (c) le groupe de traduction ?"
                       "\nTapez une lettre (r/c) : ")
        choice = choice.lower()

        if choice == "r":
            validation = input(f"\nVoulez-vous retirer {translatorGroup} de {methodDict[groupIndex + 1]} ?"
                                "\nTapez y/n : ")
            validation = validation.lower()

            while validation != "y" or validation != "n":
                validation = input("Entrée invalide. Tapez y/n : ")
                validation = validation.lower()

            if validation == "y":
                Constante.updateTranslatorsGroup(translatorGroup, groupIndex, Constante.REMOVE)
        
        elif choice == "c":
            matchingPairs = [(key, value) for key, value in methodDict.items() if key != (groupIndex + 1)]

            print(f"\nDans quelle méthode de recherche voulez-vous changer {translatorGroup} ?")
            for key, value in matchingPairs:
                print(f"{value} ({key})")

            otherIndex = input("Tapez un chiffre (1-4) : ")
            intOtherIndex = int(otherIndex)

            while (intIndex == intOtherIndex) or intOtherIndex < 1 or intOtherIndex > 4:
                otherIndex = input("Entrée invalide. Tapez un chiffre (1-4) : ")
                intOtherIndex = int(otherIndex)

            Constante.updateTranslatorsGroup(translatorGroup, groupIndex, Constante.REMOVE)
            Constante.updateTranslatorsGroup(translatorGroup, intOtherIndex - 1, Constante.ADD)

        else:
            searchAndChangeTranslatorGroup(methodDict, translatorGroup, groupIndex)

    else:
        index = input(f"\nDans quelle méthode de recherche voulez-vous ajouter {translatorGroup} ?"
                      f"\n{methodDict[1]} (1)"
                      f"\n{methodDict[2]} (2)"
                      f"\n{methodDict[3]} (3)"
                      f"\n{methodDict[4]} (4)"
                       "\nTapez un chiffre (1-4) : ")
        intIndex = int(index)

        while intIndex < 1 or intIndex > 4:
            index = input("Entrée invalide. Tapez un nouveau chiffre (1-4) : ")
            intIndex = int(index)

        Constante.updateTranslatorsGroup(translatorGroup, intIndex - 1, Constante.ADD)
    
    return

def flushStdin():
    try:
        from msvcrt import kbhit, getch

        while kbhit():
            getch()

    except ImportError:
        import sys, termios

        termios.tcflush(sys.stdin, termios.TCIFLUSH)

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")