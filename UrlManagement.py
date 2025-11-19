from constants import re, pyperclip, pyautogui, time, requests, BeautifulSoup, date, timedelta, urljoin
from constants import Constante
from DisplayManagement import Display

class Url:
    
    # --- Mapping des fonctions par direction ---
    methods = [
        lambda url, soup, index, direction: Url.search_and_go_to_page(url, soup, index, direction),
        lambda direction: Url.search_and_go_to_page_2nd_method(direction)
    ]

    mapping = {}
    patterns = []
    tentatives = 0

    def InitVar():
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
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\-]*)(\d+)([-\w]*)(\.\w+)$", ["prefix", "number", "suffix", "extension"], direction)

    def handle_prefix_number_suffix(url, direction):
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\-]*)(\d+)([-\w]+)$", ["prefix", "number", "suffix"], direction)

    def handle_prefix_number_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\-]*)(\d+)(\.\w+)$", ["prefix", "number", "extension"], direction)

    def handle_prefix_number(url, direction):
        return Url.apply_regex_and_modify(url, r"([a-zA-Z\-]*)(\d+)(?:[-\w]*)$", ["prefix", "number"], direction)

    def handle_number_suffix_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)([-\w]+)(\.\w+)$", ["number", "suffix", "extension"], direction)

    def handle_number_suffix(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)([-\w]+)$", ["number", "suffix"], direction)

    def handle_number_extension(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)(\.\w+)$", ["number", "extension"], direction)

    def handle_number_only(url, direction):
        return Url.apply_regex_and_modify(url, r"(\d+)$", ["number"], direction)

    def test_url_disponibility(url,direction):
        url_parser = url.rstrip("/").split("/")
        date_parser = []

        for ele in url_parser:
            if ele.isnumeric():
                date_parser.append(ele)

        if len(date_parser) == 2:
            date_parser[1] = str(int(date_parser[1]) + 1) if direction == "next" else str(int(date_parser[1]) - 1)
            date_parser[1] = '0'+ date_parser[1] if int(date_parser[1]) < 10 else date_parser[1]
            if int(date_parser[1]) > 12:
                date_parser[1] = '01'
                date_parser[0] = str(int(date_parser[0]) + 1)
            elif int(date_parser[1]) < 1:
                date_parser[1] = '12'
                date_parser[0] = str(int(date_parser[0]) - 1)

            date_parser.insert(1,'/')
            date_parser.append('/')
            
        elif len(date_parser) == 3:
            date_string = ""
            for d in date_parser:
                date_string += d

            day = timedelta(days=1)

            date_object = date.fromisoformat(date_string)
            date_object = date_object + day if direction == "next" else date_object - day
            date_parser = date_object.isoformat().split("-")

            date_parser.insert(1,'/')
            date_parser.insert(-1,'/')
            date_parser.append('/')

        base = ""
        for i in range(len(url_parser)):
            if url_parser[i].isnumeric():
                break
            else:
                if url_parser[i] != "":
                    base += url_parser[i]
                else:
                    base += "//" 

        date_string = ""
        for d in date_parser:
            date_string += d

        suffixe = url_parser[-1]
        return urljoin(urljoin(base,date_string),suffixe)
    
    def auto_select_method(url, direction):
        """
        Détecte automatiquement la structure de l'URL et applique la méthode correspondante
        """
        # Liste des patterns pour détecter chaque type d'URL
        patterns = [
            (r"([a-zA-Z]*)(\d+)$", Url.handle_prefix_number),                                  # Préfixe + numéro
            (r"(\d+)([-\w]+)$", Url.handle_number_suffix),                                     # Numéro + suffixe
            (r"(\d+)(\.\w+)$", Url.handle_number_extension),                                   # Numéro + extension

            (r"([a-zA-Z]*)(\d+)([-\w]+)$", Url.handle_prefix_number_suffix),                   # Préfixe + numéro + suffixe
            (r"([a-zA-Z]*)(\d+)(\.\w+)$", Url.handle_prefix_number_extension),                 # Préfixe + numéro + extension
            (r"(\d+)([-\w]+)(\.\w+)$", Url.handle_number_suffix_extension),                    # Numéro + suffixe + extension

            (r"([a-zA-Z]*)(\d+)([-\w]*)(\.\w+)$", Url.handle_prefix_number_suffix_extension),  # Préfixe + numéro + suffixe + extension
            (r"(\d+)$", Url.handle_number_only)                                                # Numéro uniquement
        ]

        # On applique chaque pattern pour détecter la méthode à utiliser
        for pattern, handler in patterns:
            match = re.search(pattern, Url.get_last_segment(url))
            if match:
                return handler(url, direction)

        return None

    def search_and_go_to_page(url, soup, index, direction="next"):
        """
        Gère la navigation entre les pages :
        - url: L'url copié du clipboard
        - soup: La page web téléchargée
        - index: L'index du groupe de traduction dans la database
        - direction: "next" ou "last"
        """

        if index == 0:
            start_url = Url.handle_prefix_number(url,direction)

            for a in soup.find_all("a",href=True):
                if start_url in a["href"]:
                    next_page_link = a["href"]
                    break

            if next_page_link != "":
                pyperclip.copy(next_page_link)
                Url.copy_paste(True)
            else:
                Display.show_minor_error_message("Il n'y a pas de nouveau chapitre") if direction == "next" else Display.show_minor_error_message("Le chapitre 0 n'existe pas")
        else:

            # On génère la nouvelle URL en fonction de la méthode détectée
            new_url = Url.auto_select_method(url, direction)
            if not new_url:
                Display.show_minor_error_message("Le chapitre 0 n'existe pas") if direction == "last" else Display.show_minor_error_message("Je ne sais pas comment tu es rentré ici, mais je te félicite")
                return

            toCheck = False
            for c in new_url.split("/")[:-1]:
                if c.isnumeric():
                    toCheck = True
                    
            if toCheck:
                while Url.tentatives < 31:
                    response = None
                    while not isinstance(response,requests.Response):
                        try:
                            response = requests.get(url)
                        except requests.exceptions.RequestException:
                            Display.show_major_error_message()
                    soup = BeautifulSoup(response.text,"html.parser")
                    if len(soup.text) < Constante.BLOG_TEXT_THRESHOLD:
                        new_url = Url.test_url_disponibility(new_url,direction)
                    else:
                        break
                    Url.tentatives += 1
            
            if Url.tentatives > 30:
                Display.show_minor_error_message("Il n'existe pas de nouveau chapitre") if direction == "next" else Display.show_minor_error_message("Il n'y a pas d'ancien chapitre")
                Url.tentatives = 0
                return
                    
            Url.tentatives = 0

            # On copie l'URL générée
            pyperclip.copy(new_url)
            Url.copy_paste(True)

    def search_and_go_to_page_2nd_method(direction : str):
        """Cherche le bouton Previous/Next sur l'écran et clique dessus"""
        
        bouton = None
        if direction == "next":
            for image_path in Constante.imagesNextButton:
                try:
                    bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
                    if bouton != None:
                        break
                        
                except pyautogui.ImageNotFoundException:
                    continue
        elif direction == "last":
            for image_path in Constante.imagesPrevButton:
                try:
                    bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
                    if bouton != None:
                        break

                except pyautogui.ImageNotFoundException:
                    pass
        
        if bouton:
            # Calcule le centre du bouton
            x, y = pyautogui.center(bouton)
            
            # Clique dessus
            pyautogui.click(x, y)
            time.sleep(1)

            if y < Constante.screenHeight / 2:
                yDiff = (Constante.screenHeight / 2) - y
                pyautogui.moveTo(x,Constante.screenHeight - 2*yDiff)
            
            pyautogui.leftClick()
            pyautogui.moveTo(Constante.screenWidth,y)
        else:
            Display.show_minor_error_message("Il n'y a pas de nouveau chapitre") if direction == "next" else Display.show_minor_error_message("Il n'y a pas d'ancien chapitre")
        
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
            return

        tl_found = match.group(0)
        i = Url.mapping[tl_found]
        func = Url.methods[0] if i < 2 else Url.methods[1]

        # Appel de la fonction correspondante
        if func.__code__.co_argcount == 4:
            func(url, soup, i, direction)
        else:
            func(direction)

    def search_page(direction):
        """Fonction qui recherche la page html précédente/suivante en fonction de la page actuelle"""
        
        Url.copy_paste()
        url = pyperclip.paste()
        if url:
            response = None
            while not isinstance(response,requests.Response):
                try:
                    response = requests.get(url)
                except requests.exceptions.RequestException:
                    Display.show_major_error_message()
            
            soup = BeautifulSoup(response.text, "html.parser")

            Url.go_to_page(url,soup,direction)

    def __str__():
        return f"Methods:\n{Url.methods}\n\nMapping:\n{Url.mapping}\n\nPatterns:\n{Url.patterns}\n\nRegular Expression:\n{Url.global_regex}"


if __name__ == "__main__":
    print(Url())