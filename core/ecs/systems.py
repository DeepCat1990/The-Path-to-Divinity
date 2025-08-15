from abc import ABC, abstractmethod
from .entity import EntityManager
from ..events import event_bus

class System(ABC):
    """系统基类"""
    
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    @abstractmethod
    def update(self, delta_time: float):
        """更新系统逻辑"""
        pass

class AttributeSystem(System):
    """属性系统 - 处理属性变化和计算"""
    
    def update(self, delta_time: float):
        entities = self.entity_manager.get_entities_with_components("AttributeComponent")
        
        for entity in entities:
            attr = entity.get_component("AttributeComponent")
            
            # 生命值回复
            if attr.health < attr.max_health:
                attr.health = min(attr.max_health, attr.health + 1)
            
            # 法力值回复
            if attr.mana < attr.max_mana:
                attr.mana = min(attr.max_mana, attr.mana + 2)

class StateSystem(System):
    """状态系统 - 处理Buff/Debuff效果"""
    
    def update(self, delta_time: float):
        entities = self.entity_manager.get_entities_with_components("StateComponent")
        
        for entity in entities:
            state = entity.get_component("StateComponent")
            
            # 处理Buff持续时间
            expired_buffs = []
            for buff_id, buff_data in state.buffs.items():
                if "duration" in buff_data:
                    buff_data["duration"] -= delta_time
                    if buff_data["duration"] <= 0:
                        expired_buffs.append(buff_id)
            
            # 移除过期Buff
            for buff_id in expired_buffs:
                del state.buffs[buff_id]
                event_bus.emit("buff_expired", {"entity_id": entity.id, "buff_id": buff_id})

class CombatSystem(System):
    """战斗系统 - 处理战斗逻辑"""
    
    def update(self, delta_time: float):
        # 处理战斗相关逻辑
        pass
    
    def cast_spell(self, caster_id: str, spell_id: str, target_id: str = None):
        """施放法术"""
        caster = self.entity_manager.get_entity(caster_id)
        if not caster:
            return False
        
        attr = caster.get_component("AttributeComponent")
        skills = caster.get_component("SkillComponent")
        
        if not attr or not skills or spell_id not in skills.learned_spells:
            return False
        
        # 从数据核心获取法术信息
        from ..data_core import data_core
        spell_data = data_core.get_spell(spell_id)
        
        if not spell_data or attr.mana < spell_data.get("cost", {}).get("mana", 0):
            return False
        
        # 消耗法力
        attr.mana -= spell_data["cost"]["mana"]
        
        # 发布施法事件
        event_bus.emit("spell_cast", {
            "caster_id": caster_id,
            "spell_id": spell_id,
            "target_id": target_id,
            "spell_data": spell_data
        })
        
        return True

class InventorySystem(System):
    """背包系统 - 处理物品管理"""
    
    def update(self, delta_time: float):
        pass
    
    def use_item(self, entity_id: str, item_id: str):
        """使用物品"""
        entity = self.entity_manager.get_entity(entity_id)
        if not entity:
            return False
        
        inventory = entity.get_component("InventoryComponent")
        if not inventory or not inventory.remove_item(item_id, 1):
            return False
        
        # 从数据核心获取物品信息
        from ..data_core import data_core
        item_data = data_core.get_item(item_id)
        
        if item_data and "effects" in item_data:
            self._apply_item_effects(entity, item_data["effects"])
        
        event_bus.emit("item_used", {"entity_id": entity_id, "item_id": item_id})
        return True
    
    def _apply_item_effects(self, entity, effects):
        """应用物品效果"""
        attr = entity.get_component("AttributeComponent")
        if not attr:
            return
        
        if "mana_restore" in effects:
            attr.mana = min(attr.max_mana, attr.mana + effects["mana_restore"])
        if "health_restore" in effects:
            attr.health = min(attr.max_health, attr.health + effects["health_restore"])