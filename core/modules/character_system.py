from ..events import event_bus
from ..data_core import data_core

class CharacterSystem:
    """角色系统 - 管理角色成长和生命周期"""
    
    def __init__(self, world_manager):
        self.world_manager = world_manager
        self.experience_table = {1: 100, 2: 250, 3: 500, 4: 1000, 5: 2000}
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("experience_gained", self._handle_experience_gained)
        event_bus.subscribe("character_death", self._handle_character_death)
        event_bus.subscribe("realm_breakthrough", self._handle_realm_breakthrough)
    
    def _handle_experience_gained(self, event_data):
        """处理经验获得事件"""
        entity_id = event_data["entity_id"]
        exp_amount = event_data["amount"]
        
        entity = self.world_manager.get_entity(entity_id)
        if not entity:
            return
        
        attr = entity.get_component("AttributeComponent")
        if not attr:
            return
        
        # 增加经验
        if not hasattr(attr, 'experience'):
            attr.experience = 0
            attr.level = 1
        
        attr.experience += exp_amount
        
        # 检查升级
        required_exp = self.experience_table.get(attr.level, attr.level * 1000)
        if attr.experience >= required_exp:
            self._level_up(entity_id, attr)
    
    def _level_up(self, entity_id, attr):
        """角色升级"""
        attr.level += 1
        attr.experience = 0
        
        # 属性提升
        attr.max_health += 20
        attr.health = attr.max_health
        attr.max_mana += 15
        attr.mana = attr.max_mana
        
        event_bus.emit("level_up", {
            "entity_id": entity_id,
            "new_level": attr.level
        })
        event_bus.emit("message", f"升级了！当前等级: {attr.level}")
    
    def _handle_character_death(self, event_data):
        """处理角色死亡事件"""
        entity_id = event_data["entity_id"]
        event_bus.emit("message", "角色已死亡，修仙之路就此结束...")
    
    def _handle_realm_breakthrough(self, event_data):
        """处理境界突破事件"""
        entity_id = event_data["entity_id"]
        new_realm = event_data["realm"]
        
        entity = self.world_manager.get_entity(entity_id)
        if not entity:
            return
        
        state = entity.get_component("StateComponent")
        attr = entity.get_component("AttributeComponent")
        
        if state and attr:
            state.realm = new_realm
            
            # 从数据核心获取境界信息
            realm_data = data_core.get_realm(new_realm)
            if realm_data:
                # 应用境界加成
                multipliers = realm_data["attribute_multipliers"]
                attr.max_health = int(attr.max_health * multipliers["health"])
                attr.max_mana = int(attr.max_mana * multipliers["mana"])
                attr.lifespan += realm_data["lifespan_bonus"]
                
                event_bus.emit("message", f"突破到 {realm_data['name']} 境界！")
    
    def check_breakthrough_conditions(self, entity_id):
        """检查突破条件"""
        entity = self.world_manager.get_entity(entity_id)
        if not entity:
            return False
        
        state = entity.get_component("StateComponent")
        attr = entity.get_component("AttributeComponent")
        
        if not state or not attr:
            return False
        
        current_realm_data = data_core.get_realm(state.realm)
        if not current_realm_data or "next_realm" not in current_realm_data:
            return False
        
        requirements = current_realm_data["breakthrough_requirements"]
        
        # 检查各种突破条件
        if "comprehension" in requirements and attr.comprehension < requirements["comprehension"]:
            return False
        
        # 如果满足条件，触发突破
        next_realm = current_realm_data["next_realm"]
        event_bus.emit("realm_breakthrough", {
            "entity_id": entity_id,
            "realm": next_realm
        })
        return True