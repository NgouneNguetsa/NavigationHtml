from constants import re, pyperclip, pyautogui, time, requests, BeautifulSoup
from constants import Constante

class Url:
    # --- Mapping des fonctions par direction ---
    methods = {
    "next": [
        lambda url, soup: Url.search_and_go_next_page_1st_method(url, soup),
        lambda url, soup: Url.search_and_go_next_page_2nd_method(url, soup),
        lambda url, soup: Url.search_and_go_next_page_3rd_method(),
    ],
    "last": [
        lambda url, soup: Url.search_and_go_last_page_1st_method(url, soup),
        lambda url, soup: Url.search_and_go_last_page_2nd_method(url, soup),
        lambda url, soup: Url.search_and_go_last_page_3rd_method(),
    ],
    }

    mapping = {}
    patterns = []

    def InitVal():
        for i, tl_group_list in enumerate(Constante.tl_group):
            for tl in tl_group_list:
                Url.patterns.append(re.escape(tl))
                Url.mapping[tl] = i  # Associe chaque texte au bon index

        # Compile une seule regex globale
        Url.global_regex = re.compile("|".join(Url.patterns))

    def increment_chapter_number(url, prefix="", chapter_number=1, suffix="", extension=""):
        """Incrémente le numéro de chapitre et reconstruit l'URL avec les éléments donnés"""
        new_chap = f"{prefix}{chapter_number + 1}{suffix}{extension}" if prefix else f"{chapter_number + 1}{suffix}{extension}"
        
        return url.replace(f"{prefix}{chapter_number}{suffix}{extension}" if prefix else f"{chapter_number}{suffix}{extension}", new_chap)

    def decrement_chapter_number(url, prefix, chapter_number, suffix, extension):
        """Décrémente le numéro de chapitre et reconstruit l'URL avec les éléments donnés"""
        new_chap = f"{prefix}{chapter_number - 1}{suffix}{extension}" if prefix else f"{chapter_number - 1}{suffix}{extension}"
        
        return url.replace(f"{prefix}{chapter_number}{suffix}{extension}" if prefix else f"{chapter_number}{suffix}{extension}", new_chap)

    def handle_prefix_number_suffix_extension(url, direction):
        """Gère le cas avec préfixe, numéro, suffixe et extension"""
        match = re.search(r"([a-zA-Z]*)(\d+)([-\w]*)(\.\w+)$", url)
        if match:
            prefix = match.group(1)
            chapter_number = int(match.group(2))
            suffix = match.group(3)
            extension = match.group(4)
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, prefix, chapter_number, suffix, extension)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, prefix, chapter_number, suffix, extension)

            return new_url
        return None

    def handle_prefix_number_suffix(url, direction):
        """Gère le cas avec préfixe, numéro et suffixe"""
        match = re.search(r"([a-zA-Z]*)(\d+)([-\w]+)$", url)
        if match:
            prefix = match.group(1)
            chapter_number = int(match.group(2))
            suffix = match.group(3)
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, prefix, chapter_number, suffix)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, prefix, chapter_number, suffix)
            
            return new_url
        return None

    def handle_prefix_number_extension(url, direction):
        """Gère le cas avec préfixe, numéro et extension"""
        match = re.search(r"([a-zA-Z]*)(\d+)(\.\w+)$", url)
        if match:
            prefix = match.group(1)
            chapter_number = int(match.group(2))
            extension = match.group(3)
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, prefix, chapter_number, extension=extension)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, prefix, chapter_number, extension=extension)
            
            return new_url
        return None

    def handle_prefix_number(url, direction):
        """Gère le cas avec préfixe et numéro uniquement"""
        match = re.search(r"([a-zA-Z]*)(\d+)$", url)
        if match:
            prefix = match.group(1)
            chapter_number = int(match.group(2))
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, prefix, chapter_number)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, prefix, chapter_number)
            
            return new_url
        return None

    def handle_number_suffix_extension(url, direction):
        """Gère le cas avec numéro, suffixe et extension"""
        match = re.search(r"(\d+)([-\w]+)(\.\w+)$", url)
        if match:
            chapter_number = int(match.group(1))
            suffix = match.group(2)
            extension = match.group(3)
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, chapter_number=chapter_number, suffix=suffix, extension=extension)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, chapter_number=chapter_number, suffix=suffix, extension=extension)
            
            return new_url
        return None

    def handle_number_suffix(url, direction):
        """Gère le cas avec numéro et suffixe uniquement"""
        match = re.search(r"(\d+)([-\w]+)$", url)
        if match:
            chapter_number = int(match.group(1))
            suffix = match.group(2)
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, chapter_number=chapter_number, suffix=suffix)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, chapter_number=chapter_number, suffix=suffix)
            
            return new_url
        return None

    def handle_number_extension(url, direction):
        """Gère le cas avec numéro et extension uniquement"""
        match = re.search(r"(\d+)(\.\w+)$", url)
        if match:
            chapter_number = int(match.group(1))
            extension = match.group(2)
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, chapter_number=chapter_number, extension=extension)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, chapter_number=chapter_number, extension=extension)
            
            return new_url
        return None

    def handle_number_only(url, direction):
        """Gère le cas avec seulement le numéro"""
        match = re.search(r"(\d+)$", url)
        if match:
            chapter_number = int(match.group(1))
            
            if direction == "next":
                # Incrémentation du numéro et reconstruction de l'URL
                new_url = Url.increment_chapter_number(url, chapter_number=chapter_number)
            else:
                # Décrémentation du numéro et reconstruction de l'URL
                new_url = Url.decrement_chapter_number(url, chapter_number=chapter_number)
            
            return new_url
        return None

    def search_and_go_next_page_1st_method(url, soup):
        """Main function to handle all URL cases and search the next page"""
        
        # Mapping des cas aux fonctions respectives
        url_handlers = [
            Url.handle_number_only,
            Url.handle_prefix_number,
            Url.handle_number_suffix,

            Url.handle_prefix_number_suffix,
            Url.handle_prefix_number_extension,
            Url.handle_prefix_number_suffix_extension,

            Url.handle_number_suffix_extension,
            Url.handle_number_extension
        ]
        
        # On parcourt tous les cas et on exécute la fonction correspondante
        for handler in url_handlers:
            new_url = handler(url, "next")
            if new_url:
                # Recherche du lien correspondant dans le HTML
                next_page_link = ""
                for a in soup.find_all("a", href=True):
                    if new_url in a["href"]:
                        next_page_link = a["href"]
                        break

                # Si aucun lien trouvé dans la page, utilise l'URL construite
                if not next_page_link:
                    next_page_link = new_url

                # Copier et coller le lien de la page suivante
                pyperclip.copy(next_page_link)
                Url.copy_paste(True)
                return

    def search_and_go_next_page_2nd_method():
        """Détecte le bouton Next sur l'écran et clique dessus"""
        
        for image_path in Constante.imagesNextButton:
            bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
            if bouton != None:
                # Calcule le centre du bouton
                x, y = pyautogui.center(bouton)
                
                # Clique dessus
                pyautogui.click(x, y)
                time.sleep(1)
                pyautogui.leftClick()
                pyautogui.moveTo(Constante.screenWidth,y)
                break

    def search_and_go_last_page_1st_method(url, soup):
        """Main function to handle all URL cases and search the next page"""
        
        # Mapping des cas aux fonctions respectives
        url_handlers = [
            Url.handle_number_only,
            Url.handle_prefix_number,
            Url.handle_number_suffix,

            Url.handle_prefix_number_suffix,
            Url.handle_prefix_number_extension,
            Url.handle_prefix_number_suffix_extension,

            Url.handle_number_suffix_extension,
            Url.handle_number_extension
        ]
        
        # On parcourt tous les cas et on exécute la fonction correspondante
        for handler in url_handlers:
            new_url = handler(url, "last")
            if new_url:
                # Recherche du lien correspondant dans le HTML
                next_page_link = ""
                for a in soup.find_all("a", href=True):
                    if new_url in a["href"]:
                        next_page_link = a["href"]
                        break

                # Si aucun lien trouvé dans la page, utilise l'URL construite
                if not next_page_link:
                    next_page_link = new_url

                # Copier et coller le lien de la page suivante
                pyperclip.copy(next_page_link)
                Url.copy_paste(True)
                return

    def search_and_go_last_page_2nd_method():
        """Détecte le bouton Prev/Previous sur l'écran et clique dessus"""
        
        for image_path in Constante.imagesPrevButton:
            bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
            if bouton != None:
                # Calcule le centre du bouton
                x, y = pyautogui.center(bouton)
                
                # Clique dessus
                pyautogui.click(x, y)
                time.sleep(1)
                pyautogui.leftClick()
                pyautogui.moveTo(Constante.screenWidth,y)
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

    def go_to_page(url, soup, direction):
        """"Cherche si le groupe de traduction existe et exécute la fonction correspondante"""
        match = Url.global_regex.search(url)
        if not match:
            pyautogui.alert(f"{url}\nLien invalide ou groupe de traduction non présent dans la database")
            time.sleep(1.5)
            exit()

        tl_found = match.group(0)
        i = Url.mapping[tl_found]
        func = Url.methods[direction][i]

        # Appel de la fonction correspondante
        if func.__code__.co_argcount == 2:
            func(url, soup)
        else:
            func()

    def search_and_go_next_page():
        """Fonction qui recherche la page html suivante en fonction de la page actuelle"""
        
        Url.copy_paste()
        url = pyperclip.paste()
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        Url.go_to_page(url,soup,"next")


    def search_and_go_last_page():
        """Fonction qui recherche la page html précédente en fonction de la page actuelle"""
        
        Url.copy_paste()
        url = pyperclip.paste()
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        Url.go_to_page(url,soup,"last")