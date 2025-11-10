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

user32 = ctypes.windll.user32

def search_and_go_next_page(url):
    """Fonction qui recherche la page html suivante en fonction de la page actuelle"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    go_to_page(url,soup,"next")

def search_and_go_next_page_1st_method(url,soup):
    """Cherche le prochain lien html présent dans la page html du lien actuel"""
    start_url = ""
    for c in url:
        if start_url.endswith("chapter"):
            break
        start_url += c

    if start_url == url:
        start_url = ""
        for c in url:
            if c.isnumeric():
                break
            start_url += c

    # Liste de tous les liens
    links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith(start_url) and url not in a["href"]]
    
    if len(links) < 2:
        pyautogui.alert("Pas de nouveau chapitre disponible")
        time.sleep(1.5)
        exit()
    else:
        pyperclip.copy(links[1])
        copy_paste(True)

def search_and_go_next_page_2nd_method(url, soup):
    """Cherche le prochain lien html logique en fonction du lien html actuel"""
    
    # Regex pour capturer un préfixe (lettres), un numéro, un suffixe variable avant .html
    match = re.search(r"([a-zA-Z]*)(\d+)([-\w]*)(\.html$|\.xml$)", url)
    
    if match:
        prefix = match.group(1)  # Le texte avant le numéro (par ex. "c" ou "")
        chapter_number = int(match.group(2))  # Le numéro du chapitre
        suffix = match.group(3)  # Le suffixe (si présent, par ex. "-a")
        extension = match.group(4)  # L'extension (".html", ".xml", etc.)
        
        # Construire l'URL avec le chapitre suivant
        new_chap = f"{prefix}{chapter_number + 1}{suffix}{extension}" if prefix else f"{chapter_number + 1}{suffix}{extension}"
        
        # Reconstituer l'URL avec le chapitre suivant
        new_url = url.replace(f"{prefix}{chapter_number}{suffix}{extension}" if prefix else f"{chapter_number}{suffix}{extension}", new_chap)
        
        # Recherche du lien correspondant dans le HTML
        link = ""
        for a in soup.find_all("a", href=True):
            if new_url in a["href"]:
                link = a["href"]
                break

        # Si aucun lien trouvé dans la page, utilise l'URL construite
        if not link:
            link = new_url

        # Copier et coller le lien de la page suivante
        pyperclip.copy(link)
        copy_paste(True)
    else:
        # Cas sans préfixe, suffixe, et extension (juste un numéro de chapitre)
        match_simple = re.search(r"(\d+)", url)
        
        if match_simple:
            chapter_number = int(match_simple.group(1))  # Le numéro du chapitre
            
            # Construire l'URL avec le chapitre suivant
            new_chap = f"{chapter_number + 1}"
            
            # Reconstituer l'URL avec le chapitre suivant (on ne change que le numéro)
            new_url = url.replace(f"{chapter_number}", new_chap)
            
            # Recherche du lien correspondant dans le HTML
            link = ""
            for a in soup.find_all("a", href=True):
                if new_url in a["href"]:
                    link = a["href"]
                    break

            # Si aucun lien trouvé dans la page, utilise l'URL construite
            if not link:
                link = new_url

            # Copier et coller le lien de la page suivante
            pyperclip.copy(link)
            copy_paste(True)

def search_and_go_next_page_3rd_method():
    """Détecte le bouton Next sur l'écran et clique dessus"""
    images = get_images_with_prefix(folder,"NextChapterButton")
    
    for image_path in images:
        bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
        if bouton != None:
            # Calcule le centre du bouton
            x, y = pyautogui.center(bouton)
            
            # Clique dessus
            pyautogui.click(x, y)
            time.sleep(1)
            pyautogui.leftClick()
            pyautogui.moveTo(screenWidth,y)
            break


def search_and_go_last_page(url):
    """Fonction qui recherche la page html précédente en fonction de la page actuelle"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    go_to_page(url,soup,"last")
        


def search_and_go_last_page_1st_method(url,soup):
    """Cherche le précédent lien html présent dans la page html du lien actuel"""
    start_url = ""
    for c in url:
        if start_url.endswith("chapter"):
            break
        start_url += c

    if start_url == url:
        start_url = ""
        for c in url:
            if c.isnumeric():
                break
            start_url += c
        
    # Liste de tous les liens
    links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith(start_url) and url not in a["href"]]
    
    pyperclip.copy(links[0])
    copy_paste(True)

def search_and_go_last_page_2nd_method(url,soup):
    """Écris le précédent lien html logique en fonction du lien actuel"""
    # Regex pour capturer un préfixe (lettres), un numéro, un suffixe variable avant .html
    match = re.search(r"([a-zA-Z]*)(\d+)([-\w]*)(\.html$|\.xml$)", url)
    
    if match:
        prefix = match.group(1)  # Le texte avant le numéro (par ex. "c" ou "")
        chapter_number = int(match.group(2))  # Le numéro du chapitre
        suffix = match.group(3)  # Le suffixe (si présent, par ex. "-a")
        extension = match.group(4)  # L'extension (".html", ".xml", etc.)
        
        # Construire l'URL avec le chapitre suivant
        new_chap = f"{prefix}{chapter_number - 1}{suffix}{extension}" if prefix else f"{chapter_number - 1}{suffix}{extension}"
        
        # Reconstituer l'URL avec le chapitre suivant
        new_url = url.replace(f"{prefix}{chapter_number}{suffix}{extension}" if prefix else f"{chapter_number}{suffix}{extension}", new_chap)
        
        # Recherche du lien correspondant dans le HTML
        link = ""
        for a in soup.find_all("a", href=True):
            if new_url in a["href"]:
                link = a["href"]
                break

        # Si aucun lien trouvé dans la page, utilise l'URL construite
        if not link:
            link = new_url

        # Copier et coller le lien de la page suivante
        pyperclip.copy(link)
        copy_paste(True)
    else:
        # Cas sans préfixe, suffixe, et extension (juste un numéro de chapitre)
        match_simple = re.search(r"(\d+)", url)
        
        if match_simple:
            chapter_number = int(match_simple.group(1))  # Le numéro du chapitre
            
            # Construire l'URL avec le chapitre précédent
            new_chap = f"{chapter_number - 1}"
            
            # Reconstituer l'URL avec le chapitre précédent (on ne change que le numéro)
            new_url = url.replace(f"{chapter_number}", new_chap)
            
            # Recherche du lien correspondant dans le HTML
            link = ""
            for a in soup.find_all("a", href=True):
                if new_url in a["href"]:
                    link = a["href"]
                    break

            # Si aucun lien trouvé dans la page, utilise l'URL construite
            if not link:
                link = new_url

            # Copier et coller le lien de la page précédente
            pyperclip.copy(link)
            copy_paste(True)

def search_and_go_last_page_3rd_method():
    """Détecte le bouton Prev/Previous sur l'écran et clique dessus"""
    images = get_images_with_prefix(folder,"PreviousChapterButton")
    
    for image_path in images:
        bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
        if bouton != None:
            # Calcule le centre du bouton
            x, y = pyautogui.center(bouton)
            
            # Clique dessus
            pyautogui.click(x, y)
            time.sleep(1)
            pyautogui.leftClick()
            pyautogui.moveTo(screenWidth,y)
            break

def copy_paste(copy_or_paste = False):
    """"Copier-coller automatique + vidange de la clipboard"""
    if not copy_or_paste:
        pyautogui.hotkey('ctrl', 'e',interval=0.1)
        pyautogui.hotkey('ctrl', 'c',interval=0.1)
        pyautogui.press('esc')
    else:
        pyautogui.hotkey('ctrl', 'e',interval=0.1)
        pyautogui.hotkey('ctrl','v',interval=0.1)
        pyautogui.press('enter')
        pyperclip.copy('')

# --- Fonction optimisée ---
def go_to_page(url, soup, direction):
    """"Cherche si le groupe de traduction existe et exécute la fonction correspondante"""
    match = global_regex.search(url)
    if not match:
        pyautogui.alert(f"{url}\nLien invalide ou groupe de traduction non présent dans la database")
        time.sleep(1.5)
        exit()

    tl_found = match.group(0)
    i = mapping[tl_found]
    func = methods[direction][i]

    # Appel de la fonction correspondante
    if func.__code__.co_argcount == 2:
        func(url, soup)
    else:
        func()

def get_images_with_prefix(folder, prefix):
    """Retourne la liste des fichiers .png qui commencent par un préfixe donné"""
    return [
        os.path.join(f'{folder}/imgs', f)
        for f in os.listdir(folder)
        if f.lower().endswith(".png") and f.startswith(prefix)
    ]

def get_window_info(window):
    """Retourne un dict avec titre, handle et pid."""
    if not window:
        return None
    try:
        hwnd = window._hWnd
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return {
            "titre": window.title,
            "handle": hwnd,
            "pid": pid.value
        }
    except Exception:
        return None

def get_active_window_info():
    """Retourne les infos de la fenêtre actuellement active."""
    try:
        return get_window_info(gw.getActiveWindow())
    except Exception:
        return None

def focus_window(hwnd):
    """Met la fenêtre correspondant au handle hwnd au premier plan."""
    try:
        user32.ShowWindow(hwnd, 9)  # 9 = SW_RESTORE (si elle est minimisée)
        user32.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print("Bienvenue dans le programme LienHtmls.py.")
    print("Ce programme vous permet de vous déplacer d'une page html à une autre à l'aide de vos flèches directionnelles")
    print("Maintenez <- jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page précédente.")
    print("Maintenez -> jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page suivante.")
    print("Maintenez ECHAP/ESC pour que le programme se ferme.")
    user_input = input("\nVoulez-vous la version réactive ou la version économe ? (Tapez r ou e) : ").lower()
    if user_input == "r":
        print("Version réactive activée")
        VERSION_REACTIVE = True
    elif user_input == "e":
        print("Version économe activée")
        VERSION_REACTIVE = False
    else:
        print("Version économe activée par défaut")
        VERSION_REACTIVE = False
    print("\nBonne utilisation.\n(Appuyer sur ENTRÉE pour commencer le programme)")
    keyboard.wait("enter")

    console = get_active_window_info()
    screenWidth, _ = pyautogui.size()
    if not VERSION_REACTIVE:
        last_action = time.time()
        DELAI_INACTIVITE = 2  # secondes
    folder = Path(__file__).parent
    urls = [["nobadnovel","shanghaifantasy","shinningnoveltranslations"],["brightnovels","otakutl"],["botitranslation"]]

    # --- Mapping des fonctions par direction ---
    methods = {
    "next": [
        lambda url, soup: search_and_go_next_page_1st_method(url, soup),
        lambda url, soup: search_and_go_next_page_2nd_method(url, soup),
        lambda url, soup: search_and_go_next_page_3rd_method(),
    ],
    "last": [
        lambda url, soup: search_and_go_last_page_1st_method(url, soup),
        lambda url, soup: search_and_go_last_page_2nd_method(url, soup),
        lambda url, soup: search_and_go_last_page_3rd_method(),
    ],
    }

    mapping = {}
    patterns = []

    for i, tl_group_list in enumerate(urls):
        for tl in tl_group_list:
            patterns.append(re.escape(tl))
            mapping[tl] = i  # Associe chaque texte au bon index

    # Compile une seule regex globale
    global_regex = re.compile("|".join(patterns))

    pyautogui.hotkey('alt','tab',interval=0.1)

    while True:
        if keyboard.is_pressed("right"):
            keyboard.block_key("right")

            copy_paste()
            url = pyperclip.paste()
            search_and_go_next_page(url)

            keyboard.unblock_key("right")

            if not VERSION_REACTIVE:
                last_action = time.time()
        
        elif keyboard.is_pressed("left"):
            keyboard.block_key("left")

            copy_paste()
            url = pyperclip.paste()
            search_and_go_last_page(url)

            keyboard.unblock_key("left")

            if not VERSION_REACTIVE:
                last_action = time.time()

        elif keyboard.is_pressed("esc"):
            focus_window(console["handle"])
            print("\nMerci d'avoir utilisé le programme LienHtmls.py.")
            print("J'espère qu'il vous a été utile.")
            time.sleep(3)
            break

        if not VERSION_REACTIVE:
            if time.time() - last_action > DELAI_INACTIVITE:
                time.sleep(1)