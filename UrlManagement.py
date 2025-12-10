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
    set_lock = threading.Lock()
    url_found = threading.Event()
    img_found = threading.Event()

    def InitVar():
        for i, tl_group_list in enumerate(Constante.tl_group):
            for tl in tl_group_list:
                Url.patterns.append(re.escape(tl))
                Url.mapping[tl] = i  # Associe chaque texte au bon index

        # Compile une seule regex globale
        Url.global_regex = re.compile("|".join(Url.patterns))

    def reset_thread_list():
        Url.thread_list.clear()

    def get_last_segment(url):
        """Retourne la dernière partie de l'URL après le dernier /"""
        return url.rstrip("/").split("/")[-1]

    def modify_chapter_number(segment, prefix, chapter_number, suffix, extension, direction):
        """Modifie le numéro selon la direction (next/last) et reconstruit le segment"""
        # En fonction de la direction, on incrémente ou décrémente
        new_number = chapter_number + 1 if direction == "next" else chapter_number - 1

        # Vérification : on évite un numéro de chapitre inférieur à 1
        if new_number < 1:
            return None  # On ne traite pas ce cas si le numéro devient invalide

        new_segment = f"{prefix}{new_number}{suffix}{extension}" if prefix else f"{new_number}{suffix}{extension}"
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
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\(-|_)]*)(\d+)([(-|_)\w]*)(\.\w+)(?:[#\w+_\w+]*)$", ["prefix", "number", "suffix", "extension"], direction)

    def handle_prefix_number_suffix(url, direction):
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\(-|_)]*)(\d+)([(-|_)\w]+)(?:[#\w+_\w+]*)$", ["prefix", "number", "suffix"], direction)

    def handle_prefix_number_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\(-|_)]*)(\d+)(\.\w+)(?:[#\w+_\w+]*)$", ["prefix", "number", "extension"], direction)

    def handle_prefix_number(url, direction):
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\(-|_)]*)(\d+)(?:[(-|_)\w+#\w+_\w+]*)$", ["prefix", "number"], direction)

    def handle_number_suffix_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)([(-|_)\w]+)(\.\w+)(?:[#\w+_\w+]*)$", ["number", "suffix", "extension"], direction)

    def handle_number_suffix(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)([(-|_)\w]+)(?:[#\w+_\w+]*)$", ["number", "suffix"], direction)

    def handle_number_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)(\.\w+)(?:[#\w+_\w+]*)$", ["number", "extension"], direction)

    def handle_number_only(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)(?:[(-|_)\w+#\w+_\w+]*)$", ["number"], direction)

    def create_new_url(url,direction):
        url_parser = url.rstrip("/").split("/")
        date_parser = [ele for ele in url_parser if ele.isdigit()]

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
    
    def auto_select_method(url, direction):
        """
        Détecte automatiquement la structure de l'URL et applique la méthode correspondante
        """
        # Liste des patterns pour détecter chaque type d'URL
        patterns = [
            (r"([a-zA-Z]*)(\d+)(?:[#\w+_\w+]*)$", Url.handle_prefix_number),                                  # Préfixe + numéro
            (r"([a-zA-Z]*)(\d+)([-\w]+)(?:[#\w+_\w+]*)$", Url.handle_prefix_number_suffix),                   # Préfixe + numéro + suffixe
            (r"([a-zA-Z]*)(\d+)(\.\w+)(?:[#\w+_\w+]*)$", Url.handle_prefix_number_extension),                 # Préfixe + numéro + extension
            (r"([a-zA-Z]*)(\d+)([-\w]*)(\.\w+)(?:[#\w+_\w+]*)$", Url.handle_prefix_number_suffix_extension),  # Préfixe + numéro + suffixe + extension
            
            (r"(\d+)([-\w]+)(?:[#\w+_\w+]*)$", Url.handle_number_suffix),                                     # Numéro + suffixe
            (r"(\d+)(\.\w+)(?:[#\w+_\w+]*)$", Url.handle_number_extension),                                   # Numéro + extension
            (r"(\d+)([-\w]+)(\.\w+)(?:[#\w+_\w+]*)$", Url.handle_number_suffix_extension),                    # Numéro + suffixe + extension

            (r"(\d+)(?:[#\w+_\w+]*)$", Url.handle_number_only)                                                # Numéro uniquement
        ]

        # On applique chaque pattern pour détecter la méthode à utiliser
        for pattern, handler in patterns:
            match = re.search(pattern, Url.get_last_segment(url))
            if match:
                return handler(url, direction)

        return None

    def search_and_go_to_page(url, index, direction="next"):
        """
        Gère la navigation entre les pages :
        - url: L'url copié du clipboard
        - soup: La page web téléchargée
        - index: L'index du groupe de traduction dans la database
        - direction: "next" ou "last"
        """

        if index == 0:
            start_url = Url.handle_prefix_number(url,direction)

            if not start_url:
                Display.show_minor_error_message("Le chapitre 0 n'existe pas") if direction == "last" else Display.show_minor_error_message("Je ne sais pas comment tu es rentré ici, mais je te félicite")
                return
            
            response = None
            while not isinstance(response,requests.Response):
                try:
                    response = requests.get(url)
                except requests.exceptions.RequestException:
                    Display.show_major_error_message()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            new_page_link = next((a["href"] for a in soup.find_all("a",href=True) if start_url in a["href"]),"")

            if new_page_link != "":
                pyperclip.copy(new_page_link)
                Url.copy_paste(True)
            else:
                Display.show_minor_error_message("Il n'y a pas de lien présent dans la page")
        else:

            # On génère la nouvelle URL en fonction de la méthode détectée
            new_url = Url.auto_select_method(url, direction)
            if not new_url:
                Display.show_minor_error_message("Le chapitre 0 n'existe pas") if direction == "last" else Display.show_minor_error_message("Je ne sais pas comment tu es rentré ici, mais je te félicite")
                return

            toCheck = any(s.isdigit() for s in new_url.split("/")[:-1])
                    
            if toCheck:
                response = None
                while not isinstance(response,requests.Response):
                    try:
                        response = requests.get(new_url)
                    except requests.exceptions.RequestException:
                        Display.show_major_error_message()

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
                    
                    Display.show_minor_error_message("Il n'existe pas de nouveau chapitre") if direction == "next" else Display.show_minor_error_message("Il n'y a pas d'ancien chapitre")
                    Url.reset_thread_list()
                    return

            # On copie l'URL générée
            pyperclip.copy(new_url)
            Url.copy_paste(True)

    def search_in_multithread(url):
        response = None
        while not isinstance(response,requests.Response):
            try:
                response = requests.get(url)
            except requests.exceptions.RequestException:
                if Constante.interrupt_handler.is_set():
                    return
                else:
                    Display.show_major_error_message()

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
        
        Display.show_minor_error_message("L'image n'existe pas ou il n'y a pas de nouveau chapitre") if direction == "next" \
        else Display.show_minor_error_message("L'image n'existe pas ou il n'y a pas d'ancien chapitre")

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
            
            # Clique dessus
            pyautogui.click(x, y)
            time.sleep(1)

            if y < Constante.screenHeight / 2:
                yDiff = (Constante.screenHeight / 2) - y
                pyautogui.moveTo(x,min(0.83*(Constante.screenHeight-1),Constante.screenHeight - 2*yDiff))
            
            pyautogui.leftClick()
            pyautogui.moveTo(Constante.screenWidth,y)

    def copy_paste(copy_or_paste = False):
        """"Copier-coller automatique + vidange de la clipboard"""
        if not copy_or_paste:
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.hotkey('ctrl', 'c')
            pyautogui.press('esc')
        else:
            pyautogui.hotkey('ctrl', 'e')
            pyautogui.hotkey('ctrl','v')
            pyautogui.press('enter')
            pyperclip.copy('')

    def go_to_page(url, direction):
        """"Cherche si le groupe de traduction existe et exécute la fonction correspondante"""
        match = Url.global_regex.search(url)
        if not match:
            pyautogui.alert(f"{url}\nLien invalide ou groupe de traduction non présent dans la database")
            time.sleep(1)
            return

        tl_found = match.group(0)
        i = Url.mapping[tl_found]
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
        if url.startswith("https") or url.startswith("http") or url.startswith("www"):
            try:
                Url.go_to_page(url,direction)
            except pyautogui.FailSafeException:
                pyautogui.move(Constante.screenWidth, Constante.screenHeight / 2)
        else:
            try:
                Url.search_and_go_to_page_2nd_method(direction)
            except pyautogui.FailSafeException:
                pyautogui.move(Constante.screenWidth, Constante.screenHeight / 2)

        keyboard.unblock_key("right") if direction == "next" else keyboard.unblock_key("left")
        Constante.EnableListener()