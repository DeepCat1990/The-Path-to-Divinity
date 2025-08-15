import json
import random
from .events import event_bus

class SectManager:
    def __init__(self):
        with open("data/sects.json", "r", encoding="utf-8") as f:
            self.sects_data = json.load(f)
        self.current_sect = None
        
    def get_available_sects(self, character):
        available = []
        for sect_id, sect in self.sects_data["sects"].items():
            req = sect["entry_requirement"]
            if (character.power >= req["power"] and 
                character.talent >= req["talent"]):
                available.append((sect_id, sect))
        return available
    
    def join_sect(self, sect_id, character):
        if sect_id in self.sects_data["sects"]:
            self.current_sect = sect_id
            sect = self.sects_data["sects"][sect_id]
            
            # 应用门派加成
            self._apply_sect_bonus(sect, character)
            
            event_bus.emit("sect_joined", {"sect_id": sect_id, "sect": sect})
            event_bus.emit("message", f"加入了 {sect['name']}！")
            return True
        return False
    
    def _apply_sect_bonus(self, sect, character):
        bonus = sect.get("bonus", {})
        if "health_regen" in bonus:
            character.max_health = int(100 * bonus["health_regen"])
        if "mana_regen" in bonus:
            character.max_mana = int(50 * bonus["mana_regen"])
    
    def get_sect_skills(self, sect_id):
        if not sect_id or sect_id not in self.sects_data["sects"]:
            return []
        
        sect_skill_ids = self.sects_data["sects"][sect_id]["skills"]
        sect_skills = []
        
        for skill_id in sect_skill_ids:
            if skill_id in self.sects_data["sect_skills"]:
                sect_skills.append((skill_id, self.sects_data["sect_skills"][skill_id]))
        
        return sect_skills
    
    def can_learn_sect_skill(self, skill_id, character):
        if skill_id not in self.sects_data["sect_skills"]:
            return False
            
        skill = self.sects_data["sect_skills"][skill_id]
        return (skill["sect"] == self.current_sect and 
                character.power >= skill["power_requirement"])
    
    def get_current_sect_info(self):
        if self.current_sect:
            return self.sects_data["sects"][self.current_sect]
        return None