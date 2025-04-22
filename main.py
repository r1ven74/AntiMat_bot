from bot import *
from gui import *

def main():
    update_json_file('config.json', 'block_mats', '0')
    update_json_file('config.json', 'block_links', '0')
    update_json_file('config.json', 'block_spam', '0')
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    run_gui()
if __name__ == "__main__":
    main()