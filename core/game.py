import json
from .character import Character
from .events import event_bus

class Game:
    def __init__(self):
        with open("data/config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.character = Character(self.config["character"])
        
    def train(self):
        self.character.train(self.config["events"]["train"])
        
    def adventure(self):
        self.character.adventure(self.config["events"]["adventure"])