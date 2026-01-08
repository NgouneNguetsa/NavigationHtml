from constants import re, pyperclip, pyautogui, time, requests, BeautifulSoup, date, timedelta, threading, keyboard
from constants import urljoin
from constants import Constante
from DisplayManagement import Display

class Url:
    methods = [
        lambda url, index, direction: Url.search_and_go_to_page(url, index, direction),
        lambda direction: Url.search_and_go_to_page_2nd_method(direction)
    ]

    mapping = {}
    patterns = []

    tentatives = 31
    thread_list = []
    url_found = threading.Event()
    img_found = threading.Event()
    url_to_test = False
    
    def InitVar():
        Url.update_regex()

    def test_screen_corners(function):
        def inner(*args,**kwargs):
            try:
                function(*args,*kwargs)
            except pyautogui.FailSafeException:
                pyautogui.FAILSAFE = False
                pyautogui.move(Constante.screenWidth, Constante.screenHeight / 2)
                pyautogui.FAILSAFE = True
                function(*args,*kwargs)
        return inner

    def reset_thread_list():
        Url.thread_list.clear()

    def update_regex():
        Url.mapping.clear()
        Url.patterns.clear()

        for i, tl_group_list in enumerate(Constante.tl_group):
            for tl in tl_group_list:
                Url.patterns.append(re.escape(tl))
                Url.mapping[tl] = i  # Associe chaque texte au bon index

        # Compile une seule regex globale
        Url.global_regex = re.compile("|".join(Url.patterns))

    def get_last_segment(url):
        """Retourne la dernière partie de l'URL après le dernier /"""
        return url.rstrip("/").split("/")[-1]

    def modify_chapter_number(segment, prefix, chapter_number, suffix, extension, direction):
        """Modifie le numéro selon la direction (next/last) et reconstruit le segment"""
        # En fonction de la direction, on incrémente ou décrémente
        new_number = chapter_number + 1 if direction == "next" else chapter_number - 1

        # Vérification : on évite un numéro de chapitre inférieur à 0
        if new_number < 0:
            return None  # On ne traite pas ce cas si le numéro devient invalide

        new_segment = f"{prefix}{new_number}{suffix}{extension}"
        return new_segment

    def apply_regex_and_modify(url, pattern, groups, direction):
        """Applique un pattern à la fin de l'URL et retourne la nouvelle URL (incrémentée ou décrémentée)"""
        
        segment = Url.get_last_segment(url)
        match = re.search(pattern, segment)
        if not match:
            return None

        # Extraire les différentes parties capturées
        parts = {name: match.group(i + 1) if i < len(groups) else "" for i, name in enumerate(groups)}
        new_segment = Url.modify_chapter_number(segment, parts.get("prefix", ""), int(parts.get("number", 1)), parts.get("suffix", ""), parts.get("extension", ""), direction)
        if not new_segment:
            return None

        # Recomposer l'URL complète
        base = url[: -len(segment)]
        return urljoin(base, new_segment)

    # --- Tous les handle_* appellent apply_regex_and_modify avec un pattern différent ---
    def handle_prefix_number_suffix_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"^([a-zA-Z_-]*?)(\d+)(?=-|_[^-]*|)([a-zA-Z0-9_-]*)?([.a-zA-Z]*)?(?:[#a-zA-Z_-]*)?$", ["prefix", "number", "suffix", "extension"], direction)

    def handle_prefix_number(url, direction):
        return Url.apply_regex_and_modify(url, r"^([a-zA-Z_-]*?)(\d+)(?=[^0-9]|$)(?:.*)$", ["prefix", "number"], direction)
    
    def handle_prefix_number_suffix_extension_test(url, direction):
        return Url.apply_regex_and_modify(url, r"^([a-zA-Z_-]*?)(\d+)([a-zA-Z0-9_-]*)?([.a-zA-Z]*)?(?:[#a-zA-Z_-]*)?$", ["prefix", "number", "suffix", "extension"], direction)

    def handle_prefix_number_test(url, direction):
        return Url.apply_regex_and_modify(url, r"^([a-zA-Z_-]*?)(\d+)(?:.*)$", ["prefix", "number"], direction)

    @test_screen_corners
    def mouse_move(x,y):
        pyautogui.click(x, y)

        yDiff = abs((Constante.screenHeight / 2) - y) if y < (Constante.screenHeight / 2) else 0
        pyautogui.moveTo(0.989*Constante.screenWidth,min(0.83*Constante.screenHeight,Constante.screenHeight - 2*yDiff))            
        time.sleep(1.5)

        pyautogui.leftClick()
        pyautogui.moveTo(Constante.screenWidth,y)

    def get_url(url):
        response = None
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException:
            Display.show_major_error_message()
            return Url.get_url(url)

        return response
    
    def test_url(url,direction):
        Url.url_to_test = True

        ind_first_point = url.index(".")
        ind_second_point = url.index(".",ind_first_point+1)
        tl_group = url[ind_first_point+1:ind_second_point]
        index = 0

        time.sleep(1.5)
        new_url = Url.copy_paste()

        if new_url != url:
            index = len(Constante.tl_group) - 1
        else:
            Url.url_to_test = Url.test_indirect(url,direction)
            if Url.url_to_test:
                Url.test_direct(url,direction)
                if Url.url_to_test:
                    index = 2
                    Display.show_status_message("Image a rajoutée")
                    return

        Constante.update_tl_group(tl_group,index)
        Url.update_regex()

        Url.url_to_test = False

    def create_new_url(url,direction):
        url_parser = url.rstrip("/").split("/")
        date_parser = [ele for ele in url_parser[:-1] if ele.isdigit()]

        if len(date_parser) == 2:
            date_parser[1] = str(int(date_parser[1]) + 1) if direction == "next" else str(int(date_parser[1]) - 1)
            date_parser[1] = '0'+ date_parser[1] if int(date_parser[1]) < 10 else date_parser[1]
            if int(date_parser[1]) > 12:
                date_parser[1] = '01'
                date_parser[0] = str(int(date_parser[0]) + 1)
            elif int(date_parser[1]) < 1:
                date_parser[1] = '12'
                date_parser[0] = str(int(date_parser[0]) - 1)

            date_parser.append('/')
            
        elif len(date_parser) == 3:
            date_string = "".join(date_parser)

            day = timedelta(days=1)

            date_object = date.fromisoformat(date_string)
            date_object = date_object + day if direction == "next" else date_object - day
            date_parser = date_object.isoformat().split("-")

            date_parser.append('/')

        index = next((i for i,v in enumerate(url_parser) if v.isdigit()),None)

        base = "/".join(url_parser[:index+1])

        date_string = "/".join(date_parser)

        suffixe = url_parser[-1]
        return urljoin(urljoin(base,date_string),suffixe)
    
    def test_direct(url,direction):
        """Le test est effectué à l'aide de la logique interne au programme"""
        url1 = Url.handle_prefix_number(url,direction)
        url2 = Url.handle_prefix_number_test(url,direction)

        if url1 != url2:
            Display.show_status_message("BIP BLIP")

        toCheck = any(s.isdigit() for s in url1.split("/")[:-1])
                
        if toCheck:
            response = Url.get_url(url1)

            soup = BeautifulSoup(response.text,"lxml")
            if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:
                for _ in range(Url.tentatives):
                    url1 = Url.create_new_url(url1,direction)
                    thread = threading.Thread(target=Url.search_in_multithread,args=(url1,))
                    Url.thread_list.append(thread)
                    thread.start()

                    if Url.url_found.is_set():
                        Url.url_to_test = False
                        break

                for thread in Url.thread_list:
                    thread.join()

                if Url.url_found.is_set():
                    Url.url_found.clear()
                    Url.reset_thread_list()
                    return
                
                Url.reset_thread_list()
                return

        pyperclip.copy(url1)
        Url.copy_paste(True)
        if ".com" not in url1:
            _,y = pyautogui.position()
            x = 0.989*Constante.screenWidth
            Url.mouse_move(x,y)

    def test_indirect(url,direction):
        """Le test est effectué à l'aide du lien url généré"""
        url1 = Url.handle_prefix_number_suffix_extension(url,direction)
        url2 = Url.handle_prefix_number_suffix_extension_test(url,direction)

        if url1 != url2:
            Display.show_status_message("BIP BIP")

        response = Url.get_url(url1)
        
        soup = BeautifulSoup(response.text, "lxml")
        
        new_page_link = next((a["href"] for a in soup.find_all("a",href=True) if url1 in a["href"]),"")

        if new_page_link != "":
            Url.url_to_test = False
            pyperclip.copy(new_page_link)
            Url.copy_paste(True)

    def search_and_go_to_page(url, index, direction="next"):
        """
        Gère la navigation entre les pages :
        - url: L'url copié du clipboard
        - soup: La page web téléchargée
        - index: L'index du groupe de traduction dans la database
        - direction: "next" ou "last"
        
        TODO: Regardez tous les codes et faire un affichage spécialisée
        """

        if index == 0:
            start_url = Url.handle_prefix_number(url,direction)

            if not start_url:
                Display.show_status_message("Le chapitre -1 n'existe pas") if direction == "last" else Display.show_status_message("Si tu es rentré là, une erreur est survenue dans le code")
                return
            
            response = Url.get_url(url)
            
            soup = BeautifulSoup(response.text, "lxml")
            
            new_page_link = next((a["href"] for a in soup.find_all("a",href=True) if start_url in a["href"]),"")

            if new_page_link != "":
                pyperclip.copy(new_page_link)
                Url.copy_paste(True)
            else:
                Display.show_status_message("Il n'y a pas de lien présent dans la page") if response.ok else Display.show_status_message(f"Error code :\n{response.status_code}")
                pyperclip.copy("")
        else:

            # On génère la nouvelle URL
            new_url = Url.handle_prefix_number_suffix_extension(url, direction)
            if not new_url:
                Display.show_status_message("Le chapitre -1 n'existe pas") if direction == "last" else Display.show_status_message("Si tu es rentré là, une erreur est survenue dans le code")
                return

            toCheck = any(s.isdigit() for s in new_url.split("/")[:-1])
                    
            if toCheck:
                response = Url.get_url(new_url)

                soup = BeautifulSoup(response.text,"lxml")
                if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:
                    for _ in range(Url.tentatives):
                        new_url = Url.create_new_url(new_url,direction)
                        thread = threading.Thread(target=Url.search_in_multithread,args=(new_url,))
                        Url.thread_list.append(thread)
                        thread.start()

                        if Url.url_found.is_set():
                            break

                    for thread in Url.thread_list:
                        thread.join()

                    if Url.url_found.is_set():
                        Url.url_found.clear()
                        Url.reset_thread_list()
                        return
                    
                    Display.show_status_message("Il n'existe pas de nouveau chapitre\nou\nil y a un problème dans le blog") if direction == "next" else Display.show_status_message("Il n'y a pas d'ancien chapitre\nou\nil y a un problème dans le blog")
                    Url.reset_thread_list()
                    return

            # On copie l'URL générée
            pyperclip.copy(new_url)
            Url.copy_paste(True)
            if ".com" not in new_url:
                _,y = pyautogui.position()
                x = 0.989*Constante.screenWidth
                Url.mouse_move(x,y)

    def search_in_multithread(url):
        response = Url.get_url(url)

        soup = BeautifulSoup(response.text,"lxml")
        if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:
            return
        
        Url.url_found.set()
        pyperclip.copy(url)
        Url.copy_paste(True)

    def search_and_go_to_page_2nd_method(direction : str):
        """Cherche le bouton Previous/Next sur l'écran et clique dessus"""
        if direction == "next":
            for img_path in Constante.imagesNextButton:
                thread = threading.Thread(target=Url.search_in_multithread_2nd_method,args=(img_path,))
                Url.thread_list.append(thread)
                thread.start()

                if Url.img_found.is_set():
                    break

        elif direction == "last":
            for img_path in Constante.imagesPrevButton:
                thread = threading.Thread(target=Url.search_in_multithread_2nd_method,args=(img_path,))
                Url.thread_list.append(thread)
                thread.start()

                if Url.img_found.is_set():
                    break

        for thread in Url.thread_list:
            thread.join()

        if Url.img_found.is_set():
            Url.img_found.clear()
            Url.reset_thread_list()
            return
        
        Display.show_status_message("L'image n'existe pas ou il n'y a pas de nouveau chapitre") if direction == "next" \
        else Display.show_status_message("L'image n'existe pas ou il n'y a pas d'ancien chapitre")

        Url.reset_thread_list()
        
    def search_in_multithread_2nd_method(img_path):
        bouton = None
        try:
            bouton = pyautogui.locateOnScreen(img_path,confidence=0.831)
        except pyautogui.ImageNotFoundException:
            return

        if bouton:
            Url.img_found.set()
            # Calcule le centre du bouton
            x, y = pyautogui.center(bouton)
            Url.mouse_move(x,y)

    @test_screen_corners
    def copy_paste(copy_or_paste = False):
        """"Copier-coller automatique + vidange de la clipboard"""
        if not copy_or_paste:
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.press('esc')
        else:
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.hotkey('ctrl','v')
            pyautogui.press('enter')
            pyperclip.copy('')

    def go_to_page(url, direction):
        """"Cherche si le groupe de traduction existe et exécute la fonction correspondante"""
        match = Url.global_regex.search(url)
        if not match:
            # Url.test_url(url,direction)
            Display.show_status_message(f"{url}\nLien invalide ou groupe de traduction non présent dans la database")
            return

        tl_found = match.group(0)
        i = Url.mapping[tl_found]

        if i == len(Constante.tl_group) - 1:
            return

        func = Url.methods[0] if i < 2 else Url.methods[1]

        # Appel de la fonction correspondante
        if func.__code__.co_argcount > 1:
            func(url, i, direction)
        else:
            func(direction)

    def search_page(direction):
        """Fonction qui recherche la page html précédente/suivante en fonction de la page actuelle"""

        Url.copy_paste()
        url = pyperclip.paste()
        if url.startswith("http"):
            Url.go_to_page(url,direction)
        else:
            Url.search_and_go_to_page_2nd_method(direction)

        keyboard.unblock_key("right") if direction == "next" else keyboard.unblock_key("left")
        Constante.EnableGlobalListener()

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")