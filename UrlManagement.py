import re
import pyperclip
import pyautogui
import time
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import threading
import keyboard
from urllib.parse import urljoin

from constants import Constante
from DisplayManagement import Display

class Url:
    methods = [
        lambda url, index, direction: Url.searchAndGoToPage(url, index, direction),
        lambda url, direction: Url.searchAndGoToPage_2ndMethod(url, direction)
    ]

    mapping = {}
    patterns = []

    tentatives = 31
    tentativesTest = 1
    threadsList = []
    urlFound = threading.Event()
    imageFound = threading.Event()
    
    def InitVar():
        Url.updateRegex()

    def testScreenCorners(function):
        def inner(*args, **kwargs):
            try:
                function(*args, *kwargs)

            except pyautogui.FailSafeException:
                pyautogui.FAILSAFE = False
                pyautogui.move(Constante.screenWidth, Constante.screenHeight / 2)
                pyautogui.FAILSAFE = True
                function(*args, *kwargs)

        return inner

    def resetThreadsList():
        Url.threadsList.clear()

    def updateRegex():
        Url.mapping.clear()
        Url.patterns.clear()

        for i, translatorsGroupList in enumerate(Constante.translatorsGroup):
            for translator in translatorsGroupList:
                Url.patterns.append(re.escape(translator))
                Url.mapping[translator] = i  # Associe chaque texte au bon index

        # Compile une seule regex globale
        Url.globalRegex = re.compile("|".join(Url.patterns))

    def getLastSegment(url : str):
        """Retourne la dernière partie de l'URL après le dernier /"""
        
        return url.rstrip("/").split("/")[-1] 

    def modifyChapterNumber(segment : str, prefix : str, chapterNumber : int, suffix : str, extension : str, direction : str):
        """Modifie le numéro selon la direction (next/last) et reconstruit le segment"""
        # En fonction de la direction, on incrémente ou décrémente
        newNumber = chapterNumber + 1 if direction == "next" else chapterNumber - 1

        # Vérification : on évite un numéro de chapitre inférieur à 0
        if newNumber < 0:
            return ""  # On ne traite pas ce cas si le numéro devient invalide

        newSegment = f"{prefix}{newNumber}{suffix}{extension}"
        return newSegment

    def applyRegexAndModify(url : str, pattern : str, groups, direction : str):
        """Applique un pattern à la fin de l'URL et retourne la nouvelle URL (incrémentée ou décrémentée)"""
        
        index = url.find("#")

        if index != -1:
            url = url.replace(url[index:], "")

        segment = Url.getLastSegment(url)
        match = re.search(pattern, segment)

        if not match:
            return ""

        # Extraire les différentes parties capturées
        parts = {name: match.group(i + 1) if i < len(groups) else "" for i, name in enumerate(groups)}

        newSegment = Url.modifyChapterNumber(segment, parts.get("prefix", ""), int(parts.get("number", 1)), parts.get("suffix", ""), parts.get("extension", ""), direction)
        
        if (not newSegment) or (int(parts["number"]) > Constante.ARBITRARY_LARGEST_CHAPTER):
            return ""

        # Recomposer l'URL complète
        base = url[: -len(segment)]

        return urljoin(base, newSegment)

    # --- Tous les handles appellent applyRegexAndModify avec un pattern différent ---
    def handlePrefixNumberSuffixExtension(url : str, direction : str):
        return Url.applyRegexAndModify(url, r"^([a-zA-Z_-]*?)(\d+)(?=-|_[^-]*|)([a-zA-Z0-9_-]*)?([.a-zA-Z]*)?(?:[#a-zA-Z_-]*)?$", ["prefix", "number", "suffix", "extension"], direction)

    def handlePrefixNumber(url : str, direction : str):
        return Url.applyRegexAndModify(url, r"^([a-zA-Z_-]*?)(\d+)(?=[^0-9]|$)(?:.*)$", ["prefix", "number"], direction)

    @testScreenCorners
    def mouseMove(x, y):
        pyautogui.click(x, y)

        yDiff = abs((Constante.screenHeight / 2) - y) if y < (Constante.screenHeight / 2) else 0
        pyautogui.moveTo(0.989*Constante.screenWidth, min(0.83*Constante.screenHeight, Constante.screenHeight - 2*yDiff))            
        time.sleep(2)

        pyautogui.leftClick()
        pyautogui.moveTo(Constante.screenWidth, y)

    @testScreenCorners
    def mouseMoveAlternative(x, y):
        pyautogui.click(x, y)

        pyautogui.moveTo(0.5*Constante.screenWidth, 0.35*Constante.screenHeight)            
        time.sleep(1)

        pyautogui.leftClick()
        pyautogui.moveTo(Constante.screenWidth, y)

    def getUrl(url : str):
        response = None

        try:
            response = requests.get(url)

        except requests.exceptions.RequestException:
            Display.showMajorErrorMessage()
            return Url.getUrl(url)

        return response
    
    def testUrl(url : str, direction : str):
        Constante.testHandler.set()

        urlToTest = True
        
        translatorGroup = url.split("/")[2]
        index = 0

        if translatorGroup.count(".") > 1:
            indexFirstPoint = translatorGroup.index(".")
            indexSecondPoint = translatorGroup.index(".",indexFirstPoint + 1)
            translatorGroup = translatorGroup[indexFirstPoint + 1 : indexSecondPoint]

        else:
            translatorGroup = translatorGroup[ : translatorGroup.index(".")]

        Display.showTestMessage()
        Url.copyPaste()
        newUrl = pyperclip.paste()

        if newUrl != url or Url.tentativesTest >= 3:
            index = len(Constante.translatorsGroup) - 1
            Url.tentativesTest = 0

        else:
            urlToTest = Url.testIndirect(url, direction)

            if urlToTest:
                index += 1
                urlToTest = Url.testDirect(url, direction)

                if urlToTest:
                    index += 1
                    Display.showStatusMessage("Image a rajoutée")
                    Url.tentativesTest = 0

                else:
                    Url.tentativesTest = 0

            else:
                Url.tentativesTest = 0

        Constante.updateTranslatorsGroup(translatorGroup, index, Constante.ADD)
        Url.tentativesTest += 1

        Constante.testHandler.clear()

    def createNewUrl(url : str, direction : str):
        urlParser = url.rstrip("/").split("/")
        dateParser = [element for element in urlParser[ : -1] if element.isdigit()]

        if len(dateParser) == 2:

            if int(dateParser[1]) < int(dateParser[0]):
                dateParser[1] = str(int(dateParser[1]) + 1) if direction == "next" else str(int(dateParser[1]) - 1)
                dateParser[1] = '0'+ dateParser[1] if int(dateParser[1]) < 10 else dateParser[1]

                if int(dateParser[1]) > 12:
                    dateParser[1] = '01'
                    dateParser[0] = str(int(dateParser[0]) + 1)

                elif int(dateParser[1]) < 1:
                    dateParser[1] = '12'
                    dateParser[0] = str(int(dateParser[0]) - 1)

            else:
                dateParser[0] = str(int(dateParser[0]) + 1) if direction == "next" else str(int(dateParser[0]) - 1)
                dateParser[0] = '0'+ dateParser[0] if int(dateParser[0]) < 10 else dateParser[0]

                if int(dateParser[0]) > 12:
                    dateParser[0] = '01'
                    dateParser[1] = str(int(dateParser[1]) + 1)

                elif int(dateParser[0]) < 1:
                    dateParser[0] = '12'
                    dateParser[1] = str(int(dateParser[1]) - 1)

            dateParser.append('/')
            
        elif len(dateParser) == 3:
            dateString = "".join(dateParser)

            day = timedelta(days=1)

            dateObject = date.fromisoformat(dateString)
            dateObject = dateObject + day if direction == "next" else dateObject - day
            dateParser = dateObject.isoformat().split("-")

            dateParser.append('/')

        index = next((i for i, value in enumerate(urlParser) if value.isdigit()), None)

        base = "/".join(urlParser[ : index + 1])

        dateString = "/".join(dateParser)

        suffixe = urlParser[-1]
        return urljoin(urljoin(base,dateString), suffixe)
    
    def testDirect(url : str, direction : str):
        """Le test est effectué à l'aide de la logique interne au programme"""
        newUrl = Url.handlePrefixNumberSuffixExtension(url, direction)

        if not newUrl:
            return True

        response = Url.getUrl(newUrl)

        if response.status_code in (500, 404, 403):
            return True

        toCheck = any(s.isdigit() for s in newUrl.split("/")[ : -1])
                
        if toCheck:

            soup = BeautifulSoup(response.text,  "lxml")

            if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:

                for _ in range(Url.tentatives):
                    newUrl = Url.createNewUrl(newUrl, direction)
                    thread = threading.Thread(target=Url.searchInMultithreads, args=(newUrl,))
                    Url.threadsList.append(thread)
                    thread.start()

                    if Url.urlFound.is_set():
                        break

                for thread in Url.threadsList:
                    thread.join()

                if Url.urlFound.is_set():
                    Url.urlFound.clear()
                    Url.resetThreadsList()
                    return False
                
                Url.resetThreadsList()
                return True

        pyperclip.copy(newUrl)
        Url.copyPaste(True)

        if ".com" not in newUrl:
            _, y = pyautogui.position()
            x = 0.989*Constante.screenWidth
            Url.mouseMove(x, y)

        return False

    def testIndirect(url : str, direction : str):
        """Le test est effectué à l'aide du lien url généré"""
        startUrl = Url.handlePrefixNumber(url, direction)

        response = Url.getUrl(startUrl)
        
        soup = BeautifulSoup(response.text, "lxml")
        
        newPageLink = next((a["href"] for a in soup.find_all("a", href=True) if startUrl in a["href"]), "")

        if newPageLink != "":
            pyperclip.copy(newPageLink)
            Url.copyPaste(True)
            return False
        
        return True

    def searchAndGoToPage(url : str, index : int, direction="next"):
        """
        Gère la navigation entre les pages :
        - url: L'url copié du clipboard
        - soup: La page web téléchargée
        - index: L'index du groupe de traduction dans la database
        - direction: "next" ou "last"
        
        TODO: Regardez tous les codes et faire un affichage spécialisée
        """

        if index == 0:
            startUrl = Url.handlePrefixNumber(url, direction)

            if not startUrl:
                Display.showStatusMessage("Le chapitre -1 n'existe pas") if direction == "last" else Display.showStatusMessage("Si tu es rentré là, une erreur est survenue dans le code")
                return
            
            response = Url.getUrl(url)
            
            soup = BeautifulSoup(response.text, "lxml")
            
            newPageLink = next((a["href"] for a in soup.find_all("a", href=True) if startUrl in a["href"]), "")
 
            hashIndex = newPageLink.find("#")

            if hashIndex != -1:
                newPageLink = newPageLink.replace(newPageLink[hashIndex : ], "")

            if newPageLink != "":
                pyperclip.copy(newPageLink)
                Url.copyPaste(True)

            else:

                if response.ok:

                    if not Url.searchAndGoToPageAlternative(startUrl):
                        Display.showStatusMessage("Il n'y a pas de lien présent dans la page")

                else:

                    if response.status_code == 403:
                        match = Url.globalRegex.search(url)
                        translatorFound = match.group(0)
                        i = Url.mapping[translatorFound]

                        Constante.updateTranslatorsGroup(translatorFound, i, Constante.REMOVE)
                        Constante.updateTranslatorsGroup(translatorFound, i + 1, Constante.ADD)
                        Url.goToPage(url, direction)

                    else:
                        Display.showStatusMessage(f"Error code :\n{response.status_code}")

                pyperclip.copy("")

        else:
            # On génère la nouvelle URL
            newUrl = Url.handlePrefixNumberSuffixExtension(url, direction)

            if not newUrl:
                Display.showStatusMessage("Le chapitre -1 n'existe pas") if direction == "last" else Display.showStatusMessage("Si tu es rentré là, une erreur est survenue dans le code")
                return

            toCheck = any(s.isdigit() for s in newUrl.split("/")[ : -1])
                    
            if toCheck:
                response = Url.getUrl(newUrl)

                soup = BeautifulSoup(response.text, "lxml")

                if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:

                    for _ in range(Url.tentatives):
                        newUrl = Url.createNewUrl(newUrl, direction)
                        thread = threading.Thread(target=Url.searchInMultithreads, args=(newUrl,))
                        Url.threadsList.append(thread)
                        thread.start()

                        if Url.urlFound.is_set():
                            break

                    for thread in Url.threadsList:
                        thread.join()

                    if Url.urlFound.is_set():
                        Url.urlFound.clear()
                        Url.resetThreadsList()
                        return
                    
                    Display.showStatusMessage("Il n'existe pas de nouveau chapitre\nou\nil y a un problème dans le blog") if direction == "next" else Display.showStatusMessage("Il n'y a pas d'ancien chapitre\nou\nil y a un problème dans le blog")
                    Url.resetThreadsList()
                    return

            # On copie l'URL générée
            pyperclip.copy(newUrl)
            Url.copyPaste(True)

            if ".com" not in newUrl:
                _, y = pyautogui.position()
                x = 0.989*Constante.screenWidth
                Url.mouseMove(x, y)

    def searchAndGoToPageAlternative(url : str):
        
        if "goldennovel" in url:
            urlParser = url.split("/")

            index = next((i for i, value in enumerate(urlParser) if value == "index.php"), None)

            urlParser.insert(index + 1, "category")
            urlToCheck = "/".join(urlParser[ : -1])

            response = Url.getUrl(urlToCheck)

            soup = BeautifulSoup(response.text, "lxml")
            
            newPageLink = next((a["href"] for a in soup.find_all("a", href=True) if url in a["href"]), "")
 
            hashIndex = newPageLink.find("#")

            if hashIndex != -1:
                newPageLink = newPageLink.replace(newPageLink[hashIndex : ], "")

            if newPageLink != "":
                pyperclip.copy(newPageLink)
                Url.copyPaste(True)
                return True

        return False

    def searchInMultithreads(url):
        response = Url.getUrl(url)

        soup = BeautifulSoup(response.text,"lxml")

        if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:
            return
        
        Url.urlFound.set()
        pyperclip.copy(url)
        Url.copyPaste(True)

    def searchAndGoToPage_2ndMethod(url : str, direction : str):
        """Cherche le button Previous/Next sur l'écran et clique dessus"""
        if direction == "next":

            for imagePath in Constante.imagesNextButton:
                thread = threading.Thread(target=Url.searchInMultithreads_2ndMethod, args=(url, imagePath))
                Url.threadsList.append(thread)
                thread.start()

                if Url.imageFound.is_set():
                    break

        elif direction == "last":

            for imagePath in Constante.imagesPrevButton:
                thread = threading.Thread(target=Url.searchInMultithreads_2ndMethod, args=(url, imagePath))
                Url.threadsList.append(thread)
                thread.start()

                if Url.imageFound.is_set():
                    break

        for thread in Url.threadsList:
            thread.join()

        if Url.imageFound.is_set():
            Url.imageFound.clear()
            Url.resetThreadsList()
            return
        
        Url.resetThreadsList()
        
    def searchInMultithreads_2ndMethod(url : str, imagePath):
        button = None

        try:
            button = pyautogui.locateOnScreen(imagePath, confidence=0.831)

        except pyautogui.ImageNotFoundException:
            return

        if button:
            Url.imageFound.set()
            # Calcule le centre du bouton
            x, y = pyautogui.center(button)

            if not "nulltranslation" in url:
                Url.mouseMove(x, y)

            else:
                Url.mouseMoveAlternative(x, y)

    @testScreenCorners
    def copyPaste(copyOrPaste=False):
        """"Copier-coller automatique + vidange de la clipboard"""
        if not copyOrPaste:
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.press('esc')

        else:
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
            pyperclip.copy('')

    def goToPage(url : str, direction : str):
        """"Cherche si le groupe de traduction existe et exécute la fonction correspondante"""
        match = Url.globalRegex.search(url)

        if not match:
            Url.testUrl(url, direction)
            return

        translatorFound = match.group(0)
        i = Url.mapping[translatorFound]

        if i == len(Constante.translatorsGroup) - 1:
            return

        func = Url.methods[0] if i < 2 else Url.methods[1]

        # Appel de la fonction correspondante
        if func.__code__.co_argcount > 2:
            func(url, i, direction)

        else:
            func(url, direction)

    def searchPage(direction):
        """Fonction qui recherche la page html précédente/suivante en fonction de la page actuelle"""
        if Constante.reloadHandler.is_set():
            Url.updateRegex()
            Constante.reloadHandler.clear()

        Url.copyPaste()
        url = pyperclip.paste()

        if url.startswith("http"):
            Url.goToPage(url, direction)

        else:
            Url.searchAndGoToPage_2ndMethod(url, direction)

        keyboard.unblock_key("right") if direction == "next" else keyboard.unblock_key("left")
        Constante.EnableGlobalListener()

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")