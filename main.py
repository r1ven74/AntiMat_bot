import threading
from bot import run_bot
from gui import run_gui

def main():
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    run_gui()

if __name__ == "__main__":
    main()