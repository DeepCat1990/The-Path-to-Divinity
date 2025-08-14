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
        self.setWindowTitle("修仙之路")
        self.setFixedSize(600, 480)
        
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
        
        # 血条
        health_layout = QVBoxLayout()
        self.health_label = QLabel(f"生命值: {char.health}/100")
        self.health_bar = QProgressBar()
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(char.health)
        self.health_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
        health_layout.addWidget(self.health_label)
        health_layout.addWidget(self.health_bar)
        layout.addLayout(health_layout)
        
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
        
        # 消息区域
        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)
        layout.addWidget(self.message_area)
        
    def setup_events(self):
        event_bus.subscribe("character_updated", self.update_character_info)
        event_bus.subscribe("message", self.add_message)
        event_bus.subscribe("day_changed", self.update_day)
        
    def update_character_info(self, character_data):
        self.power_label.setText(f"修为: {character_data['power']}")
        self.age_label.setText(f"年龄: {character_data['age']}")
        self.talent_label.setText(f"天赋: {character_data['talent']}")
        self.health_label.setText(f"生命值: {character_data['health']}/100")
        self.health_bar.setValue(character_data['health'])
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