from abc import ABC, abstractmethod
from ..events import event_bus
from ..data_core import data_core

class EffectProcessor(ABC):
    """效果处理器基类"""
    
    @abstractmethod
    def process(self, caster_entity, target_entity, effect_data):
        """处理效果"""
        pass

class DamageEffect(EffectProcessor):
    """伤害效果处理器"""
    
    def process(self, caster_entity, target_entity, effect_data):
        if not target_entity:
            return
        
        target_attr = target_entity.get_component("AttributeComponent")
        if not target_attr:
            return
        
        damage = effect_data.get("damage", 0)
        
        # 计算最终伤害
        caster_attr = caster_entity.get_component("AttributeComponent")
        if caster_attr:
            damage += caster_attr.spell_attack * 0.1
        
        # 应用伤害
        target_attr.health = max(0, target_attr.health - int(damage))
        
        event_bus.emit("damage_dealt", {
            "target_id": target_entity.id,
            "damage": damage
        })

class HealEffect(EffectProcessor):
    """治疗效果处理器"""
    
    def process(self, caster_entity, target_entity, effect_data):
        if not target_entity:
            target_entity = caster_entity
        
        target_attr = target_entity.get_component("AttributeComponent")
        if not target_attr:
            return
        
        heal_amount = effect_data.get("heal_amount", 0)
        target_attr.health = min(target_attr.max_health, target_attr.health + heal_amount)
        
        event_bus.emit("healing_done", {
            "target_id": target_entity.id,
            "heal_amount": heal_amount
        })

class ApplyStateEffect(EffectProcessor):
    """状态效果处理器"""
    
    def process(self, caster_entity, target_entity, effect_data):
        if not target_entity:
            return
        
        state = target_entity.get_component("StateComponent")
        if not state:
            return
        
        state_id = effect_data.get("state_id")
        duration = effect_data.get("duration", 3)
        
        if state_id:
            state.debuffs[state_id] = {"duration": duration, "data": effect_data}
            
            event_bus.emit("state_applied", {
                "target_id": target_entity.id,
                "state_id": state_id
            })

class SpellSystem:
    """法术系统 - 管理法术施放和效果"""
    
    def __init__(self, world_manager):
        self.world_manager = world_manager
        self.effect_processors = {
            "damage": DamageEffect(),
            "heal": HealEffect(),
            "apply_state": ApplyStateEffect()
        }
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("request_cast_spell", self._handle_cast_spell_request)
        event_bus.subscribe("spell_cast", self._handle_spell_cast)
    
    def _handle_cast_spell_request(self, event_data):
        """处理施法请求"""
        caster_id = event_data["caster_id"]
        spell_id = event_data["spell_id"]
        target_id = event_data.get("target_id")
        
        if self._can_cast_spell(caster_id, spell_id):
            self._cast_spell(caster_id, spell_id, target_id)
    
    def _can_cast_spell(self, caster_id, spell_id):
        """检查是否可以施法"""
        caster = self.world_manager.get_entity(caster_id)
        if not caster:
            return False
        
        attr = caster.get_component("AttributeComponent")
        skills = caster.get_component("SkillComponent")
        state = caster.get_component("StateComponent")
        
        if not attr or not skills:
            return False
        
        # 检查是否学会法术
        if spell_id not in skills.learned_spells:
            return False
        
        # 检查法力值
        spell_data = data_core.get_spell(spell_id)
        if not spell_data:
            return False
        
        mana_cost = spell_data.get("cost", {}).get("mana", 0)
        if attr.mana < mana_cost:
            return False
        
        # 检查状态限制（如沉默）
        if state and "silence" in state.debuffs:
            return False
        
        return True
    
    def _cast_spell(self, caster_id, spell_id, target_id):
        """施放法术"""
        caster = self.world_manager.get_entity(caster_id)
        target = self.world_manager.get_entity(target_id) if target_id else None
        
        spell_data = data_core.get_spell(spell_id)
        if not spell_data:
            return
        
        # 消耗资源
        attr = caster.get_component("AttributeComponent")
        mana_cost = spell_data.get("cost", {}).get("mana", 0)
        attr.mana -= mana_cost
        
        # 发布施法事件
        event_bus.emit("spell_cast", {
            "caster_id": caster_id,
            "spell_id": spell_id,
            "target_id": target_id,
            "spell_data": spell_data
        })
    
    def _handle_spell_cast(self, event_data):
        """处理法术施放"""
        caster_id = event_data["caster_id"]
        target_id = event_data.get("target_id")
        spell_data = event_data["spell_data"]
        
        caster = self.world_manager.get_entity(caster_id)
        target = self.world_manager.get_entity(target_id) if target_id else None
        
        # 处理法术效果
        effects = spell_data.get("effects", {})
        
        # 伤害效果
        if "damage" in effects:
            self.effect_processors["damage"].process(caster, target, effects)
        
        # 治疗效果
        if "heal_amount" in effects:
            self.effect_processors["heal"].process(caster, target, effects)
        
        # 状态效果
        if "freeze_duration" in effects:
            freeze_effect = {
                "state_id": "frozen",
                "duration": effects["freeze_duration"]
            }
            self.effect_processors["apply_state"].process(caster, target, freeze_effect)
    
    def add_effect_processor(self, effect_type, processor):
        """添加新的效果处理器"""
        self.effect_processors[effect_type] = processor