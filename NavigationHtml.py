import keyboard
from pynput.keyboard import Key, KeyCode, Listener
import threading
import time

from DisplayManagement import Display
from UrlManagement import Url
from constants import Constante

class Navigation:
    def __init__(self):
        Constante.InitVar()
        Url.InitVar()
        Display.InitVar()
        Display.start_message()
        self.stopEvent = threading.Event()
        self.pauseHandler = threading.Event()

    # La fonction est responsable de toute les actions du thread d'écoute globale
    def GlobalListener_on_press(self,key):
        if Constante.interrupt_handler.is_set():
            Display.show_interrupt_message()
            return False
        
        elif Constante.globalListener_disabled.is_set():
            return

        if key == Key.esc:
            self.stopEvent.set()
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

        elif key == KeyCode.from_char("r") or key == KeyCode.from_char("R"):
            Constante.reload_tl_group_list()

    # La fonction est responsable de la pause/remise en marche du programme
    def PauseResume(self):
        while not Constante.interrupt_handler.is_set() and not self.stopEvent.is_set():

            if Constante.pauseResumeListener_disabled.is_set() or Constante.test_handler.is_set():

                if self.stopEvent.wait(0.1):
                    break

                continue

            if not Display.is_browser_window() and not self.pauseHandler.is_set():
                self.pauseHandler.set()
                Display.show_status_message("Programme en pause")
                Display.pause_state_message()
                Constante.DisableGlobalListener()

                try:
                    keyboard.remove_hotkey(self.hotkeyHandler)

                except KeyError:
                    pass

            elif Display.is_browser_window() and self.pauseHandler.is_set():
                self.pauseHandler.clear()
                Display.state_message()
                Constante.EnableGlobalListener()
                self.hotkeyHandler = HotkeyInterruption()

            if self.stopEvent.wait(0.1):
                break

    def Run(self):
        globalListener = Listener(on_press=self.GlobalListener_on_press)
        PRListener = threading.Thread(target=self.PauseResume, daemon=True)
        globalListener.start()
        PRListener.start()
        self.hotkeyHandler = HotkeyInterruption()
        WindowChangeState()
        globalListener.join()

def HotkeyInterruption():
    return keyboard.add_hotkey('ctrl+c', lambda: Constante.interrupt_handler.set())

def WindowChangeState():
    keyboard.hook(onAltEvent)

def onAltEvent(event):
    if 'alt' in event.name:

        if event.event_type == keyboard.KEY_DOWN:
            Constante.DisablePauseResumeListener()

        elif event.event_type == keyboard.KEY_UP:
            Constante.EnablePauseResumeListener()

if __name__ == "__main__":
    prog = Navigation()
    prog.Run()
    