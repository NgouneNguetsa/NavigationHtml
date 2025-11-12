from constants import re, pyperclip, pyautogui, time, requests, BeautifulSoup, urljoin
from constants import Constante
from DisplayManagement import Display

class Url:
    
    # --- Mapping des fonctions par direction ---
    methods = {
    "next": [
        lambda url, soup, index, direction: Url.search_and_go_to_page(url, soup, index, direction),
        lambda direction: Url.search_and_go_to_page_2nd_method(direction)
    ],
    "last": [
        lambda url, soup, index, direction: Url.search_and_go_to_page(url, soup, index, direction),
        lambda direction: Url.search_and_go_to_page_2nd_method(direction)
    ],
    }

    mapping = {}
    patterns = []

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

    def auto_select_method(url, direction):
        """
        Détecte automatiquement la structure de l'URL et applique la méthode correspondante
        """
        # Liste des patterns pour détecter chaque type d'URL
        patterns = [
            (r"([a-zA-Z]*)(\d+)([-\w]*)(\.\w+)$", Url.handle_prefix_number_suffix_extension),  # Préfixe + numéro + suffixe + extension
            (r"([a-zA-Z]*)(\d+)([-\w]+)$", Url.handle_prefix_number_suffix),                   # Préfixe + numéro + suffixe
            (r"([a-zA-Z]*)(\d+)(\.\w+)$", Url.handle_prefix_number_extension),                 # Préfixe + numéro + extension
            (r"([a-zA-Z]*)(\d+)$", Url.handle_prefix_number),                                  # Préfixe + numéro
            (r"(\d+)([-\w]+)(\.\w+)$", Url.handle_number_suffix_extension),                    # Numéro + suffixe + extension
            (r"(\d+)([-\w]+)$", Url.handle_number_suffix),                                     # Numéro + suffixe
            (r"(\d+)(\.\w+)$", Url.handle_number_extension),                                   # Numéro + extension
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
            next_page_link = ""
            for a in soup.find_all("a", href=True):
                if start_url in a["href"]:
                    next_page_link = a["href"]
                    break

            if next_page_link != "":
                pyperclip.copy(next_page_link)
                Url.copy_paste(True)
            else:
                Display.show_error_message("Il n'y a pas de nouveau chapitre") if direction == "next" else Display.show_error_message("Le chapitre 0 n'existe pas")
        else:

            # On génère la nouvelle URL en fonction de la méthode détectée
            new_url = Url.auto_select_method(url, direction)
            if not new_url:
                Display.show_error_message("COMMENT !? J'AI PRIS TOUS LES CAS EN COMPTE !?")
                return

            # On copie l'URL générée
            pyperclip.copy(new_url)
            Url.copy_paste(True)

    def search_and_go_to_page_2nd_method(direction : str):
        """Cherche le bouton Previous/Next sur l'écran et clique dessus"""
        
        if direction == "next":
            for image_path in Constante.imagesNextButton:
                try:
                    bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
                    if bouton != None:
                        break
                        
                except pyautogui.ImageNotFoundException:
                    continue
        else:
            for image_path in Constante.imagesPrevButton:
                try:
                    bouton = pyautogui.locateOnScreen(image_path,confidence=0.8)
                    if bouton != None:
                        break

                except pyautogui.ImageNotFoundException:
                    pass
        
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

    # def increment_chapter_number(url, prefix, chapter_number : int, suffix, extension):
    #     """Incrémente le numéro de chapitre et reconstruit l'URL avec les éléments donnés"""
    #     new_chap = f"{prefix}{chapter_number + 1}{suffix}{extension}" if prefix else f"{chapter_number + 1}{suffix}{extension}"
        
    #     return url.replace(f"{prefix}{chapter_number}{suffix}{extension}" if prefix else f"{chapter_number}{suffix}{extension}", new_chap)

    # def decrement_chapter_number(url, prefix, chapter_number : int, suffix, extension):
    #     """Décrémente le numéro de chapitre et reconstruit l'URL avec les éléments donnés"""
    #     new_chap = f"{prefix}{chapter_number - 1}{suffix}{extension}" if prefix else f"{chapter_number - 1}{suffix}{extension}"
        
    #     return url.replace(f"{prefix}{chapter_number}{suffix}{extension}" if prefix else f"{chapter_number}{suffix}{extension}", new_chap)

    # def handle_prefix_number_suffix_extension(url, direction):
    #     """Gère le cas avec préfixe, numéro, suffixe et extension"""
    #     match = re.search(r"([a-zA-Z]*)(\d+)([-\w]*)(\.\w+)$", url)
    #     if match:
    #         prefix = match.group(1)
    #         chapter_number = int(match.group(2))
    #         suffix = match.group(3)
    #         extension = match.group(4)
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, prefix, chapter_number, suffix, extension)
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, prefix, chapter_number, suffix, extension)

    #         return new_url
    #     return None

    # def handle_prefix_number_suffix(url, direction):
    #     """Gère le cas avec préfixe, numéro et suffixe"""
    #     match = re.search(r"([a-zA-Z]*)(\d+)([-\w]+)$", url)
    #     if match:
    #         prefix = match.group(1)
    #         chapter_number = int(match.group(2))
    #         suffix = match.group(3)
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, prefix, chapter_number, suffix, "")
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, prefix, chapter_number, suffix, "")
            
    #         return new_url
    #     return None

    # def handle_prefix_number_extension(url, direction):
    #     """Gère le cas avec préfixe, numéro et extension"""
    #     match = re.search(r"([a-zA-Z]*)(\d+)(\.\w+)$", url)
    #     if match:
    #         prefix = match.group(1)
    #         chapter_number = int(match.group(2))
    #         extension = match.group(3)
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, prefix, chapter_number, "", extension)
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, prefix, chapter_number, "", extension)
            
    #         return new_url
    #     return None

    # def handle_prefix_number(url, direction):
    #     """Gère le cas avec préfixe et numéro uniquement"""
    #     match = re.search(r"([a-zA-Z]*)(\d+)$", url)
    #     if match:
    #         prefix = match.group(1)
    #         chapter_number = int(match.group(2))
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, prefix, chapter_number, "", "")
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, prefix, chapter_number, "", "")
            
    #         return new_url
    #     return None

    # def handle_number_suffix_extension(url, direction):
    #     """Gère le cas avec numéro, suffixe et extension"""
    #     match = re.search(r"(\d+)([-\w]+)(\.\w+)$", url)
    #     if match:
    #         chapter_number = int(match.group(1))
    #         suffix = match.group(2)
    #         extension = match.group(3)
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, "", chapter_number, suffix, extension)
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, "", chapter_number, suffix, extension)
            
    #         return new_url
    #     return None

    # def handle_number_suffix(url, direction):
    #     """Gère le cas avec numéro et suffixe uniquement"""
    #     match = re.search(r"(\d+)([-\w]+)$", url)
    #     if match:
    #         chapter_number = int(match.group(1))
    #         suffix = match.group(2)
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, "", chapter_number, suffix, "")
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, "", chapter_number, suffix, "")
            
    #         return new_url
    #     return None

    # def handle_number_extension(url, direction):
    #     """Gère le cas avec numéro et extension uniquement"""
    #     match = re.search(r"(\d+)(\.\w+)$", url)
    #     if match:
    #         chapter_number = int(match.group(1))
    #         extension = match.group(2)
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, "", chapter_number, "", extension)
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, "", chapter_number, "" ,extension)
            
    #         return new_url
    #     return None

    # def handle_number_only(url, direction):
    #     """Gère le cas avec seulement le numéro"""
    #     match = re.search(r"(\d+)$", url)
    #     if match:
    #         chapter_number = int(match.group(1))
            
    #         if direction == "next":
    #             # Incrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.increment_chapter_number(url, "", chapter_number, "", "")
    #         else:
    #             # Décrémentation du numéro et reconstruction de l'URL
    #             new_url = Url.decrement_chapter_number(url, "", chapter_number, "", "")
            
    #         return new_url
    #     return None

    # def search_and_go_next_page_1st_method(url,soup):
    #     """Cherche le prochain lien html présent dans la page html du lien actuel"""
    #     start_url = ""
    #     for c in url:
    #         if start_url.endswith("chapter"):
    #             break
    #         start_url += c

    #     if start_url == url:
    #         start_url = ""
    #         for c in url:
    #             if c.isnumeric():
    #                 break
    #             start_url += c

    #     # Liste de tous les liens
    #     links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith(start_url) and url not in a["href"]]
        
    #     if len(links) < 2:
    #         pyautogui.alert("Pas de nouveau chapitre disponible")
    #         time.sleep(1.5)
    #     else:
    #         pyperclip.copy(links[1])
    #         Url.copy_paste(True)

    # def search_and_go_next_page_2nd_method(url, soup):
    #     """Main function to handle all URL cases and search the next page"""
        
    #     # Mapping des cas aux fonctions respectives
    #     url_handlers = [
    #         Url.handle_number_only,
    #         Url.handle_prefix_number,
    #         Url.handle_number_suffix,

    #         Url.handle_prefix_number_suffix,
    #         Url.handle_prefix_number_extension,
    #         Url.handle_prefix_number_suffix_extension,

    #         Url.handle_number_suffix_extension,
    #         Url.handle_number_extension
    #     ]
        
    #     # On parcourt tous les cas et on exécute la fonction correspondante
    #     for handler in url_handlers:
    #         new_url = handler(url, "next")
    #         if new_url:
    #             # Recherche du lien correspondant dans le HTML
    #             next_page_link = ""
    #             for a in soup.find_all("a", href=True):
    #                 if new_url in a["href"]:
    #                     next_page_link = a["href"]
    #                     break

    #             # Si aucun lien trouvé dans la page, utilise l'URL construite
    #             if not next_page_link:
    #                 next_page_link = new_url

    #             # Copier et coller le lien de la page suivante
    #             pyperclip.copy(next_page_link)
    #             Url.copy_paste(True)
    #             return

    # def search_and_go_next_page_2nd_method():
    #     """Détecte le bouton Next sur l'écran et clique dessus"""
        


    # def search_and_go_last_page_1st_method(url,soup):
    #     """Cherche le précédent lien html présent dans la page html du lien actuel"""
    #     start_url = ""
    #     for c in url:
    #         if start_url.endswith("chapter"):
    #             break
    #         start_url += c

    #     if start_url == url:
    #         start_url = ""
    #         for c in url:
    #             if c.isnumeric():
    #                 break
    #             start_url += c
            
    #     # Liste de tous les liens
    #     links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith(start_url) and url not in a["href"]]
        
    #     pyperclip.copy(links[0])
    #     Url.copy_paste(True)

    # def search_and_go_last_page_2nd_method(url, soup):
    #     """Main function to handle all URL cases and search the next page"""
        
    #     # Mapping des cas aux fonctions respectives
    #     url_handlers = [
    #         Url.handle_number_only,
    #         Url.handle_prefix_number,
    #         Url.handle_number_suffix,

    #         Url.handle_prefix_number_suffix,
    #         Url.handle_prefix_number_extension,
    #         Url.handle_prefix_number_suffix_extension,

    #         Url.handle_number_suffix_extension,
    #         Url.handle_number_extension
    #     ]
        
    #     # On parcourt tous les cas et on exécute la fonction correspondante
    #     for handler in url_handlers:
    #         new_url = handler(url, "last")
    #         if new_url:
    #             # Recherche du lien correspondant dans le HTML
    #             next_page_link = ""
    #             for a in soup.find_all("a", href=True):
    #                 if new_url in a["href"]:
    #                     next_page_link = a["href"]
    #                     break

    #             # Si aucun lien trouvé dans la page, utilise l'URL construite
    #             if not next_page_link:
    #                 next_page_link = new_url

    #             # Copier et coller le lien de la page suivante
    #             pyperclip.copy(next_page_link)
    #             Url.copy_paste(True)
    #             return

    # def search_and_go_last_page_2nd_method():
    #     """Détecte le bouton Prev/Previous sur l'écran et clique dessus"""
        


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

        tl_found = match.group(0)
        i = Url.mapping[tl_found]
        func = Url.methods[direction][0] if i < 2 else Url.methods[direction][1]

        # Appel de la fonction correspondante
        if func.__code__.co_argcount == 4:
            func(url, soup, i, direction)
        else:
            func(direction)

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

    def __str__():
        return f"Methods:\n{Url.methods}\n\nMapping:\n{Url.mapping}\n\nPatterns:\n{Url.patterns}\n\nRegular Expression:\n{Url.global_regex}"


if __name__ == "__main__":
    print(Url())