import json
from .events import event_bus

class SkillManager:
    def __init__(self):
        with open("data/skills.json", "r", encoding="utf-8") as f:
            self.skills_data = json.load(f)
        self.learned_skills = []
        
    def get_available_skills(self, character_power):
        available = []
        all_skills = self._get_all_skills()
        
        for skill_id, skill in all_skills.items():
            if (skill_id not in self.learned_skills and 
                character_power >= skill.get("power_requirement", 0)):
                available.append((skill_id, skill))
        return available
    
    def learn_skill(self, skill_id):
        if skill_id not in self.learned_skills:
            self.learned_skills.append(skill_id)
            all_skills = self._get_all_skills()
            skill = all_skills.get(skill_id, {})
            event_bus.emit("skill_learned", {"id": skill_id, "skill": skill})
            return True
        return False
    
    def get_learned_skills(self):
        result = []
        all_skills = self._get_all_skills()
            
        for skill_id in self.learned_skills:
            if skill_id in all_skills:
                result.append((skill_id, all_skills[skill_id]))
        return result
        
    def get_total_attack_power(self):
        physical_attack = 0
        spell_attack = 0
        all_skills = self._get_all_skills()
        
        for skill_id in self.learned_skills:
            if skill_id in all_skills:
                skill = all_skills[skill_id]
                if skill.get("type") == "physical":
                    physical_attack += skill.get("physical_attack", 0)
                elif skill.get("type") == "spell":
                    spell_attack += skill.get("spell_attack", 0)
                    
        return physical_attack, spell_attack
    
    def _get_all_skills(self):
        """获取所有技能数据"""
        all_skills = {}
        
        # 加载基础技能
        if "physical_skills" in self.skills_data:
            all_skills.update(self.skills_data["physical_skills"])
        if "spell_skills" in self.skills_data:
            all_skills.update(self.skills_data["spell_skills"])
        
        # 兼容旧数据结构
        if "martial_arts" in self.skills_data:
            all_skills.update(self.skills_data["martial_arts"])
        if "spells" in self.skills_data:
            all_skills.update(self.skills_data["spells"])
        
        # 加载门派技能
        try:
            with open("data/sects.json", "r", encoding="utf-8") as f:
                sects_data = json.load(f)
                all_skills.update(sects_data.get("sect_skills", {}))
        except:
            pass
            
        return all_skills