import json
from .events import event_bus

class SkillManager:
    def __init__(self):
        with open("data/skills.json", "r", encoding="utf-8") as f:
            self.skills_data = json.load(f)
        self.learned_skills = []
        
    def get_available_skills(self, character_power):
        available = []
        all_skills = {**self.skills_data["physical_skills"], **self.skills_data["spell_skills"]}
        
        for skill_id, skill in all_skills.items():
            if (skill_id not in self.learned_skills and 
                character_power >= skill["power_requirement"]):
                available.append((skill_id, skill))
        return available
    
    def learn_skill(self, skill_id):
        if skill_id not in self.learned_skills:
            self.learned_skills.append(skill_id)
            all_skills = {**self.skills_data["martial_arts"], **self.skills_data["spells"]}
            skill = all_skills[skill_id]
            event_bus.emit("skill_learned", {"id": skill_id, "skill": skill})
            return True
        return False
    
    def get_learned_skills(self):
        result = []
        all_skills = {**self.skills_data["physical_skills"], **self.skills_data["spell_skills"]}
        for skill_id in self.learned_skills:
            if skill_id in all_skills:
                result.append((skill_id, all_skills[skill_id]))
        return result
        
    def get_total_attack_power(self):
        physical_attack = 0
        spell_attack = 0
        all_skills = {**self.skills_data["physical_skills"], **self.skills_data["spell_skills"]}
        
        for skill_id in self.learned_skills:
            if skill_id in all_skills:
                skill = all_skills[skill_id]
                if skill["type"] == "physical":
                    physical_attack += skill.get("physical_attack", 0)
                elif skill["type"] == "spell":
                    spell_attack += skill.get("spell_attack", 0)
                    
        return physical_attack, spell_attack