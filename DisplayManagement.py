import keyboard
import ctypes
import pygetwindow as gw
import time
import pyautogui
import os
import psutil
from tkinter import ttk

from constants import Constante

class Display:
    def InitVar():
        Display.console = getActiveWindowInfo()

    def isBrowserWindow():
        window = getActiveWindowInfo()

        if not window:
            return False
        
        try:
            process = psutil.Process(window["pid"])
            processName = process.name().lower()
            return any(navigator in processName for navigator in Constante.navigatorsList)
        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        
    def isConsoleWindow():
        window = getActiveWindowInfo()

        if not window:
            return False
        
        if window == Display.console:
            return True
        
        return False

    def stateMessage():
        os.system("cls")
        print("Bienvenue dans le programme NavigationHtml.")
        print("Ce programme vous permet de vous déplacer d'une page html à une autre à l'aide de vos flèches directionnelles")
        print("Appuyez <- jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page précédente.")
        print("Appuyez -> jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page suivante.")
        print("Appuyez sur r pour mettre à jour les groupes de traduction.")
        print("Appuyer sur l pour afficher les groupes de traduction.")
        print("Appuyez sur c pour changer un groupe de traduction.")
        print("Appuyez sur ECHAP/ESC pour que le programme se ferme.")

    def startMessage():
        Display.stateMessage()
        print("\nBonne utilisation.\n(Appuyer sur ENTRÉE pour commencer le programme)")
        keyboard.wait("enter")
        pyautogui.hotkey('alt', 'tab')

    def pauseStateMessage():
        Display.stateMessage()
        print("\nLe programme est en pause")

    def stopMessage():
        pyautogui.alert("Merci d'avoir utilisé le programme NavigationHtml.\n" 
                        "J'espère qu'il vous a été utile.")

    def showStatusMessage(statusMessage : str):
        Constante.displayHandler.set()

        pyautogui.alert(f"{statusMessage}")
        time.sleep(0.1)

        Constante.displayHandler.clear()

    def showMajorErrorMessage():
        Constante.displayHandler.set()

        focusWindow(Display.console["handle"])
        print("Il y a eu une erreur de connexion (Internet ou retentatives max atteintes)")
        time.sleep(2)

        for i in range(3):
            print(f"Le programme va reprendre son cours dans {3-i} s")
            time.sleep(1)

        pyautogui.hotkey('alt', 'tab')

        Constante.displayHandler.clear()

    def showInterruptMessage():
        pyautogui.alert("Le programme s'est fini en avance par interruption clavier")

    def showTestMessage():
        Constante.displayHandler.set()
        
        focusWindow(Display.console["handle"])

        for i in range(3):
            print(f"Commencement du test de l'url dans {3-i} s")
            time.sleep(1)

        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.5)
        Display.stateMessage()

        Constante.displayHandler.clear()

    def showTranslatorGroupsList():
        print("\nFirst research method - First case")
        print("; ".join(Constante.translatorsGroup[0]),"\n")

        print("First research method - Second case")
        print("; ".join(Constante.translatorsGroup[1]),"\n")

        print("Second research method")
        print("; ".join(Constante.translatorsGroup[2]),"\n")

        print("To skip")
        print("; ".join(Constante.translatorsGroup[3]),"\n")

    def changeTranslatorGroupsList():
        os.system("cls")
        flushStdin()
        choice = input("Voulez-vous ajouter (a)/ enlever (r)/ changer (c) un groupe de traduction ?"
                       "\nTapez une lettre (a/r/c) : ")
        choice = choice.lower()

        methodDict = {1 : "First research method - First case", 
                      2 : "First research method - Second case", 
                      3 : "Second research method", 
                      4 : "To skip"}

        if choice == 'a':
            translatorGroup = input("\nQuel est le groupe de traduction ?\n")
            translatorGroup = translatorGroup.lower()

            index = input("\nDans quelle méthode de recherche voulez-vous le mettre ?"
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

        elif choice == 'r':
            index = input("\nDans quelle méthode de recherche voulez-vous retirer le groupe de traduction ?"
                         f"\n{methodDict[1]} (1)"
                         f"\n{methodDict[2]} (2)"
                         f"\n{methodDict[3]} (3)"
                         f"\n{methodDict[4]} (4)"
                          "\nTapez un chiffre (1-4) : ")
            intIndex = int(index)

            while intIndex < 1 or intIndex > 4:
                index = input("Entrée invalide. Tapez un nouveau chiffre (1-4) : ")
                intIndex = int(index)

            print("\n")
            for i in range(len(Constante.translatorsGroup[intIndex - 1])):
                print(f"{i + 1} : {Constante.translatorsGroup[intIndex - 1][i]}")

            groupChoice = input("\nQuel est le groupe de traduction que vous voulez enlever ?"
                               f"\nTapez un chiffre (1-{len(Constante.translatorsGroup[intIndex - 1])}) : ")

            while int(groupChoice) < 1 or int(groupChoice) > len(Constante.translatorsGroup[intIndex - 1]):
                groupChoice = input("Entrée invalide."
                                   f"Tapez un nouveau chiffre (1-{len(Constante.translatorsGroup[intIndex - 1])}) : ")
                
            Constante.updateTranslatorsGroup(Constante.translatorsGroup[intIndex - 1][int(groupChoice) - 1], intIndex - 1, Constante.REMOVE)

        elif choice == 'c':
            index = input("\nDans quelle méthode de recherche voulez-vous retirer le groupe de traduction ?"
                         f"\n{methodDict[1]} (1)"
                         f"\n{methodDict[2]} (2)"
                         f"\n{methodDict[3]} (3)"
                         f"\n{methodDict[4]} (4)"
                          "\nTapez un chiffre (1-4) : ")
            intIndex = int(index)

            while intIndex < 1 or intIndex > 4:
                index = input("Entrée invalide. Tapez un chiffre (1-4) : ")
                intIndex = int(index)

            matchingPairs = [(key, value) for key, value in methodDict.items() if key != intIndex]
            
            print("\nDans quelle méthode de recherche voulez-vous le mettre ?")
            for key, value in matchingPairs:
                print(f"{value} ({key})")
            otherIndex = input("Tapez un chiffre (1-4) : ")
            intOtherIndex = int(otherIndex)

            while (intIndex == intOtherIndex) or intOtherIndex < 1 or intOtherIndex > 4:
                otherIndex = input("Entrée invalide. Tapez un chiffre (1-4) : ")
                intOtherIndex = int(otherIndex)

            print("\n")
            for i in range(len(Constante.translatorsGroup[intIndex - 1])):
                print(f"{i + 1} : {Constante.translatorsGroup[intIndex - 1][i]}")

            groupChoice = input("\nQuel est le groupe de traduction que vous voulez changer ?"
                               f"\nTapez un chiffre (1-{len(Constante.translatorsGroup[intIndex - 1])}) : ")
            intGroupChoice = int(groupChoice)

            while intGroupChoice < 1 or intGroupChoice > len(Constante.translatorsGroup[intIndex - 1]):
                groupChoice = input("Entrée invalide."
                                   f"Tapez un nouveau chiffre (1-{len(Constante.translatorsGroup[intIndex - 1])}) : ")
                intGroupChoice = int(groupChoice)
                
            translatorGroup = Constante.translatorsGroup[intIndex - 1][intGroupChoice - 1]
            Constante.updateTranslatorsGroup(translatorGroup, intIndex - 1, Constante.REMOVE)
            Constante.updateTranslatorsGroup(translatorGroup, intOtherIndex - 1, Constante.ADD)

        else:
            Display.changeTranslatorGroupsList()
            return False

        Display.pauseStateMessage()
        print("\nNouvelle liste de groupe de traduction\n")
        Display.showTranslatorGroupsList()
        
        return False

def getWindowInfo(window):
    """Retourne un dict avec titre, handle et pid."""
    
    try:
        hwnd = window._hWnd
        pid = ctypes.c_ulong()
        Constante.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return {
            "titre": window.title,
            "handle": hwnd,
            "pid": pid.value
        }
    
    except Exception:
        return None

def getActiveWindowInfo():
    """Retourne les infos de la fenêtre actuellement active."""
    
    try:
        return getWindowInfo(gw.getActiveWindow())
    
    except Exception:
        return None

def focusWindow(hwnd):
    """Met la fenêtre correspondant au handle hwnd au premier plan."""
    
    try:
        Constante.user32.ShowWindow(hwnd, 3)  # 3 = Active la fenêtre en plein écran
        Constante.user32.SetForegroundWindow(hwnd)

    except Exception:
        pass

def flushStdin():
    try:
        import msvcrt

        while msvcrt.kbhit():
            msvcrt.getch()

    except ImportError:
        import sys, termios

        termios.tcflush(sys.stdin, termios.TCIFLUSH)

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")