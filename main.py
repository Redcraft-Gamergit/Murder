import random
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen

WORDS_FILE = "Murder/words.json"
SKIN_FOLDER = "skins"
MAX_SKINS = 7


# ---------------------------------------------------------
# MENÜ SCREEN
# ---------------------------------------------------------
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        layout.add_widget(Label(text="Murder Game", font_size=40))

        self.name_inputs = []

        for i in range(12):  # max 12 Spieler
            name = TextInput(hint_text=f"Spieler {i+1} Name", multiline=False)
            self.name_inputs.append(name)
            layout.add_widget(name)

        # Murder Tipps AN/AUS
        self.tips_enabled = True
        self.tip_button = Button(text="Murder Tipps: AN", on_press=self.toggle_tips)
        layout.add_widget(self.tip_button)

        start_btn = Button(text="Spiel starten", font_size=24, on_press=self.start_game)
        layout.add_widget(start_btn)

        self.add_widget(layout)

    def toggle_tips(self, instance):
        self.tips_enabled = not self.tips_enabled
        self.tip_button.text = "Murder Tipps: AN" if self.tips_enabled else "Murder Tipps: AUS"

    def start_game(self, instance):
        names = [n.text.strip() for n in self.name_inputs if n.text.strip()]

        if len(names) < 3:
            return

        self.manager.player_names = names
        self.manager.player_count = len(names)
        self.manager.tips_enabled = self.tips_enabled

        self.manager.current = "setup"


# ---------------------------------------------------------
# SETUP SCREEN
# ---------------------------------------------------------
class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Runde vorbereiten", font_size=32))

        start_btn = Button(text="Runde starten", on_press=self.start_game)
        layout.add_widget(start_btn)

        self.add_widget(layout)

    def start_game(self, instance):
        count = self.manager.player_count

        # Wörter laden
        with open(WORDS_FILE, "r", encoding="utf-8") as f:
            word_help_list = json.load(f)

        entry = random.choice(word_help_list)
        self.manager.secret_word = entry["word"]
        self.manager.murder_hint = entry["help"]

        # Spieler erstellen
        players = [{"has_word": True} for _ in range(count)]
        murder_index = random.randint(0, count - 1)
        players[murder_index]["has_word"] = False
        self.manager.murder_index = murder_index

        # Skins laden
        available_skins = []
        for i in range(1, MAX_SKINS + 1):
            path = f"{SKIN_FOLDER}/{i}.png"
            if os.path.exists(path):
                available_skins.append(path)

        # Wenn nur 1 Skin existiert → alle bekommen denselben
        if len(available_skins) == 1:
            for p in players:
                p["skin"] = available_skins[0]

        else:
            random.shuffle(available_skins)
            for i in range(count):
                if i < len(available_skins):
                    players[i]["skin"] = available_skins[i]
                else:
                    players[i]["skin"] = random.choice(available_skins)

        self.manager.players = players
        self.manager.current_player = 0

        self.manager.current = "role"


# ---------------------------------------------------------
# ROLE SCREEN
# ---------------------------------------------------------
class RoleScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        idx = self.manager.current_player
        p = self.manager.players[idx]
        name = self.manager.player_names[idx]

        layout.add_widget(Label(text=name, font_size=30))

        skin = Image(source=p["skin"], size_hint=(1, 0.5))
        layout.add_widget(skin)

        if p["has_word"]:
            layout.add_widget(Label(text=f"Dein Wort:\n[b]{self.manager.secret_word}[/b]", markup=True))
        else:
            layout.add_widget(Label(text="Du bist der Murder!"))
            if self.manager.tips_enabled:
                layout.add_widget(Label(text=f"Hilfe: {self.manager.murder_hint}"))

        next_btn = Button(text="Weiter", on_press=self.next_player)
        layout.add_widget(next_btn)

        self.add_widget(layout)

    def next_player(self, instance):
        self.manager.current_player += 1
        if self.manager.current_player >= self.manager.player_count:
            self.manager.current = "vote"
        else:
            self.manager.current = "role"


# ---------------------------------------------------------
# VOTE SCREEN
# ---------------------------------------------------------
class VoteScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Wen wählt ihr?", font_size=32))

        self.spinner = Spinner(
            text="Spieler wählen",
            values=self.manager.player_names,
            size_hint=(1, 0.3)
        )

        vote_btn = Button(text="Abstimmen", on_press=self.vote)

        layout.add_widget(self.spinner)
        layout.add_widget(vote_btn)

        self.add_widget(layout)

    def vote(self, instance):
        chosen = self.spinner.text
        if chosen == "Spieler wählen":
            return

        idx = self.manager.player_names.index(chosen)
        is_murder = (idx == self.manager.murder_index)

        if is_murder:
            self.manager.vote_result = f"{chosen} war der Murder! Runde beendet."
        else:
            self.manager.vote_result = f"{chosen} war NICHT der Murder. Runde vorbei."

        self.manager.current = "result"


# ---------------------------------------------------------
# RESULT SCREEN
# ---------------------------------------------------------
class ResultScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text=self.manager.vote_result, font_size=32))

        back_btn = Button(text="Zurück ins Menü", on_press=self.back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def back(self, instance):
        self.manager.current = "menu"


# ---------------------------------------------------------
# APP
# ---------------------------------------------------------
class MurderApp(App):
    def build(self):
        sm = ScreenManager()

        sm.player_names = []
        sm.player_count = 0
        sm.tips_enabled = True

        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(SetupScreen(name="setup"))
        sm.add_widget(RoleScreen(name="role"))
        sm.add_widget(VoteScreen(name="vote"))
        sm.add_widget(ResultScreen(name="result"))

        return sm


if __name__ == "__main__":
    MurderApp().run()