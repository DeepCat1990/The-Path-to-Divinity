import json
import random
from ..events import event_bus
from ..data_core import data_core

class TaiwuTimeSystem:
    """太吾时间系统 - 以月为单位的时间流逝"""
    
    def __init__(self):
        self.current_month = 1
        self.current_year = 1
        self.config = self._load_config()
        self._setup_event_handlers()
    
    def _load_config(self):
        try:
            with open("data/taiwu_system.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    
    def _setup_event_handlers(self):
        event_bus.subscribe("month_passed", self._handle_month_change)
    
    def advance_month(self):
        """推进一个月"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        
        event_bus.emit("month_passed", {
            "month": self.current_month,
            "year": self.current_year,
            "total_months": (self.current_year - 1) * 12 + self.current_month
        })
    
    def _handle_month_change(self, time_data):
        """处理月份变化"""
        total_months = time_data["total_months"]
        
        # 检查相枢入侵阶段
        self._check_xiangshu_phase(total_months)
        
        # 角色老化
        self._age_characters()
    
    def _check_xiangshu_phase(self, total_months):
        """检查相枢入侵阶段"""
        phases = self.config.get("xiangshu_invasion", {}).get("phases", [])
        
        for phase in phases:
            if total_months == phase["month_start"]:
                event_bus.emit("xiangshu_phase_change", phase)
                event_bus.emit("message", f"【相枢入侵】{phase['name']}: {phase['description']}")
    
    def _age_characters(self):
        """角色老化"""
        event_bus.emit("character_aging", {"months": 1})

class StanceSystem:
    """立场系统"""
    
    def __init__(self):
        self.config = self._load_config()
        self.player_stance = "neutral"
        self.stance_points = {"righteous": 0, "benevolent": 0, "neutral": 50, "rebellious": 0, "selfish": 0}
    
    def _load_config(self):
        try:
            with open("data/taiwu_system.json", "r", encoding="utf-8") as f:
                return json.load(f)["stances"]
        except:
            return {}
    
    def adjust_stance(self, stance_type, points):
        """调整立场点数"""
        if stance_type in self.stance_points:
            self.stance_points[stance_type] += points
            
            # 重新计算主导立场
            max_stance = max(self.stance_points, key=self.stance_points.get)
            if max_stance != self.player_stance and self.stance_points[max_stance] > 60:
                old_stance = self.player_stance
                self.player_stance = max_stance
                
                stance_name = self.config[max_stance]["name"]
                event_bus.emit("stance_changed", {
                    "old_stance": old_stance,
                    "new_stance": max_stance,
                    "stance_name": stance_name
                })
                event_bus.emit("message", f"你的立场转向了【{stance_name}】")
    
    def get_npc_reaction_modifier(self, npc_stance):
        """获取NPC反应修正"""
        if self.player_stance in self.config:
            reactions = self.config[self.player_stance].get("npc_reaction_bonus", {})
            return reactions.get(npc_stance, 0)
        return 0

class AptitudeSystem:
    """资质系统"""
    
    def __init__(self):
        self.config = self._load_config()
        self.aptitudes = self._generate_random_aptitudes()
    
    def _load_config(self):
        try:
            with open("data/taiwu_system.json", "r", encoding="utf-8") as f:
                return json.load(f)["aptitudes"]
        except:
            return {}
    
    def _generate_random_aptitudes(self):
        """生成随机资质"""
        aptitudes = {}
        
        for category, skills in self.config.items():
            aptitudes[category] = {}
            for skill_id, skill_data in skills.items():
                # 资质范围 1-10，平均值约5
                aptitude_value = max(1, min(10, int(random.gauss(5, 2))))
                aptitudes[category][skill_id] = aptitude_value
        
        return aptitudes
    
    def get_aptitude(self, category, skill):
        """获取特定技能的资质"""
        return self.aptitudes.get(category, {}).get(skill, 1)
    
    def get_learning_modifier(self, category, skill):
        """获取学习修正"""
        aptitude = self.get_aptitude(category, skill)
        return aptitude / 5.0  # 资质5为基准1.0倍速

class RegionSystem:
    """地区系统"""
    
    def __init__(self):
        self.config = self._load_config()
        self.current_region = "central_plains"
        self.discovered_regions = ["central_plains"]
    
    def _load_config(self):
        try:
            with open("data/taiwu_system.json", "r", encoding="utf-8") as f:
                return json.load(f)["regions"]
        except:
            return {}
    
    def travel_to_region(self, region_id):
        """前往地区"""
        if region_id in self.config:
            old_region = self.current_region
            self.current_region = region_id
            
            if region_id not in self.discovered_regions:
                self.discovered_regions.append(region_id)
                event_bus.emit("region_discovered", {"region_id": region_id})
            
            region_data = self.config[region_id]
            event_bus.emit("region_changed", {
                "old_region": old_region,
                "new_region": region_id,
                "region_data": region_data
            })
            
            event_bus.emit("message", f"来到了【{region_data['name']}】- {region_data['description']}")
            return True
        return False
    
    def get_current_region_data(self):
        """获取当前地区数据"""
        return self.config.get(self.current_region, {})
    
    def get_available_resources(self):
        """获取当前地区可用资源"""
        region_data = self.get_current_region_data()
        return region_data.get("resources", [])

class XiangshuSystem:
    """相枢入侵系统"""
    
    def __init__(self):
        self.config = self._load_config()
        self.current_phase = 0
        self.invasion_effects = {}
        self._setup_event_handlers()
    
    def _load_config(self):
        try:
            with open("data/taiwu_system.json", "r", encoding="utf-8") as f:
                return json.load(f)["xiangshu_invasion"]
        except:
            return {}
    
    def _setup_event_handlers(self):
        event_bus.subscribe("xiangshu_phase_change", self._handle_phase_change)
    
    def _handle_phase_change(self, phase_data):
        """处理相枢入侵阶段变化"""
        self.current_phase += 1
        self.invasion_effects = phase_data.get("effects", {})
        
        # 应用全局效果
        if "encounter_rate" in self.invasion_effects:
            event_bus.emit("global_modifier_changed", {
                "type": "encounter_rate",
                "value": self.invasion_effects["encounter_rate"]
            })
        
        if "danger_level" in self.invasion_effects:
            event_bus.emit("global_modifier_changed", {
                "type": "danger_level", 
                "value": self.invasion_effects["danger_level"]
            })
    
    def get_current_threat_level(self):
        """获取当前威胁等级"""
        return self.invasion_effects.get("danger_level", 1.0)
    
    def is_invasion_active(self):
        """是否正在入侵中"""
        return self.current_phase > 0