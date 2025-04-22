import customtkinter as ctk
import json
import threading

class ConfigGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Настройки бота")
        self.root.geometry("600x600")
        self.config = {}
        self.lock = threading.Lock()
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        self.mats_var = ctk.StringVar(value="off")
        self.links_var = ctk.StringVar(value="off")
        self.spam_var = ctk.StringVar(value="off")

        self.switch_mats = ctk.CTkSwitch(self.root, text="АнтиМат", command=self.update_mats)
        self.switch_mats.pack(pady=20)

        self.label_mats = ctk.CTkLabel(self.root, text="Переключатель выключен", fg_color="red")
        self.label_mats.pack(pady=20)

        self.switch_links = ctk.CTkSwitch(self.root, text="АнтиСсылка", command=self.update_links)
        self.switch_links.pack(pady=20)

        self.label_links = ctk.CTkLabel(self.root, text="Переключатель выключен", fg_color="red")
        self.label_links.pack(pady=20)

        self.switch_spam = ctk.CTkSwitch(self.root, text="АнтиСпам", command=self.update_spam)
        self.switch_spam.pack(pady=20)

        self.label_spam = ctk.CTkLabel(self.root, text="Переключатель выключен", fg_color="red")
        self.label_spam.pack(pady=20)

        exit_button = ctk.CTkButton(self.root, text="Exit", command=self.root.destroy)
        exit_button.pack(pady=15)

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                with self.lock:
                    self.config = json.load(f)
                    self.switch_mats.configure(state=self.config.get('block_mats', True))
                    self.switch_links.configure(state=self.config.get('block_links', True))
                    self.switch_spam.configure(state=self.config.get('block_spam', True))
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                'block_mats': True,
                'block_links': True,
                'block_spam': True,
                'token': 'YOUR_BOT_TOKEN'
            }
            self.save_config()

    def update_mats(self):
        self.config['block_mats'] = self.switch_mats.get()
        self.save_setting('block_mats', self.config['block_mats'])
        self.update_label(self.switch_mats, self.label_mats)

    def update_links(self):
        self.config['block_links'] = self.switch_links.get()
        self.save_setting('block_links', self.config['block_links'])
        self.update_label(self.switch_links, self.label_links)

    def update_spam(self):
        self.config['block_spam'] = self.switch_spam.get()
        self.save_setting('block_spam', self.config['block_spam'])
        self.update_label(self.switch_spam, self.label_spam)

    def update_label(self, switch, label):
        if switch.get():
            label.configure(text="Переключатель включен", fg_color="green")
        else:
            label.configure(text="Переключатель выключен", fg_color="red")

    def save_setting(self, key, value):
        with self.lock:
            self.config[key] = value
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)

    def run(self):
        self.root.mainloop()

def run_gui():
    gui = ConfigGUI()
    gui.run()

if __name__ == "__main__":
    run_gui()