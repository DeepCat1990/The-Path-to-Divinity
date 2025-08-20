import json
import os
from typing import Dict, Any, Optional

class DataManager:
    """数据管理器 - 统一管理所有游戏数据"""
    
    def __init__(self):
        self.data_cache = {}
        self.data_files = {
            'character_template': 'data/character_template.json',
            'spell': 'data/spell.json',
            'item': 'data/item.json',
            'realm': 'data/realm.json',
            'encounters': 'data/encounter.json',
            'gongfa': 'data/gongfa.json',
            'techniques': 'data/techniques.json',
            'skills': 'data/skills.json'
        }
        self._load_all_data()
    
    def _load_all_data(self):
        """加载所有数据文件"""
        for data_type, file_path in self.data_files.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.data_cache[data_type] = json.load(f)
                except Exception as e:
                    print(f"加载数据文件 {file_path} 失败: {e}")
                    self.data_cache[data_type] = {}
            else:
                self.data_cache[data_type] = {}
    
    def get_static_data(self, data_type: str, item_id: str = None) -> Optional[Dict[str, Any]]:
        """获取静态数据"""
        if data_type not in self.data_cache:
            return None
        
        data = self.data_cache[data_type]
        
        if item_id is None:
            return data
        
        # 处理不同的数据结构
        if data_type == 'spell' and 'spells' in data:
            return data['spells'].get(item_id)
        elif data_type == 'encounters' and 'encounters' in data:
            return data['encounters'].get(item_id)
        else:
            return data.get(item_id)
    
    def get_character_template(self, template_type: str = 'player_template') -> Optional[Dict[str, Any]]:
        """获取角色模板"""
        templates = self.data_cache.get('character_template', {})
        return templates.get(template_type)
    
    def get_technique(self, category: str, technique_id: str = None) -> Optional[Dict[str, Any]]:
        """获取技能/功法数据"""
        # 先尝试从techniques文件获取
        techniques = self.data_cache.get('techniques', {})
        if category in techniques:
            if technique_id is None:
                return techniques[category]
            return techniques[category].get(technique_id)
        
        # 如果没有，尝试从其他文件获取
        if category == 'combat_techniques':
            gongfa = self.data_cache.get('gongfa', {})
            if technique_id is None:
                return gongfa
            return gongfa.get(technique_id)
        
        return None

# 全局数据管理器实例
data_manager = DataManager()