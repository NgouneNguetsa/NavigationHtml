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

    def stateMessage():
        os.system("cls")
        print("Bienvenue dans le programme NavigationHtml.")
        print("Ce programme vous permet de vous déplacer d'une page html à une autre à l'aide de vos flèches directionnelles")
        print("Appuyez <- jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page précédente.")
        print("Appuyez -> jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page suivante.")
        print("Appuyez sur r pour mettre à jour les groupes de traduction.")
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

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")