from typing import Dict, Any, Set
import uuid

class Entity:
    """实体 - 游戏世界中万物的唯一标识"""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.components: Dict[str, Any] = {}
        self.active = True
    
    def add_component(self, component_type: str, component: Any):
        """添加组件"""
        self.components[component_type] = component
    
    def get_component(self, component_type: str):
        """获取组件"""
        return self.components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """检查是否有指定组件"""
        return component_type in self.components
    
    def remove_component(self, component_type: str):
        """移除组件"""
        if component_type in self.components:
            del self.components[component_type]

class EntityManager:
    """实体管理器"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
    
    def create_entity(self) -> Entity:
        """创建新实体"""
        entity = Entity()
        self.entities[entity.id] = entity
        return entity
    
    def get_entity(self, entity_id: str) -> Entity:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def destroy_entity(self, entity_id: str):
        """销毁实体"""
        if entity_id in self.entities:
            del self.entities[entity_id]
            return True
        return False
    
    def remove_entity(self, entity_id: str):
        """移除实体（别名）"""
        return self.destroy_entity(entity_id)
    
    def get_entities_with_components(self, *component_types) -> list:
        """获取拥有指定组件的所有实体"""
        result = []
        for entity in self.entities.values():
            if entity.active and all(entity.has_component(ct) for ct in component_types):
                result.append(entity)
        return result