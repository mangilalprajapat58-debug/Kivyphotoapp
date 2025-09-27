from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.popup import Popup
from plyer import filechooser   # <-- नया import
import sqlite3
import os

DATABASE_FILE = 'mydatabase.db'
PHOTO_PATHS_FILE = 'photo_paths.txt'

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # --- Header ---
        self.header = BoxLayout(orientation="vertical", size_hint_y=0.2, padding=5, spacing=5)
        self.add_widget(self.header)

        company, btype, address = self.get_company_info()
        self.company_label = Label(text=f"{company} {btype}", font_size=20, color=(1,1,1,1))
        self.address_label = Label(text=address, font_size=14, color=(1,1,1,1))
        self.header.add_widget(self.company_label)
        self.header.add_widget(self.address_label)

        sale_btn = Button(text="SALE", size_hint=(0.2, 0.4), on_release=self.open_sale_form)
        self.header.add_widget(sale_btn)

        # --- Control Buttons Row ( <  =  >  + Add Photo ) ---
        controls = BoxLayout(orientation="horizontal", size_hint_y=0.1, spacing=10, padding=5)
        prev_btn = Button(text="<", on_release=self.prev_photo)
        pause_btn = Button(text="=", on_release=self.toggle_slideshow)
        next_btn = Button(text=">", on_release=self.next_photo_manual)
        add_btn = Button(text="Add Photo", on_release=self.add_photo)
        controls.add_widget(prev_btn)
        controls.add_widget(pause_btn)
        controls.add_widget(next_btn)
        controls.add_widget(add_btn)
        self.add_widget(controls)

        # --- Photo Viewer ---
        self.photo = Image(allow_stretch=True, keep_ratio=True)
        self.add_widget(self.photo)

        # Load photo list
        self.photo_files = self.load_photo_paths()
        self.current_index = 0
        self.slideshow_event = None
        self.is_paused = False

        if self.photo_files:
            self.show_photo()
            self.start_slideshow()

    def get_company_info(self, status=1):
        company, btype, address = "N/A", "N/A", "N/A"
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cur = conn.cursor()
            cur.execute("SELECT Company, Btype, Adress FROM Company WHERE Status = ?", (status,))
            row = cur.fetchone()
            if row:
                company, btype, address = row
            conn.close()
        except Exception as e:
            print("DB Error:", e)
        return company, btype, address

    def show_photo(self):
        if self.photo_files:
            self.photo.source = self.photo_files[self.current_index]
            self.photo.reload()

    def start_slideshow(self):
        if not self.slideshow_event:
            self.slideshow_event = Clock.schedule_interval(self.next_photo, 3)

    def stop_slideshow(self):
        if self.slideshow_event:
            self.slideshow_event.cancel()
            self.slideshow_event = None

    def toggle_slideshow(self, instance):
        if self.is_paused:
            self.start_slideshow()
            self.is_paused = False
        else:
            self.stop_slideshow()
            self.is_paused = True

    def next_photo(self, dt=None):
        if not self.photo_files:
            return
        self.current_index = (self.current_index + 1) % len(self.photo_files)
        self.show_photo()

    def prev_photo(self, instance):
        if not self.photo_files:
            return
        self.current_index = (self.current_index - 1) % len(self.photo_files)
        self.show_photo()

    def next_photo_manual(self, instance):
        self.next_photo()

    def load_photo_paths(self):
        files = []
        if os.path.exists(PHOTO_PATHS_FILE):
            with open(PHOTO_PATHS_FILE, "r") as f:
                for line in f:
                    path = line.strip()
                    if os.path.exists(path):
                        files.append(path)
        return files

    def save_photo_paths(self):
        try:
            with open(PHOTO_PATHS_FILE, "w") as f:
                for path in self.photo_files:
                    f.write(path + "\n")
        except Exception as e:
            print("Error saving photo paths:", e)

    def add_photo(self, instance):
        try:
            filepaths = filechooser.open_file(title="Select Photo",
                                              multiple=True,
                                              filters=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
            if filepaths:
                for path in filepaths:
                    if path not in self.photo_files and os.path.exists(path):
                        self.photo_files.append(path)
                self.save_photo_paths()
                self.current_index = len(self.photo_files) - 1
                self.show_photo()
        except Exception as e:
            print("FileChooser Error:", e)

    def open_sale_form(self, instance):
        popup = Popup(title="SALE Form",
                      content=Label(text="This is the SALE Form!"),
                      size_hint=(0.6, 0.4))
        popup.open()

class MyApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    MyApp().run()
