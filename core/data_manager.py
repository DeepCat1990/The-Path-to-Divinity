import json
import os
from typing import Dict, Any, Optional
from .events import event_bus

class DataManager:
    """数据管理器 - 统一管理所有游戏数据和世界状态"""
    
    def __init__(self):
        self.static_data = {}  # 静态配置数据
        self.dynamic_data = {}  # 动态世界状态
        self.data_files = {
            # 静态数据文件
            'character_data': 'data/character_data.json',
            'techniques': 'data/techniques.json',
            'encounters': 'data/encounters.json',
            'taiwu_system': 'data/taiwu_system.json',
            'sects': 'data/sects.json',
            'skills': 'data/skills.json',
            'spell': 'data/spell.json',
            'item': 'data/item.json',
            'realm': 'data/realm.json',
            # 动态数据文件
            'world_state': 'data/world_state.json'
        }
        self._load_all_data()
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("world_state_changed", self._handle_world_state_change)
        event_bus.subscribe("save_world_state", self._save_world_state)
    
    def _load_all_data(self):
        """加载所有数据文件"""
        for key, filepath in self.data_files.items():
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if key == 'world_state':
                            self.dynamic_data[key] = data
                        else:
                            self.static_data[key] = data
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
    
    def get_static_data(self, data_type: str, item_id: str = None) -> Any:
        """获取静态数据"""
        if data_type not in self.static_data:
            return None
        
        data = self.static_data[data_type]
        if item_id:
            # 支持嵌套查找
            for section in data.values() if isinstance(data, dict) else [data]:
                if isinstance(section, dict) and item_id in section:
                    return section[item_id]
            return None
        return data
    
    def get_world_state(self, state_key: str = None) -> Any:
        """获取世界状态"""
        world_state = self.dynamic_data.get('world_state', {})
        if state_key:
            return world_state.get(state_key)
        return world_state
    
    def update_world_state(self, state_key: str, new_value: Any):
        """更新世界状态"""
        if 'world_state' not in self.dynamic_data:
            self.dynamic_data['world_state'] = {}
        
        self.dynamic_data['world_state'][state_key] = new_value
        
        event_bus.emit("world_state_changed", {
            "key": state_key,
            "value": new_value
        })
    
    def get_character_template(self, template_type: str = 'player_template') -> Dict:
        """获取角色模板"""
        data = self.get_static_data('character_data')
        if data and template_type in data:
            return data[template_type]
        return None
    
    def get_technique(self, category: str, technique_id: str = None) -> Any:
        """获取功法数据"""
        techniques = self.get_static_data('techniques')
        if not techniques:
            return None
        
        if category in techniques:
            category_data = techniques[category]
            if technique_id:
                # 在分类中查找具体功法
                for subcategory in category_data.values():
                    if isinstance(subcategory, dict) and technique_id in subcategory:
                        return subcategory[technique_id]
            return category_data
        return None
    
    def get_seasonal_encounters(self, season: str) -> list:
        """获取季节性奇遇"""
        encounters = self.get_static_data('encounters')
        if encounters and 'seasonal_encounters' in encounters:
            return encounters['seasonal_encounters'].get(season, [])
        return []
    
    def get_monthly_events(self, month: int) -> list:
        """获取月度特殊事件"""
        encounters = self.get_static_data('encounters')
        if encounters and 'monthly_special_events' in encounters:
            return encounters['monthly_special_events'].get(str(month), [])
        return []
    
    def get_xiangshu_events(self, phase: int) -> list:
        """获取相枢入侵事件"""
        encounters = self.get_static_data('encounters')
        if encounters and 'xiangshu_invasion_events' in encounters:
            phase_key = f"phase_{phase}"
            return encounters['xiangshu_invasion_events'].get(phase_key, [])
        return []
    
    def get_region_state(self, region_id: str) -> Dict:
        """获取地区状态"""
        world_state = self.get_world_state()
        regions = world_state.get('regions', {})
        return regions.get(region_id, {})
    
    def update_region_state(self, region_id: str, state_data: Dict):
        """更新地区状态"""
        world_state = self.get_world_state()
        if 'regions' not in world_state:
            world_state['regions'] = {}
        
        world_state['regions'][region_id] = state_data
        self.update_world_state('regions', world_state['regions'])
    
    def get_global_modifiers(self) -> Dict:
        """获取全局修正值"""
        world_state = self.get_world_state()
        global_state = world_state.get('global_state', {})
        return global_state.get('global_modifiers', {})
    
    def update_global_modifier(self, modifier_type: str, value: float):
        """更新全局修正值"""
        world_state = self.get_world_state()
        if 'global_state' not in world_state:
            world_state['global_state'] = {}
        if 'global_modifiers' not in world_state['global_state']:
            world_state['global_state']['global_modifiers'] = {}
        
        world_state['global_state']['global_modifiers'][modifier_type] = value
        self.update_world_state('global_state', world_state['global_state'])
    
    def _handle_world_state_change(self, event_data):
        """处理世界状态变化"""
        # 可以在这里添加状态变化的副作用逻辑
        pass
    
    def _save_world_state(self, event_data=None):
        """保存世界状态到文件"""
        if 'world_state' in self.dynamic_data:
            try:
                with open(self.data_files['world_state'], 'w', encoding='utf-8') as f:
                    json.dump(self.dynamic_data['world_state'], f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving world state: {e}")
    
    def save_all_data(self):
        """保存所有动态数据"""
        self._save_world_state()

# 全局数据管理器实例
data_manager = DataManager()