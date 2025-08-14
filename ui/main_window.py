from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from core.events import event_bus

class MainWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setup_ui()
        self.setup_events()
        
    def setup_ui(self):
        self.setWindowTitle("修仙之路")
        self.setFixedSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 角色信息
        info_layout = QHBoxLayout()
        self.power_label = QLabel("修为: 10")
        self.health_label = QLabel("生命: 100")
        self.talent_label = QLabel("天赋: 5")
        info_layout.addWidget(self.power_label)
        info_layout.addWidget(self.health_label)
        info_layout.addWidget(self.talent_label)
        layout.addLayout(info_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.train_btn = QPushButton("修炼")
        self.adventure_btn = QPushButton("历练")
        self.train_btn.clicked.connect(self.game.train)
        self.adventure_btn.clicked.connect(self.game.adventure)
        button_layout.addWidget(self.train_btn)
        button_layout.addWidget(self.adventure_btn)
        layout.addLayout(button_layout)
        
        # 消息区域
        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)
        layout.addWidget(self.message_area)
        
    def setup_events(self):
        event_bus.subscribe("character_updated", self.update_character_info)
        event_bus.subscribe("message", self.add_message)
        
    def update_character_info(self, character_data):
        self.power_label.setText(f"修为: {character_data['power']}")
        self.health_label.setText(f"生命: {character_data['health']}")
        self.talent_label.setText(f"天赋: {character_data['talent']}")
        
    def add_message(self, message):
        self.message_area.append(message)