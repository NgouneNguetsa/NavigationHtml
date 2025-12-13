from constants import keyboard, Key, Listener, threading
from DisplayManagement import Display
from UrlManagement import Url
from constants import Constante

class Navigation:
    def __init__(self):
        Constante.InitVar()
        Url.InitVar()
        Display.InitVar()
        Display.start_message()
        self.pauseHandler = threading.Event()

    # La fonction est responsable de toute les actions du thread d'écoute globale
    def GL_on_press(self,key):
        if Constante.interrupt_handler.is_set():
            Display.show_interrupt_message()
            return False
        
        elif Constante.globalListener_disabled.is_set():
            return

        if key == Key.esc:
            Display.stop_message()
            return False
        
        elif key == Key.right:
            keyboard.block_key("right")
            Constante.DisableGlobalListener()
            threading.Thread(target=Url.search_page, args=("next",), daemon=True).start()

        elif key == Key.left:
            keyboard.block_key("left")
            Constante.DisableGlobalListener()
            threading.Thread(target=Url.search_page, args=("last",), daemon=True).start()

    # La fonction est responsable de la pause/remise en marche du programme
    def PR_on_press(self,key):
        if Constante.interrupt_handler.is_set():
            return False

        if key == Key.f3 and not self.pauseHandler.is_set():
            Display.show_status_message("Programme en pause")
            self.pauseHandler.set()
            Constante.DisableGlobalListener()
            try:
                keyboard.remove_hotkey(self.hotkeyHandler)
            except KeyError:
                pass

        elif key == Key.f3 and self.pauseHandler.is_set():
            Display.show_status_message("Reprise du programme")
            self.pauseHandler.clear()
            Constante.EnableGlobalListener()
            self.KeyboardInterrupt()

    def KeyboardInterrupt(self):
        self.hotkeyHandler = keyboard.add_hotkey('ctrl+c', lambda: Constante.interrupt_handler.set())

    def Run(self):
        globalListener = Listener(on_press=self.GL_on_press)
        speListener = Listener(on_press=self.PR_on_press)
        globalListener.start()
        speListener.start()
        self.KeyboardInterrupt()
        globalListener.join()
        speListener.join()

if __name__ == "__main__":
    prog = Navigation()
    prog.Run()
    