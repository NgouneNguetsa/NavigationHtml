import keyboard
from pynput.keyboard import Key, KeyCode, Listener
import threading
from watchdog.observers import Observer

from DisplayManagement import Display
from UrlManagement import Url
from constants import Constante
from DirectoryManagement import Directory, DirectoryWatcherHandler

class Navigation:

    def __init__(self):
        Directory.InitVar()
        Constante.InitVar()
        Url.InitVar()
        Display.InitVar()
        Display.startMessage()

        self.eventHandler = DirectoryWatcherHandler()
        self.observer = Observer()
        self.observer.schedule(self.eventHandler, path=Directory.subdirectory, recursive=False)

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
                if self.stopEvent.wait(0.3):
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
                    keyboard.remove_hotkey('ctrl + c')

                except KeyError:
                    pass

            elif Display.isBrowserWindow() and self.pauseHandler.is_set():
                self.pauseHandler.clear()
                
                self.specialListener.stop()
                self.specialListener.join()

                Display.stateMessage()
                Constante.EnableGlobalListener()
                HotkeyInterruption()

            if self.stopEvent.wait(0.3):
                break

    def SpecialListener(self,key):
        if Display.isConsoleWindow():

            if (key == KeyCode.from_char("l") or key == KeyCode.from_char("L")):
                Display.showTranslatorGroupsList()

            elif key == KeyCode.from_char("r") or key == KeyCode.from_char("R"):
                Constante.reloadTranslatorsGroupList()
                print("\nMise a jour des groupes de traduction terminée")

            elif (key == KeyCode.from_char("c") or key == KeyCode.from_char("C")):
                changeThread = threading.Thread(target=Display.changeTranslatorGroupsList, daemon=True)
                changeThread.start()
                changeThread.join()

    def Run(self):
        globalListener = Listener(on_press=self.GlobalListener)
        globalListener.start()

        threading.Thread(target=self.PauseResume, daemon=True).start()

        self.observer.start()

        HotkeyInterruption()
        WindowChangeState()

        while not self.stopEvent.is_set() and not Constante.interruptHandler.is_set():
            if self.stopEvent.wait(1):
                break

        self.observer.stop()
        self.observer.join()

        globalListener.join()

        try:
            keyboard.unhook_all()

        except Exception:
            pass

def HotkeyInterruption():
    try:
        keyboard.remove_hotkey('ctrl + c')

    except KeyError:
        pass

    keyboard.add_hotkey('ctrl + c', lambda: Constante.interruptHandler.set())

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
    