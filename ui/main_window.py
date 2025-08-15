from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QTextEdit, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from core.events import event_bus

class MainWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setup_ui()
        self.setup_events()
        
    def setup_ui(self):
        self.setWindowTitle("The Path")
        self.setFixedSize(600, 580)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 角色信息面板
        char = self.game.character
        
        # 回合信息
        turn_layout = QHBoxLayout()
        self.day_label = QLabel("第1天")
        self.day_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: #ff6600; font-weight: bold;")
        turn_layout.addWidget(self.day_label)
        turn_layout.addStretch()
        turn_layout.addWidget(self.countdown_label)
        layout.addLayout(turn_layout)
        
        # 基础属性
        stats_layout = QHBoxLayout()
        self.power_label = QLabel(f"修为: {char.power}")
        self.age_label = QLabel(f"年龄: {char.age}")
        self.talent_label = QLabel(f"天赋: {char.talent}")
        stats_layout.addWidget(self.power_label)
        stats_layout.addWidget(self.age_label)
        stats_layout.addWidget(self.talent_label)
        layout.addLayout(stats_layout)
        
        # 攻击力属性
        attack_layout = QHBoxLayout()
        self.physical_attack_label = QLabel(f"物理攻击: {char.physical_attack}")
        self.spell_attack_label = QLabel(f"法术攻击: {char.spell_attack}")
        self.physical_attack_label.setStyleSheet("color: #cc6600; font-weight: bold;")
        self.spell_attack_label.setStyleSheet("color: #6600cc; font-weight: bold;")
        attack_layout.addWidget(self.physical_attack_label)
        attack_layout.addWidget(self.spell_attack_label)
        layout.addLayout(attack_layout)
        
        # 血条和法力条
        bars_layout = QVBoxLayout()
        self.health_label = QLabel(f"生命值: {char.health}/100")
        self.health_bar = QProgressBar()
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(char.health)
        self.health_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
        
        self.mana_label = QLabel(f"法力值: {char.mana}/{char.max_mana}")
        self.mana_bar = QProgressBar()
        self.mana_bar.setMaximum(char.max_mana)
        self.mana_bar.setValue(char.mana)
        self.mana_bar.setStyleSheet("QProgressBar::chunk { background-color: #4444ff; }")
        
        bars_layout.addWidget(self.health_label)
        bars_layout.addWidget(self.health_bar)
        bars_layout.addWidget(self.mana_label)
        bars_layout.addWidget(self.mana_bar)
        layout.addLayout(bars_layout)
        
        # 门派信息
        self.sect_label = QLabel("门派: 无")
        self.sect_label.setStyleSheet("color: #cc0066; font-weight: bold;")
        layout.addWidget(self.sect_label)
        
        # 技能显示
        self.skills_label = QLabel("已学技能: 无")
        self.skills_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        layout.addWidget(self.skills_label)
        
        # 状态显示
        self.status_label = QLabel(self._get_status(char))
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.train_btn = QPushButton("修炼 (60秒)")
        self.adventure_btn = QPushButton("历练 (30秒)")
        self.train_btn.clicked.connect(lambda: self.start_action("train", 60))
        self.adventure_btn.clicked.connect(lambda: self.start_action("adventure", 30))
        button_layout.addWidget(self.train_btn)
        button_layout.addWidget(self.adventure_btn)
        layout.addLayout(button_layout)
        
        # 倒计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_time = 0
        self.current_action = None
        
        # 游戏主循环定时器
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game.update)
        self.game_timer.start(100)  # 100ms更新一次
        
        # 消息区域
        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)
        layout.addWidget(self.message_area)
        
    def setup_events(self):
        event_bus.subscribe("character_updated", self.update_character_info)
        event_bus.subscribe("message", self.add_message)
        event_bus.subscribe("day_changed", self.update_day)
        event_bus.subscribe("skill_learned", self.update_skills)
        event_bus.subscribe("sect_joined", self.update_sect)
        
    def update_character_info(self, character_data):
        self.power_label.setText(f"修为: {character_data['power']}")
        self.age_label.setText(f"年龄: {character_data['age']}")
        self.talent_label.setText(f"天赋: {character_data['talent']}")
        self.physical_attack_label.setText(f"物理攻击: {character_data['physical_attack']}")
        self.spell_attack_label.setText(f"法术攻击: {character_data['spell_attack']}")
        self.health_label.setText(f"生命值: {character_data['health']}/100")
        self.health_bar.setValue(character_data['health'])
        self.mana_label.setText(f"法力值: {character_data['mana']}/{character_data['max_mana']}")
        self.mana_bar.setValue(character_data['mana'])
        self.status_label.setText(self._get_status(character_data))
        
    def _get_status(self, char_data):
        if isinstance(char_data, dict):
            health, power = char_data['health'], char_data['power']
        else:
            health, power = char_data.health, char_data.power
            
        if health < 30:
            return "状态: 重伤"
        elif health < 60:
            return "状态: 轻伤"
        elif power > 50:
            return "状态: 修为精进"
        else:
            return "状态: 正常"
        
    def add_message(self, message):
        self.message_area.append(message)
        
    def start_action(self, action, duration):
        if self.remaining_time > 0:
            return
            
        self.current_action = action
        self.remaining_time = duration
        self.timer.start(1000)
        self.set_buttons_enabled(False)
        
    def update_countdown(self):
        self.remaining_time -= 1
        if self.remaining_time > 0:
            self.countdown_label.setText(f"剩余: {self.remaining_time}秒")
        else:
            self.timer.stop()
            self.countdown_label.setText("")
            self.execute_action()
            self.set_buttons_enabled(True)
            
    def execute_action(self):
        if self.current_action == "train":
            self.game.train()
        elif self.current_action == "adventure":
            self.game.adventure()
        self.current_action = None
        
    def set_buttons_enabled(self, enabled):
        self.train_btn.setEnabled(enabled)
        self.adventure_btn.setEnabled(enabled)
        
    def update_day(self, day):
        self.day_label.setText(f"第{day}天")
        
    def update_skills(self, skill_data):
        learned = self.game.skill_manager.get_learned_skills()
        if learned:
            skill_names = [f"{skill[1]['name']}({skill[1]['realm']})" for skill in learned]
            self.skills_label.setText(f"已学技能: {', '.join(skill_names)}")
        else:
            self.skills_label.setText("已学技能: 无")
            
        # 更新攻击力
        physical, spell = self.game.skill_manager.get_total_attack_power()
        char = self.game.character
        char.physical_attack = 5 + physical
        char.spell_attack = spell
        event_bus.emit("character_updated", char.__dict__)
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        from ..world_manager import world_manager
        world_manager.stop()
        event.accept()
        
    def update_sect(self, sect_data):
        sect = sect_data["sect"]
        self.sect_label.setText(f"门派: {sect['name']} ({sect['type']})")