import time
from typing import List
from .ecs.entity import EntityManager
from .ecs.systems import System, AttributeSystem, StateSystem, CombatSystem, InventorySystem
from .ecs.components import AttributeComponent, SkillComponent, StateComponent, InventoryComponent, EquipmentComponent
from .events import event_bus
from .data_core import data_core
from .modules.character_system import CharacterSystem
from .modules.spell_system import SpellSystem
from .modules.encounter_system import EncounterSystem
from .modules.combat_system import CombatSystem as ModuleCombatSystem

class WorldManager:
    """游戏世界管理器 - 管理ECS和游戏主循环"""
    
    def __init__(self):
        self.entity_manager = EntityManager()
        self.systems: List[System] = []
        self.running = False
        self.last_update_time = time.time()
        self.game_time = 0.0
        self.day_length = 60.0  # 一天60秒
        self.current_day = 1
        
        self._initialize_systems()
        self._initialize_modules()
        self._setup_event_handlers()
    
    def _initialize_systems(self):
        """初始化所有系统"""
        self.systems = [
            AttributeSystem(self.entity_manager),
            StateSystem(self.entity_manager),
            CombatSystem(self.entity_manager),
            InventorySystem(self.entity_manager)
        ]
        
    def _initialize_modules(self):
        """初始化功能模块"""
        self.character_system = CharacterSystem(self)
        self.spell_system = SpellSystem(self)
        self.encounter_system = EncounterSystem(self)
        self.combat_system = ModuleCombatSystem(self)
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("spell_cast", self._handle_spell_cast)
        event_bus.subscribe("item_used", self._handle_item_used)
    
    def create_player_entity(self) -> str:
        """创建玩家实体"""
        entity = self.entity_manager.create_entity()
        
        # 从数据核心获取角色模板
        template = data_core.get_character_template()
        base_attrs = template["base_attributes"]
        initial_stats = template["initial_stats"]
        
        # 添加组件
        entity.add_component("AttributeComponent", AttributeComponent(
            health=initial_stats["health"],
            max_health=initial_stats["health"],
            mana=initial_stats["mana"],
            max_mana=initial_stats["mana"],
            lifespan=initial_stats["lifespan"],
            age=initial_stats["age"]
        ))
        
        entity.add_component("SkillComponent", SkillComponent())
        entity.add_component("StateComponent", StateComponent())
        entity.add_component("InventoryComponent", InventoryComponent())
        entity.add_component("EquipmentComponent", EquipmentComponent())
        
        return entity.id
    
    def update(self):
        """更新游戏世界"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 更新游戏时间
        self.game_time += delta_time
        new_day = int(self.game_time / self.day_length) + 1
        
        if new_day > self.current_day:
            self.current_day = new_day
            event_bus.emit("day_changed", self.current_day)
            self._process_daily_events()
        
        # 更新所有系统
        for system in self.systems:
            system.update(delta_time)
            
        # 模块不需要更新，它们通过事件响应
    
    def _process_daily_events(self):
        """处理每日事件"""
        # 角色老化
        entities = self.entity_manager.get_entities_with_components("AttributeComponent")
        for entity in entities:
            attr = entity.get_component("AttributeComponent")
            attr.age += 1
            
            # 检查寿命
            if attr.age >= attr.lifespan:
                event_bus.emit("character_death", {"entity_id": entity.id})
    
    def _handle_spell_cast(self, event_data):
        """处理施法事件"""
        spell_data = event_data["spell_data"]
        target_id = event_data.get("target_id")
        
        if target_id and "damage" in spell_data.get("effects", {}):
            target = self.entity_manager.get_entity(target_id)
            if target:
                attr = target.get_component("AttributeComponent")
                if attr:
                    damage = spell_data["effects"]["damage"]
                    attr.health = max(0, attr.health - damage)
                    
                    if attr.health == 0:
                        event_bus.emit("entity_death", {"entity_id": target_id})
    
    def _handle_item_used(self, event_data):
        """处理物品使用事件"""
        pass
    
    def get_entity(self, entity_id: str):
        """获取实体"""
        return self.entity_manager.get_entity(entity_id)
    
    def start(self):
        """启动世界管理器"""
        self.running = True
        self.last_update_time = time.time()
    
    def stop(self):
        """停止世界管理器"""
        self.running = False

# 全局世界管理器实例
world_manager = WorldManager()