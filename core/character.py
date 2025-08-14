import random
from .events import event_bus

class Character:
    def __init__(self, config):
        self.power = config["initial_power"]
        self.health = config["initial_health"]
        self.age = config["initial_age"]
        self.talent = random.randint(*config["talent_range"])
        self.mana = 50
        self.max_mana = 50
        self.physical_attack = 5
        self.spell_attack = 0
        
    def train(self, config):
        gain_range = config["power_gain"]
        multiplier = config["talent_multiplier"]
        gain = random.randint(*gain_range) + int(self.talent * multiplier)
        self.power += gain
        event_bus.emit("character_updated", self.__dict__)
        event_bus.emit("message", f"修炼获得 {gain} 修为")
        
    def adventure(self, events_config):
        event = self._select_event(events_config)
        if "power_bonus" in event:
            self.power += event["power_bonus"]
        if "health_loss" in event:
            loss = random.randint(*event["health_loss"])
            self.health -= loss
        if "talent_bonus" in event:
            self.talent += event["talent_bonus"]
        
        event_bus.emit("character_updated", self.__dict__)
        event_bus.emit("message", event["name"])
    
    def _select_event(self, events):
        rand = random.random()
        cumulative = 0
        for event in events:
            cumulative += event["probability"]
            if rand <= cumulative:
                return event
        return events[-1]