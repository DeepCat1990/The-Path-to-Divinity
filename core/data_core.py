class DataCore:
    """核心数据层 - 兼容性包装器"""
    
    def __init__(self):
        # 延迟导入避免循环引用
        from .data_manager import data_manager
        self.data_manager = data_manager
    
    def get_data(self, data_type, item_id=None):
        """获取数据"""
        return self.data_manager.get_static_data(data_type, item_id)
    
    def get_character_template(self, template_type='player_template'):
        """获取角色模板"""
        return self.data_manager.get_character_template(template_type)
    
    def get_gongfa(self, gongfa_id=None):
        """获取功法数据"""
        return self.data_manager.get_technique('combat_techniques', gongfa_id)
    
    def get_spell(self, spell_id=None):
        """获取法术数据"""
        return self.data_manager.get_static_data('spell', spell_id)
    
    def get_item(self, item_id=None):
        """获取物品数据"""
        return self.data_manager.get_static_data('item', item_id)
    
    def get_realm(self, realm_id=None):
        """获取境界数据"""
        return self.data_manager.get_static_data('realm', realm_id)
    
    def get_encounter(self, encounter_id=None):
        """获取奇遇数据"""
        return self.data_manager.get_static_data('encounters', encounter_id)

# 全局数据核心实例
data_core = DataCore()