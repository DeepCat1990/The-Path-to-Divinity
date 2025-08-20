import random
import json
from ..events import event_bus
from ..data_core import data_core

class MartialSystem:
    """武学体系 - 太吾传人武学管理"""
    
    def __init__(self):
        self.config = self._load_config()
        self.auto_training = False
        self.training_focus = "balanced"  # balanced, internal, external, agility, special
        self._setup_event_handlers()
    
    def _load_config(self):
        try:
            with open("data/martial_system.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return self._get_default_config()
    
    def _get_default_config(self):
        return {
            "martial_types": {
                "internal": {"name": "内功", "description": "修炼内力，提升法力和恢复"},
                "external": {"name": "外功", "description": "锻炼体魄，提升攻击和防御"},
                "agility": {"name": "身法", "description": "提升速度和闪避"},
                "special": {"name": "绝技", "description": "特殊技能和奥义"}
            },
            "recommended_builds": [
                {
                    "name": "刚猛路线",
                    "description": "以外功为主，内功为辅",
                    "focus": ["external", "internal"],
                    "skills": ["iron_body", "tiger_fist", "basic_internal"]
                },
                {
                    "name": "灵巧路线", 
                    "description": "身法配合绝技",
                    "focus": ["agility", "special"],
                    "skills": ["light_step", "shadow_clone", "swift_strike"]
                },
                {
                    "name": "内力路线",
                    "description": "深厚内功配合法术",
                    "focus": ["internal", "special"],
                    "skills": ["deep_meditation", "qi_burst", "energy_shield"]
                }
            ]
        }
    
    def _setup_event_handlers(self):
        event_bus.subscribe("auto_training_toggle", self._handle_auto_training)
        event_bus.subscribe("training_focus_change", self._handle_focus_change)
        event_bus.subscribe("martial_learn_request", self._handle_learn_request)
    
    def get_available_martials(self, character_id):
        """获取可学习的武学"""
        from ..world_manager import world_manager
        from ..ecs.components import AttributeComponent, StateComponent
        
        if not world_manager.has_component(character_id, AttributeComponent):
            return []
        
        attrs = world_manager.get_component(character_id, AttributeComponent)
        state = world_manager.get_component(character_id, StateComponent)
        
        available = []
        
        # 基础武学 - 总是可学
        basic_martials = [
            {
                "id": "basic_internal",
                "name": "基础内功",
                "type": "internal",
                "level": 1,
                "requirements": {"constitution": 3},
                "effects": {"max_mana": 10, "mana_regen": 2},
                "description": "基础的内力修炼法门"
            },
            {
                "id": "basic_external", 
                "name": "基础外功",
                "type": "external",
                "level": 1,
                "requirements": {"constitution": 4},
                "effects": {"physical_attack": 5, "defense": 3},
                "description": "强身健体的外功心法"
            },
            {
                "id": "basic_agility",
                "name": "基础身法",
                "type": "agility", 
                "level": 1,
                "requirements": {"constitution": 3},
                "effects": {"dodge": 10, "speed": 5},
                "description": "轻功身法的入门功夫"
            }
        ]
        
        # 检查学习条件
        for martial in basic_martials:
            can_learn = True
            for req_attr, req_value in martial["requirements"].items():
                if getattr(attrs, req_attr, 0) < req_value:
                    can_learn = False
                    break
            
            if can_learn:
                available.append(martial)
        
        # 高级武学 - 需要前置条件
        if attrs.constitution >= 6:
            available.extend([
                {
                    "id": "iron_body",
                    "name": "铁布衫",
                    "type": "external",
                    "level": 2,
                    "requirements": {"constitution": 6, "prerequisite": "basic_external"},
                    "effects": {"defense": 8, "health": 20},
                    "description": "刀枪不入的护体神功"
                },
                {
                    "id": "tiger_fist",
                    "name": "猛虎拳",
                    "type": "external",
                    "level": 2,
                    "requirements": {"constitution": 6, "prerequisite": "basic_external"},
                    "effects": {"physical_attack": 12, "crit_rate": 0.1},
                    "description": "威猛霸道的拳法"
                }
            ])
        
        if attrs.comprehension >= 7:
            available.extend([
                {
                    "id": "deep_meditation",
                    "name": "深层冥想",
                    "type": "internal",
                    "level": 2,
                    "requirements": {"comprehension": 7, "prerequisite": "basic_internal"},
                    "effects": {"max_mana": 25, "spell_attack": 8},
                    "description": "深入内心的修炼法门"
                }
            ])
        
        return available
    
    def learn_martial(self, character_id, martial_id):
        """学习武学"""
        from ..world_manager import world_manager
        from ..ecs.components import SkillComponent
        
        if not world_manager.has_component(character_id, SkillComponent):
            return False
        
        skills = world_manager.get_component(character_id, SkillComponent)
        available = self.get_available_martials(character_id)
        
        # 查找武学
        martial = None
        for m in available:
            if m["id"] == martial_id:
                martial = m
                break
        
        if not martial:
            event_bus.emit("message", "无法学习此武学")
            return False
        
        # 检查是否已学会
        if martial_id in skills.learned_gongfa:
            event_bus.emit("message", f"已经学会了{martial['name']}")
            return False
        
        # 学习成功
        skills.learned_gongfa.append(martial_id)
        
        # 应用效果
        self._apply_martial_effects(character_id, martial)
        
        event_bus.emit("martial_learned", {
            "character_id": character_id,
            "martial": martial
        })
        event_bus.emit("message", f"学会了{martial['name']}！")
        
        return True
    
    def _apply_martial_effects(self, character_id, martial):
        """应用武学效果"""
        from ..world_manager import world_manager
        from ..ecs.components import AttributeComponent
        
        if not world_manager.has_component(character_id, AttributeComponent):
            return
        
        attrs = world_manager.get_component(character_id, AttributeComponent)
        effects = martial.get("effects", {})
        
        # 应用属性加成
        for effect, value in effects.items():
            if effect == "max_mana":
                attrs.max_mana += value
                attrs.mana = min(attrs.mana + value, attrs.max_mana)
            elif effect == "max_health":
                attrs.max_health += value
                attrs.health = min(attrs.health + value, attrs.max_health)
            elif effect == "physical_attack":
                attrs.physical_attack += value
            elif effect == "spell_attack":
                attrs.spell_attack += value
            elif effect == "defense":
                attrs.defense += value
    
    def auto_train_martials(self, character_id):
        """自动修炼武学"""
        if not self.auto_training:
            return
        
        from ..world_manager import world_manager
        from ..ecs.components import SkillComponent, AttributeComponent
        
        if not world_manager.has_component(character_id, SkillComponent):
            return
        
        skills = world_manager.get_component(character_id, SkillComponent)
        attrs = world_manager.get_component(character_id, AttributeComponent)
        
        # 根据修炼重点自动学习
        available = self.get_available_martials(character_id)
        
        if self.training_focus == "balanced":
            # 平衡发展 - 优先学基础武学
            priorities = ["basic_internal", "basic_external", "basic_agility"]
        elif self.training_focus == "internal":
            priorities = ["basic_internal", "deep_meditation"]
        elif self.training_focus == "external":
            priorities = ["basic_external", "iron_body", "tiger_fist"]
        elif self.training_focus == "agility":
            priorities = ["basic_agility", "light_step"]
        else:
            priorities = []
        
        # 尝试学习优先级武学
        for martial_id in priorities:
            if martial_id not in skills.learned_gongfa:
                if self.learn_martial(character_id, martial_id):
                    break
    
    def get_recommended_build(self, character_id):
        """获取推荐的武学搭配"""
        from ..world_manager import world_manager
        from ..ecs.components import AttributeComponent
        
        if not world_manager.has_component(character_id, AttributeComponent):
            return None
        
        attrs = world_manager.get_component(character_id, AttributeComponent)
        
        # 根据属性推荐搭配
        if attrs.constitution >= 7:
            return self.config["recommended_builds"][0]  # 刚猛路线
        elif attrs.comprehension >= 7:
            return self.config["recommended_builds"][2]  # 内力路线
        else:
            return self.config["recommended_builds"][1]  # 灵巧路线
    
    def get_martial_synergy(self, martial_list):
        """获取武学协同效应"""
        synergies = []
        
        # 检查常见组合
        if "basic_internal" in martial_list and "basic_external" in martial_list:
            synergies.append({
                "name": "内外兼修",
                "description": "内功外功并重，攻防平衡",
                "bonus": {"all_attributes": 1}
            })
        
        if "iron_body" in martial_list and "tiger_fist" in martial_list:
            synergies.append({
                "name": "刚猛无双",
                "description": "攻防俱佳的刚猛路线",
                "bonus": {"physical_attack": 3, "defense": 3}
            })
        
        return synergies
    
    def _handle_auto_training(self, event_data):
        """处理自动修炼开关"""
        self.auto_training = event_data.get("enabled", False)
        event_bus.emit("message", f"自动修炼{'开启' if self.auto_training else '关闭'}")
    
    def _handle_focus_change(self, event_data):
        """处理修炼重点变更"""
        self.training_focus = event_data.get("focus", "balanced")
        focus_names = {
            "balanced": "平衡发展",
            "internal": "内功专精",
            "external": "外功专精", 
            "agility": "身法专精",
            "special": "绝技专精"
        }
        focus_name = focus_names.get(self.training_focus, "未知")
        event_bus.emit("message", f"修炼重点调整为：{focus_name}")
    
    def _handle_learn_request(self, event_data):
        """处理学习请求"""
        character_id = event_data.get("character_id")
        martial_id = event_data.get("martial_id")
        
        if character_id and martial_id:
            self.learn_martial(character_id, martial_id)

class CombatStrategy:
    """战斗策略系统"""
    
    def __init__(self):
        self.strategies = {
            "aggressive": {
                "name": "激进攻击",
                "description": "优先使用攻击技能",
                "priority": ["attack", "special", "defend"]
            },
            "defensive": {
                "name": "稳健防守", 
                "description": "优先防御和恢复",
                "priority": ["defend", "heal", "attack"]
            },
            "balanced": {
                "name": "攻防平衡",
                "description": "根据情况灵活应对",
                "priority": ["attack", "defend", "special"]
            }
        }
        self.current_strategy = "balanced"
    
    def set_strategy(self, strategy_name):
        """设置战斗策略"""
        if strategy_name in self.strategies:
            self.current_strategy = strategy_name
            event_bus.emit("combat_strategy_changed", {
                "strategy": strategy_name,
                "description": self.strategies[strategy_name]["description"]
            })
    
    def get_next_action(self, character_id, combat_state):
        """根据策略获取下一个行动"""
        strategy = self.strategies[self.current_strategy]
        
        # 简化的AI决策
        health_ratio = combat_state.get("health_ratio", 1.0)
        enemy_health_ratio = combat_state.get("enemy_health_ratio", 1.0)
        
        if health_ratio < 0.3:
            return "heal"  # 血量低时优先治疗
        elif enemy_health_ratio < 0.2:
            return "special"  # 敌人血量低时使用绝技
        else:
            # 按策略优先级选择
            return strategy["priority"][0]