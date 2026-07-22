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
        Display.startMessage()
        self.stopEvent = threading.Event()
        self.pauseHandler = threading.Event()

    # La fonction est responsable de toute les actions du thread d'écoute globale
    def GlobalListener(self,key):
        if Constante.interruptHandler.is_set():
            Display.showInterruptMessage()
            return False
        
        elif Constante.globalListenerDisabled.is_set():
            return

        if key == Key.esc:
            self.stopEvent.set()
            Display.stopMessage()
            return False
        
        elif key == Key.right:
            keyboard.block_key("right")
            Constante.DisableGlobalListener()
            threading.Thread(target=Url.searchPage, args=("next",), daemon=True).start()

        elif key == Key.left:
            keyboard.block_key("left")
            Constante.DisableGlobalListener()
            threading.Thread(target=Url.searchPage, args=("last",), daemon=True).start()

    # La fonction est responsable de la pause/remise en marche du programme
    def PauseResume(self):
        while not Constante.interruptHandler.is_set() and not self.stopEvent.is_set():

            if Constante.pauseResumeListenerDisabled.is_set() or Constante.testHandler.is_set() or Constante.displayHandler.is_set():

                if self.stopEvent.wait(0.1):
                    break

                continue

            if not Display.isBrowserWindow() and not self.pauseHandler.is_set():
                self.pauseHandler.set()
                Constante.DisableGlobalListener()
                Display.showStatusMessage("Programme en pause")
                Display.pauseStateMessage()
                self.specialListener = Listener(on_press=self.SpecialListener)
                self.specialListener.start()

                try:
                    keyboard.remove_hotkey(self.hotkeyHandler)

                except KeyError:
                    pass

            elif Display.isBrowserWindow() and self.pauseHandler.is_set():
                self.pauseHandler.clear()
                self.specialListener.stop()
                self.specialListener.join()
                Display.stateMessage()
                Constante.EnableGlobalListener()
                self.hotkeyHandler = HotkeyInterruption()

            if self.stopEvent.wait(0.1):
                break

    def SpecialListener(self,key):
        if (key == KeyCode.from_char("l") or key == KeyCode.from_char("L")) and Display.isConsoleWindow():
            Display.showTranslatorGroupsList()

        elif key == KeyCode.from_char("r") or key == KeyCode.from_char("R"):
            Constante.reloadTranslatorsGroupList()

        elif (key == KeyCode.from_char("c") or key == KeyCode.from_char("C")) and Display.isConsoleWindow():
            changeThread = threading.Thread(target=Constante.changeTranslatorGroupsList, daemon=True)
            changeThread.start()
            changeThread.join()

    def Run(self):
        globalListener = Listener(on_press=self.GlobalListener)
        PauseResumeListener = threading.Thread(target=self.PauseResume, daemon=True)
        globalListener.start()
        PauseResumeListener.start()
        self.hotkeyHandler = HotkeyInterruption()
        WindowChangeState()
        globalListener.join()

def HotkeyInterruption():
    return keyboard.add_hotkey('ctrl+c', lambda: Constante.interruptHandler.set())

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
    