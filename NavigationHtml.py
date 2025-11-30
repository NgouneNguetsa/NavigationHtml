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

    def on_press(self,key):
        if Constante.interrupt_handler.is_set():
            Display.show_interrupt_message()
            return False
        
        elif Constante.listener_enabled.is_set():
            return

        if key == Key.esc:
            Display.stop_message()
            return False
        
        elif key == Key.right:
            keyboard.block_key("right")
            Constante.DisableListener()
            threading.Thread(target=Url.search_page, args=("next",), daemon=True).start()

        elif key == Key.left:
            keyboard.block_key("left")
            Constante.DisableListener()
            threading.Thread(target=Url.search_page, args=("last",), daemon=True).start()

    def KeyboardInterrupt(self):
        keyboard.add_hotkey('ctrl+c', lambda: Constante.interrupt_handler.set())

    def Run(self):
        listener = Listener(on_press=self.on_press)
        listener.start()
        self.KeyboardInterrupt()
        listener.join()

if __name__ == "__main__":
    prog = Navigation()
    prog.Run()
    