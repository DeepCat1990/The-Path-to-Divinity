import json
import random
from .character import Character
from .skills import SkillManager
from .events import event_bus

class Game:
    def __init__(self):
        with open("data/config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.character = Character(self.config["character"])
        self.skill_manager = SkillManager()
        self.day = 1
        
    def train(self):
        self.character.train(self.config["events"]["train"])
        self.next_day()
        
    def adventure(self):
        self.character.adventure(self.config["events"]["adventure"])
        self._check_skill_learning()
        self.next_day()
        
    def _check_skill_learning(self):
        available = self.skill_manager.get_available_skills(self.character.power)
        if available and random.random() < 0.3:
            skill_id, skill = random.choice(available)
            self.skill_manager.learn_skill(skill_id)
            event_bus.emit("message", f"领悟了 {skill['name']}！")
        
    def next_day(self):
        self.day += 1
        event_bus.emit("day_changed", self.day)