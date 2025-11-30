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
        if not Constante.listener_enabled:
            return
        
        if key == Key.esc:
            Display.stop_message()
            return False
        
        elif key == Key.right:
            keyboard.block_key("right")
            Constante.listener_enabled = False
            threading.Thread(target=Url.search_page, args=("next",), daemon=True).start()

        elif key == Key.left:
            keyboard.block_key("left")
            Constante.listener_enabled = False
            threading.Thread(target=Url.search_page, args=("last",), daemon=True).start()

    def Run(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":

    prog = Navigation()
    prog.Run()
    