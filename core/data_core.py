import json
import os
from typing import Dict, Any, Optional

class DataCore:
    """核心数据层 - 统一管理所有游戏数据"""
    
    def __init__(self):
        self.data_cache = {}
        self.data_files = {
            'character_template': 'data/character_template.json',
            'gongfa': 'data/gongfa.json', 
            'spell': 'data/spell.json',
            'item': 'data/item.json',
            'quest': 'data/quest.json',
            'encounter': 'data/encounter.json',
            'realm': 'data/realm.json',
            'sects': 'data/sects.json',
            'skills': 'data/skills.json',
            'config': 'data/config.json'
        }
        self._load_all_data()
    
    def _load_all_data(self):
        """加载所有数据文件到缓存"""
        for key, filepath in self.data_files.items():
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.data_cache[key] = json.load(f)
    
    def get_data(self, data_type: str, item_id: str = None) -> Any:
        """获取数据"""
        if data_type not in self.data_cache:
            return None
        
        data = self.data_cache[data_type]
        if item_id:
            # 支持嵌套查找
            for section in data.values():
                if isinstance(section, dict) and item_id in section:
                    return section[item_id]
            return None
        return data
    
    def get_character_template(self, template_type: str = 'player_template') -> Dict:
        """获取角色模板"""
        data = self.get_data('character_template')
        if data and template_type in data:
            return data[template_type]
        return None
    
    def get_gongfa(self, gongfa_id: str = None) -> Any:
        """获取功法数据"""
        if gongfa_id:
            return self.get_data('gongfa', gongfa_id)
        return self.get_data('gongfa')
    
    def get_spell(self, spell_id: str = None) -> Any:
        """获取法术数据"""
        if spell_id:
            return self.get_data('spell', spell_id)
        return self.get_data('spell')
    
    def get_item(self, item_id: str = None) -> Any:
        """获取物品数据"""
        if item_id:
            return self.get_data('item', item_id)
        return self.get_data('item')
    
    def get_realm(self, realm_id: str = None) -> Any:
        """获取境界数据"""
        if realm_id:
            return self.get_data('realm', realm_id)
        return self.get_data('realm')
    
    def get_encounter(self, encounter_id: str = None) -> Any:
        """获取奇遇数据"""
        if encounter_id:
            return self.get_data('encounter', encounter_id)
        return self.get_data('encounter')

# 全局数据核心实例
data_core = DataCore()