from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class CharacterWindow(QDialog):
    """角色详情界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("角色详情")
        self.setFixedSize(400, 600)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("角色信息")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 获取角色数据
        from core.world_manager import world_manager
        player_entity = world_manager.get_entity(self.game.player_entity_id)
        if not player_entity:
            # 使用旧角色数据作为备用
            char = self.game.character
            attr = type('obj', (object,), {
                'age': char.age, 'constitution': 5, 'comprehension': 5,
                'charm': 5, 'luck': 5, 'spiritual_root': 3,
                'physical_attack': char.physical_attack, 'spell_attack': char.spell_attack,
                'defense': 5, 'health': char.health, 'max_health': 100,
                'mana': char.mana, 'max_mana': char.max_mana, 'lifespan': 80
            })()
            state = type('obj', (object,), {'realm': 'mortal', 'sect': None})()
        else:
            attr = player_entity.get_component("AttributeComponent")
            state = player_entity.get_component("StateComponent")
            
            if not attr:
                return
        
        # 基础属性
        basic_layout = QVBoxLayout()
        basic_layout.addWidget(QLabel("=== 基础属性 ==="))
        basic_layout.addWidget(QLabel(f"年龄: {attr.age} 岁"))
        basic_layout.addWidget(QLabel(f"寿命: {attr.lifespan} 岁"))
        basic_layout.addWidget(QLabel(f"根骨: {attr.constitution}"))
        basic_layout.addWidget(QLabel(f"悟性: {attr.comprehension}"))
        basic_layout.addWidget(QLabel(f"魅力: {attr.charm}"))
        basic_layout.addWidget(QLabel(f"气运: {attr.luck}"))
        basic_layout.addWidget(QLabel(f"灵根: {attr.spiritual_root}"))
        layout.addLayout(basic_layout)
        
        # 战斗属性
        combat_layout = QVBoxLayout()
        combat_layout.addWidget(QLabel("=== 战斗属性 ==="))
        combat_layout.addWidget(QLabel(f"物理攻击: {attr.physical_attack}"))
        combat_layout.addWidget(QLabel(f"法术攻击: {attr.spell_attack}"))
        combat_layout.addWidget(QLabel(f"防御力: {attr.defense}"))
        layout.addLayout(combat_layout)
        
        # 生命值条
        health_layout = QVBoxLayout()
        health_label = QLabel(f"生命值: {attr.health}/{attr.max_health}")
        health_bar = QProgressBar()
        health_bar.setMaximum(attr.max_health)
        health_bar.setValue(attr.health)
        health_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
        health_layout.addWidget(health_label)
        health_layout.addWidget(health_bar)
        layout.addLayout(health_layout)
        
        # 法力值条
        mana_layout = QVBoxLayout()
        mana_label = QLabel(f"法力值: {attr.mana}/{attr.max_mana}")
        mana_bar = QProgressBar()
        mana_bar.setMaximum(attr.max_mana)
        mana_bar.setValue(attr.mana)
        mana_bar.setStyleSheet("QProgressBar::chunk { background-color: #4444ff; }")
        mana_layout.addWidget(mana_label)
        mana_layout.addWidget(mana_bar)
        layout.addLayout(mana_layout)
        
        # 修炼状态
        if state:
            state_layout = QVBoxLayout()
            state_layout.addWidget(QLabel("=== 修炼状态 ==="))
            state_layout.addWidget(QLabel(f"当前境界: {state.realm}"))
            if state.sect:
                state_layout.addWidget(QLabel(f"所属门派: {state.sect}"))
            else:
                state_layout.addWidget(QLabel("所属门派: 无"))
            layout.addLayout(state_layout)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)