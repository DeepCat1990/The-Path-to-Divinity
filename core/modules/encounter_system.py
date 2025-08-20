import random
from abc import ABC, abstractmethod
from ..events import event_bus
from ..data_core import data_core

class Trigger(ABC):
    """触发器基类"""
    
    @abstractmethod
    def check_condition(self, entity_id, context):
        """检查触发条件"""
        pass

class LocationTrigger(Trigger):
    """位置触发器"""
    
    def __init__(self, location):
        self.location = location
    
    def check_condition(self, entity_id, context):
        return context.get("location") == self.location

class AttributeTrigger(Trigger):
    """属性触发器"""
    
    def __init__(self, attribute, threshold, comparison=">="):
        self.attribute = attribute
        self.threshold = threshold
        self.comparison = comparison
    
    def check_condition(self, entity_id, context):
        world_manager = context.get("world_manager")
        if not world_manager:
            return False
        
        entity = world_manager.get_entity(entity_id)
        if not entity:
            return False
        
        attr = entity.get_component("AttributeComponent")
        if not attr:
            return False
        
        value = getattr(attr, self.attribute, 0)
        
        if self.comparison == ">=":
            return value >= self.threshold
        elif self.comparison == "<=":
            return value <= self.threshold
        elif self.comparison == "==":
            return value == self.threshold
        
        return False

class TimeTrigger(Trigger):
    """时间触发器"""
    
    def __init__(self, day_condition):
        self.day_condition = day_condition
    
    def check_condition(self, entity_id, context):
        current_day = context.get("current_day", 1)
        if isinstance(current_day, dict):
            current_day = current_day.get('new_day', 1)
        return current_day % self.day_condition == 0

class EncounterSystem:
    """奇遇系统 - 管理随机事件和奇遇"""
    
    def __init__(self, world_manager):
        self.world_manager = world_manager
        self.active_encounters = {}
        self.triggers = []
        self._setup_event_handlers()
        self._initialize_triggers()
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("day_changed", self._check_daily_encounters)
        event_bus.subscribe("location_changed", self._check_location_encounters)
        event_bus.subscribe("encounter_choice", self._handle_encounter_choice)
    
    def _initialize_triggers(self):
        """初始化触发器"""
        self.triggers = [
            LocationTrigger("mountain"),
            LocationTrigger("wilderness"),
            AttributeTrigger("health", 30, "<="),
            TimeTrigger(7)  # 每7天触发一次
        ]
    
    def _check_daily_encounters(self, day_data):
        """检查每日奇遇"""
        current_day = day_data.get('new_day', day_data) if isinstance(day_data, dict) else day_data
        context = {
            "current_day": current_day,
            "world_manager": self.world_manager
        }
        
        # 获取玩家实体（假设只有一个玩家）
        player_entities = self.world_manager.entity_manager.get_entities_with_components("AttributeComponent", "StateComponent")
        
        for entity in player_entities:
            self._check_encounters_for_entity(entity.id, context)
    
    def _check_location_encounters(self, event_data):
        """检查位置相关奇遇"""
        entity_id = event_data["entity_id"]
        location = event_data["location"]
        
        context = {
            "location": location,
            "world_manager": self.world_manager
        }
        
        self._check_encounters_for_entity(entity_id, context)
    
    def _check_encounters_for_entity(self, entity_id, context):
        """为特定实体检查奇遇"""
        # 检查所有触发器
        for trigger in self.triggers:
            if trigger.check_condition(entity_id, context):
                self._try_trigger_encounter(entity_id, context)
                break
    
    def _try_trigger_encounter(self, entity_id, context):
        """尝试触发奇遇"""
        encounters_data = data_core.get_encounter()
        if not encounters_data:
            return
        
        # 随机选择一个奇遇
        encounter_list = list(encounters_data["encounters"].values())
        available_encounters = []
        
        for encounter in encounter_list:
            # 检查触发条件
            trigger_conditions = encounter.get("trigger_conditions", {})
            probability = trigger_conditions.get("probability", 0.1)
            
            if random.random() < probability:
                # 检查其他条件
                if self._check_encounter_requirements(entity_id, trigger_conditions):
                    available_encounters.append(encounter)
        
        if available_encounters:
            encounter = random.choice(available_encounters)
            self._start_encounter(entity_id, encounter)
    
    def _check_encounter_requirements(self, entity_id, requirements):
        """检查奇遇需求"""
        entity = self.world_manager.get_entity(entity_id)
        if not entity:
            return False
        
        state = entity.get_component("StateComponent")
        if "realm" in requirements:
            required_realm = requirements["realm"]
            if not state or state.realm != required_realm:
                return False
        
        return True
    
    def _start_encounter(self, entity_id, encounter):
        """开始奇遇"""
        encounter_id = encounter["id"]
        self.active_encounters[entity_id] = encounter
        
        event_bus.emit("encounter_started", {
            "entity_id": entity_id,
            "encounter_id": encounter_id,
            "encounter": encounter
        })
        
        event_bus.emit("message", f"奇遇：{encounter['name']}")
        event_bus.emit("message", encounter["description"])
        
        # 显示选择项
        for i, choice in enumerate(encounter.get("choices", [])):
            event_bus.emit("message", f"{i+1}. {choice['text']}")
    
    def _handle_encounter_choice(self, event_data):
        """处理奇遇选择"""
        entity_id = event_data["entity_id"]
        choice_index = event_data["choice_index"]
        
        if entity_id not in self.active_encounters:
            return
        
        encounter = self.active_encounters[entity_id]
        choices = encounter.get("choices", [])
        
        if 0 <= choice_index < len(choices):
            choice = choices[choice_index]
            self._execute_choice_outcome(entity_id, choice)
        
        # 结束奇遇
        del self.active_encounters[entity_id]
    
    def _execute_choice_outcome(self, entity_id, choice):
        """执行选择结果"""
        outcomes = choice.get("outcomes", [])
        
        # 根据概率选择结果
        rand = random.random()
        cumulative_prob = 0
        
        for outcome in outcomes:
            cumulative_prob += outcome["probability"]
            if rand <= cumulative_prob:
                self._apply_outcome(entity_id, outcome)
                break
    
    def _handle_combat_outcome(self, entity_id, combat_data):
        """处理战斗结果"""
        enemy_data = {
            "name": combat_data.get("enemy", "未知敌人"),
            "health": combat_data.get("level", 1) * 30,
            "attack": combat_data.get("level", 1) * 10,
            "defense": combat_data.get("level", 1) * 3
        }
        
        # 通过战斗系统处理战斗
        if hasattr(self.world_manager, 'combat_system'):
            self.world_manager.combat_system.handle_encounter_combat(entity_id, enemy_data)
        else:
            # 备用简单战斗
            event_bus.emit("message", f"与{enemy_data['name']}展开激战！")
            if random.random() < 0.7:  # 70%胜率
                event_bus.emit("message", "胜利！")
            else:
                event_bus.emit("message", "失败...")
                entity = self.world_manager.get_entity(entity_id)
                if entity:
                    attr = entity.get_component("AttributeComponent")
                    if attr:
                        attr.health = max(1, attr.health - 20)
    
    def _apply_outcome(self, entity_id, outcome):
        """应用结果"""
        entity = self.world_manager.get_entity(entity_id)
        if not entity:
            return
        
        result = outcome.get("result")
        rewards = outcome.get("rewards", {})
        combat = outcome.get("combat")
        
        # 处理战斗结果
        if combat:
            self._handle_combat_outcome(entity_id, combat)
            return
        
        # 应用物品奖励
        if "items" in rewards:
            inventory = entity.get_component("InventoryComponent")
            if inventory:
                for item in rewards["items"]:
                    inventory.add_item(item["id"], item["count"])
                    event_bus.emit("message", f"获得 {item['id']} x{item['count']}")
        
        # 应用经验奖励
        if "experience" in rewards:
            event_bus.emit("experience_gained", {
                "entity_id": entity_id,
                "amount": rewards["experience"]
            })
        
        # 应用功法奖励
        if "gongfa" in rewards:
            skills = entity.get_component("SkillComponent")
            if skills:
                gongfa_id = rewards["gongfa"]
                if gongfa_id not in skills.learned_gongfa:
                    skills.learned_gongfa.append(gongfa_id)
                    event_bus.emit("message", f"学会了功法：{gongfa_id}")
        
        # 显示结果消息
        if result == "treasure_found":
            event_bus.emit("message", "你发现了宝物！")
        elif result == "ancient_inheritance":
            event_bus.emit("message", "你获得了古代传承！")
        elif result == "safe_retreat":
            event_bus.emit("message", "你安全地离开了。")
    
    def make_choice(self, entity_id, choice_index):
        """玩家做出选择"""
        event_bus.emit("encounter_choice", {
            "entity_id": entity_id,
            "choice_index": choice_index
        })