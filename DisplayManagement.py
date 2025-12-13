from constants import ctypes, gw, keyboard, time, pyautogui, os
from constants import Constante

class Display:
    def InitVar():
        Display.console = Display.get_active_window_info()
    
    def get_window_info(window):
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

    def get_active_window_info():
        """Retourne les infos de la fenêtre actuellement active."""
        
        try:
            return Display.get_window_info(gw.getActiveWindow())
        except Exception:
            return None

    def focus_window(hwnd):
        """Met la fenêtre correspondant au handle hwnd au premier plan."""
        
        try:
            Constante.user32.ShowWindow(hwnd, 3)  # 3 = SW_SHOWMAXIMIZED (si elle est minimisée)
            Constante.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass
        
    def start_message():
        os.system("cls")
        print("Bienvenue dans le programme NavigationHtml.")
        print("Ce programme vous permet de vous déplacer d'une page html à une autre à l'aide de vos flèches directionnelles")
        print("Appuyez <- jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page précédente.")
        print("Appuyez -> jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page suivante.")
        print("Appuyez sur F5 pour mettre en pause/résumer le programme.")
        print("Appuyez sur ECHAP/ESC pour que le programme se ferme.")
        print("\nBonne utilisation.\n(Appuyer sur ENTRÉE pour commencer le programme)")
        keyboard.wait("enter")
        pyautogui.hotkey('alt','tab')

    def stop_message():
        Display.focus_window(Display.console["handle"])
        print("\nMerci d'avoir utilisé le programme NavigationHtml.")
        print("J'espère qu'il vous a été utile.")
        time.sleep(2)
        pyautogui.hotkey('alt','tab')

    def show_minor_error_message(error_message : str):
        pyautogui.alert(f"{error_message}")
        time.sleep(1)

    def show_major_error_message():
        Display.focus_window(Display.console["handle"])
        print("Il y a eu une erreur de connexion (Internet ou retentatives max atteintes)")
        time.sleep(2)
        for i in range(3):
            print(f"Le programme va reprendre son cours dans {3-i} s")
            time.sleep(1)
        pyautogui.hotkey('alt','tab')

    def show_interrupt_message():
        Display.focus_window(Display.console["handle"])
        print("Le programme s'est fini en avance par interruption clavier")
        time.sleep(2)
        pyautogui.hotkey('alt','tab')

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")