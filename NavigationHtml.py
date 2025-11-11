from Constants import pyautogui, keyboard, time
from DisplayManagement import Display
from UrlManagement import Url
from Constants import Constante

class Navigation:

    def __init__(self):
        Constante.InitVal()
        Url.InitVal()
        Display.InitDisplay()

    def Run(self):
        Display.start_message()
        pyautogui.hotkey('alt','tab',interval=0.1)

        if not Constante.VERSION_REACTIVE:
            last_action = time.time()
            DELAI_INACTIVITE = 2  # secondes

        while True:
            if keyboard.is_pressed("right"):
                keyboard.block_key("right")

                Url.search_and_go_next_page()

                keyboard.unblock_key("right")

                if not Constante.VERSION_REACTIVE:
                    last_action = time.time()
            
            elif keyboard.is_pressed("left"):
                keyboard.block_key("left")

                Url.search_and_go_last_page()

                keyboard.unblock_key("left")

                if not Constante.VERSION_REACTIVE:
                    last_action = time.time()

            elif keyboard.is_pressed("esc"):
                break

            if not Constante.VERSION_REACTIVE:
                if time.time() - last_action > DELAI_INACTIVITE:
                    time.sleep(1)

    def __del__(self):
        Display.stop_message()


if __name__ == "__main__":

    prog = Navigation()
    prog.Run()
    del prog