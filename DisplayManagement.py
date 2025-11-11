from Constants import ctypes, gw, keyboard, time, pyautogui
from Constants import Constante

class Display:

    def InitDisplay():
        Display.console = Display.get_active_window_info()
    
    def get_window_info(window):
        """Retourne un dict avec titre, handle et pid."""
        if not window:
            return None
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
            Constante.user32.ShowWindow(hwnd, 9)  # 9 = SW_RESTORE (si elle est minimisée)
            Constante.user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False
        
    def start_message():
        print("Bienvenue dans le programme NavigationHtml.")
        print("Ce programme vous permet de vous déplacer d'une page html à une autre à l'aide de vos flèches directionnelles")
        print("Maintenez <- jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page précédente.")
        print("Maintenez -> jusqu'à ce que le lien soit surligné en bleu afin d'aller à la page suivante.")
        print("Maintenez ECHAP/ESC pour que le programme se ferme.")
        user_input = input("\nVoulez-vous la version réactive ou la version économe ? (Tapez r ou e) : ").lower()
        if user_input == "r":
            print("Version réactive activée")
            Constante.VERSION_REACTIVE = True
        elif user_input == "e":
            print("Version économe activée")
            Constante.VERSION_REACTIVE = False
        else:
            print("Version économe activée par défaut")
            Constante.VERSION_REACTIVE = False
        print("\nBonne utilisation.\n(Appuyer sur ENTRÉE pour commencer le programme)")
        keyboard.wait("enter")

    def stop_message():
        Display.focus_window(Display.console["handle"])
        print("\nMerci d'avoir utilisé le programme NavigationHtml.")
        print("J'espère qu'il vous a été utile.")
        time.sleep(3)

    def show_error_message(error_message : str):
        Display.focus_window(Display.console["handle"])
        print(f"{error_message}")
        time.sleep(2)
        pyautogui.hotkey('alt','tab',interval=0.1)