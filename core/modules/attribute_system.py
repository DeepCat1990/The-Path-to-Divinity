from ..events import event_bus
from ..ecs.components import AttributeComponent

class AttributeEffectSystem:
    """属性效果系统 - 处理六维属性对角色的影响"""
    
    def __init__(self):
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        event_bus.subscribe("day_changed", self._handle_daily_recovery)
        event_bus.subscribe("character_created", self._apply_initial_effects)
        event_bus.subscribe("attribute_changed", self._apply_attribute_effects)
    
    def _handle_daily_recovery(self, day):
        """处理每日恢复"""
        from ..world_manager import world_manager
        if hasattr(world_manager, 'player_entity_id'):
            self._apply_constitution_recovery(world_manager.player_entity_id)
    
    def _apply_constitution_recovery(self, entity_id):
        """应用体质的每日生命恢复"""
        from ..world_manager import world_manager
        if world_manager.has_component(entity_id, AttributeComponent):
            attrs = world_manager.get_component(entity_id, AttributeComponent)
            
            # 体质影响每日生命恢复
            constitution = getattr(attrs, 'constitution', 3)
            recovery_rate = max(1, constitution // 2)  # 体质每2点提供1点恢复
            
            if attrs.health < attrs.max_health:
                old_health = attrs.health
                attrs.health = min(attrs.max_health, attrs.health + recovery_rate)
                
                if attrs.health > old_health:
                    event_bus.emit("message", f"体质强健，恢复了 {attrs.health - old_health} 点生命值")
    
    def _apply_initial_effects(self, event_data):
        """应用初始属性效果"""
        entity_id = event_data.get("entity_id")
        if entity_id:
            self._calculate_attribute_effects(entity_id)
    
    def _apply_attribute_effects(self, event_data):
        """应用属性变化效果"""
        entity_id = event_data.get("entity_id")
        if entity_id:
            self._calculate_attribute_effects(entity_id)
    
    def _calculate_attribute_effects(self, entity_id):
        """计算属性对角色的影响"""
        from ..world_manager import world_manager
        if not world_manager.has_component(entity_id, AttributeComponent):
            return
        
        attrs = world_manager.get_component(entity_id, AttributeComponent)
        
        # 体质影响生命值和内外伤上限
        constitution = getattr(attrs, 'constitution', 3)
        base_health = 100
        health_bonus = (constitution - 3) * 15  # 每点体质增加15点生命
        new_max_health = base_health + health_bonus
        
        # 更新最大生命值
        if attrs.max_health != new_max_health:
            health_diff = new_max_health - attrs.max_health
            attrs.max_health = new_max_health
            attrs.health = min(attrs.health + health_diff, attrs.max_health)
        
        # 定力影响真气上限
        determination = getattr(attrs, 'determination', 3)
        base_mana = 50
        mana_bonus = (determination - 3) * 10  # 每点定力增加10点真气
        new_max_mana = base_mana + mana_bonus
        
        if attrs.max_mana != new_max_mana:
            mana_diff = new_max_mana - attrs.max_mana
            attrs.max_mana = new_max_mana
            attrs.mana = min(attrs.mana + mana_diff, attrs.max_mana)
        
        # 根骨影响功法发挥
        bone_root = getattr(attrs, 'bone_root', 3)
        martial_bonus = max(0, (bone_root - 3) * 2)  # 每点根骨增加2点武学威力
        
        # 魅力影响社交
        charm = attrs.charm
        social_bonus = (charm - 3) * 5  # 每点魅力增加5%社交成功率
        
        # 幸运影响随机事件
        luck = attrs.luck
        luck_modifier = (luck - 3) * 0.05  # 每点幸运增加5%好运概率
        
        # 存储计算结果到属性中
        if not hasattr(attrs, 'martial_bonus'):
            attrs.martial_bonus = martial_bonus
        else:
            attrs.martial_bonus = martial_bonus
            
        if not hasattr(attrs, 'social_bonus'):
            attrs.social_bonus = social_bonus
        else:
            attrs.social_bonus = social_bonus
            
        if not hasattr(attrs, 'luck_modifier'):
            attrs.luck_modifier = luck_modifier
        else:
            attrs.luck_modifier = luck_modifier