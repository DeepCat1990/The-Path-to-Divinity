from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QPushButton, QTextEdit, QListWidgetItem
from PySide6.QtCore import Qt
from core.events import event_bus

class SkillsWindow(QDialog):
    """技能界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("技能修炼")
        self.setFixedSize(600, 500)
        
        layout = QHBoxLayout(self)
        
        # 左侧技能列表
        left_layout = QVBoxLayout()
        self.skills_label = QLabel("已学技能:")
        left_layout.addWidget(self.skills_label)
        
        self.skill_list = QListWidget()
        self.skill_list.itemClicked.connect(self.show_skill_details)
        left_layout.addWidget(self.skill_list)
        
        # 施法按钮
        self.cast_btn = QPushButton("施展法术")
        self.cast_btn.clicked.connect(self.cast_spell)
        left_layout.addWidget(self.cast_btn)
        
        layout.addLayout(left_layout)
        
        # 右侧技能详情
        right_layout = QVBoxLayout()
        self.detail_label = QLabel("技能详情:")
        right_layout.addWidget(self.detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        right_layout.addWidget(self.detail_text)
        
        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        right_layout.addWidget(self.close_btn)
        
        layout.addLayout(right_layout)
        
        self.refresh_skills()
    
    def refresh_skills(self):
        """刷新技能列表"""
        self.skill_list.clear()
        
        learned_skills = self.game.skill_manager.get_learned_skills()
        for skill_id, skill_data in learned_skills:
            skill_text = f"{skill_data['name']} ({skill_data['realm']})"
            item = QListWidgetItem(skill_text)
            item.setData(Qt.UserRole, (skill_id, skill_data))
            self.skill_list.addItem(item)
    
    def show_skill_details(self, item):
        """显示技能详情"""
        skill_id, skill_data = item.data(Qt.UserRole)
        
        details = f"技能名称: {skill_data['name']}\\n"
        details += f"境界要求: {skill_data['realm']}\\n"
        details += f"修为要求: {skill_data['power_requirement']}\\n"
        
        if 'physical_attack' in skill_data:
            details += f"物理攻击: +{skill_data['physical_attack']}\\n"
        if 'spell_attack' in skill_data:
            details += f"法术攻击: +{skill_data['spell_attack']}\\n"
        if 'mana_cost' in skill_data:
            details += f"法力消耗: {skill_data['mana_cost']}\\n"
        
        details += f"\\n描述: {skill_data['description']}"
        
        self.detail_text.setText(details)
    
    def cast_spell(self):
        """施展法术"""
        current_item = self.skill_list.currentItem()
        if not current_item:
            event_bus.emit("message", "请先选择一个法术")
            return
        
        skill_id, skill_data = current_item.data(Qt.UserRole)
        
        if skill_data['type'] != 'spell':
            event_bus.emit("message", "只能施展法术类技能")
            return
        
        # 发送施法请求
        event_bus.emit("request_cast_spell", {
            "caster_id": self.game.player_entity_id,
            "spell_id": skill_id
        })
        
        event_bus.emit("message", f"施展了 {skill_data['name']}")
        self.close()