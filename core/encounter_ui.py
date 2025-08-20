from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from .events import event_bus

class EncounterDialog(QDialog):
    """奇遇对话框"""
    
    def __init__(self, encounter_data, entity_id, parent=None):
        super().__init__(parent)
        self.encounter_data = encounter_data
        self.entity_id = entity_id
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("奇遇")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 奇遇标题
        title_label = QLabel(self.encounter_data["name"])
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #cc6600;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 奇遇描述
        desc_text = QTextEdit()
        desc_text.setPlainText(self.encounter_data["description"])
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(100)
        layout.addWidget(desc_text)
        
        # 选择按钮
        choices = self.encounter_data.get("choices", [])
        for i, choice in enumerate(choices):
            btn = QPushButton(f"{i+1}. {choice['text']}")
            btn.clicked.connect(lambda checked, idx=i: self.make_choice(idx))
            layout.addWidget(btn)
        
        # 关闭按钮
        close_btn = QPushButton("离开")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
    
    def make_choice(self, choice_index):
        """做出选择"""
        event_bus.emit("encounter_choice", {
            "entity_id": self.entity_id,
            "choice_index": choice_index
        })
        self.accept()