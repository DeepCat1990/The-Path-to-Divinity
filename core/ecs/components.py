from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class AttributeComponent:
    """属性组件 - 存储角色数值属性"""
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    constitution: int = 5
    comprehension: int = 5
    charm: int = 5
    luck: int = 5
    spiritual_root: int = 3
    physical_attack: int = 10
    spell_attack: int = 0
    defense: int = 5
    lifespan: int = 80
    age: int = 16

@dataclass
class SkillComponent:
    """技能组件 - 存储已学法术"""
    learned_spells: List[str] = None
    learned_gongfa: List[str] = None
    
    def __post_init__(self):
        if self.learned_spells is None:
            self.learned_spells = []
        if self.learned_gongfa is None:
            self.learned_gongfa = []

@dataclass
class StateComponent:
    """状态组件 - 存储当前状态效果"""
    realm: str = "mortal"
    sect: str = None
    buffs: Dict[str, Any] = None
    debuffs: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.buffs is None:
            self.buffs = {}
        if self.debuffs is None:
            self.debuffs = {}

@dataclass
class InventoryComponent:
    """背包组件 - 存储物品"""
    items: Dict[str, int] = None
    capacity: int = 100
    
    def __post_init__(self):
        if self.items is None:
            self.items = {}
    
    def add_item(self, item_id: str, count: int = 1):
        """添加物品"""
        if item_id in self.items:
            self.items[item_id] += count
        else:
            self.items[item_id] = count
    
    def remove_item(self, item_id: str, count: int = 1) -> bool:
        """移除物品"""
        if item_id in self.items and self.items[item_id] >= count:
            self.items[item_id] -= count
            if self.items[item_id] == 0:
                del self.items[item_id]
            return True
        return False

@dataclass
class EquipmentComponent:
    """装备组件 - 管理已穿戴装备"""
    weapon: str = None
    armor: str = None
    accessory: str = None
    
    def equip_item(self, slot: str, item_id: str):
        """装备物品"""
        if hasattr(self, slot):
            setattr(self, slot, item_id)
    
    def unequip_item(self, slot: str):
        """卸下装备"""
        if hasattr(self, slot):
            setattr(self, slot, None)

@dataclass
class PositionComponent:
    """位置组件 - 用于场景定位"""
    x: float = 0.0
    y: float = 0.0
    scene: str = "starting_village"