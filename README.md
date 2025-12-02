# NavigationHtml
Ce programme permet simplement de se déplacer d'une page web à une autre de 2 façons différentes :

**1ère méthode**
- Le programme récupère le lien html grâce à des raccourcis claviers, parse l'url et trouve le précédent/prochain lien

**2ème méthode**
- Le programme cherche simplement où se trouve le bouton du précédent/prochain chapitre

# Pré-requis
Ce programme ne fonctionne qu'avec Windows *Cela pourrait changer en fonction de ma motivation à continuer*\
Pour que ce programme fonctionne, il faut lancer la commande suivante :
```bash
py -m pip install requests bs4 pyautogui pygetwindow keyboard pyperclip opencv-python pynput lxml
```
Cela permet de récupérer les librairies nécessaires au bon fonctionnement du programme

/!\ Ce programme python ne marche que pour les versions de Python 3.11 et moins.\
    Cela est dû à la recherche sur l'écran avec pyscreeze qui n'a pas de version pour Python 3.12 et plus

# Mot de remerciement
Pour tout ceux qui utiliseront ce programme *autre que moi*, je vous remercie de l'attention portée à un petit projet tel que le mien et je vous souhaite une bonne journée.