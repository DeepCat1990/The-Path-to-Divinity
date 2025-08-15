from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QPushButton, QTextEdit, QListWidgetItem
from PySide6.QtCore import Qt
from core.events import event_bus

class NPCWindow(QDialog):
    """NPC互动界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("江湖人士")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("附近的修仙者")
        layout.addWidget(title_label)
        
        # NPC列表
        self.npc_list = QListWidget()
        self.npc_list.itemClicked.connect(self.show_npc_details)
        layout.addWidget(self.npc_list)
        
        # NPC详情
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(100)
        layout.addWidget(self.detail_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.interact_btn = QPushButton("互动")
        self.refresh_btn = QPushButton("刷新")
        self.close_btn = QPushButton("关闭")
        
        self.interact_btn.clicked.connect(self.interact_with_npc)
        self.refresh_btn.clicked.connect(self.refresh_npc_list)
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.interact_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.refresh_npc_list()
    
    def refresh_npc_list(self):
        """刷新NPC列表"""
        self.npc_list.clear()
        
        # 获取NPC系统
        from core.world_manager import world_manager
        if hasattr(world_manager, 'npc_system'):
            nearby_npcs = world_manager.npc_system.get_nearby_npcs()
            
            for npc_data in nearby_npcs:
                npc_text = f"{npc_data['name']} (修为: {npc_data['power']})"
                item = QListWidgetItem(npc_text)
                item.setData(Qt.UserRole, npc_data)
                self.npc_list.addItem(item)
        
        if self.npc_list.count() == 0:
            item = QListWidgetItem("附近没有其他修仙者")
            self.npc_list.addItem(item)
    
    def show_npc_details(self, item):
        """显示NPC详情"""
        npc_data = item.data(Qt.UserRole)
        if not npc_data:
            self.detail_text.setText("无详细信息")
            return
        
        template_names = {
            "wandering_cultivator": "独行修士",
            "sect_disciple": "门派弟子", 
            "mysterious_elder": "神秘长者"
        }
        
        template_name = template_names.get(npc_data['template'], "未知")
        
        details = f"姓名: {npc_data['name']}\\n"
        details += f"类型: {template_name}\\n"
        details += f"修为: {npc_data['power']}\\n"
        
        # 根据修为判断实力
        power = npc_data['power']
        if power < 20:
            strength = "初入修仙"
        elif power < 50:
            strength = "小有成就"
        elif power < 100:
            strength = "颇有实力"
        else:
            strength = "深不可测"
        
        details += f"实力: {strength}"
        
        self.detail_text.setText(details)
    
    def interact_with_npc(self):
        """与NPC互动"""
        current_item = self.npc_list.currentItem()
        if not current_item:
            event_bus.emit("message", "请先选择一个修仙者")
            return
        
        npc_data = current_item.data(Qt.UserRole)
        if not npc_data:
            return
        
        # 发送互动事件
        event_bus.emit("npc_interaction", {
            "npc_id": npc_data["id"]
        })
        
        event_bus.emit("message", f"你主动与 {npc_data['name']} 交流")
        self.close()