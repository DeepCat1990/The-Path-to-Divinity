from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QPushButton, QListWidgetItem
from PySide6.QtCore import Qt
from core.events import event_bus

class InventoryWindow(QDialog):
    """背包界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("背包")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # 背包容量显示
        self.capacity_label = QLabel("背包容量: 0/100")
        layout.addWidget(self.capacity_label)
        
        # 物品列表
        self.item_list = QListWidget()
        self.item_list.itemDoubleClicked.connect(self.use_item)
        layout.addWidget(self.item_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.use_btn = QPushButton("使用")
        self.close_btn = QPushButton("关闭")
        self.use_btn.clicked.connect(self.use_selected_item)
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.use_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.refresh_inventory()
    
    def refresh_inventory(self):
        """刷新背包显示"""
        self.item_list.clear()
        
        # 获取玩家背包组件
        from core.world_manager import world_manager
        player_entity = world_manager.get_entity(self.game.player_entity_id)
        if not player_entity:
            return
            
        inventory = player_entity.get_component("InventoryComponent")
        if not inventory:
            return
        
        # 更新容量显示
        item_count = sum(inventory.items.values())
        self.capacity_label.setText(f"背包容量: {item_count}/{inventory.capacity}")
        
        # 显示物品
        for item_id, count in inventory.items.items():
            item_text = f"{item_id} x{count}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, item_id)
            self.item_list.addItem(item)
    
    def use_item(self, item):
        """使用物品"""
        item_id = item.data(Qt.UserRole)
        if item_id:
            # 通过世界管理器的背包系统使用物品
            from core.world_manager import world_manager
            inventory_system = None
            for system in world_manager.systems:
                if hasattr(system, 'use_item'):
                    inventory_system = system
                    break
            
            if inventory_system:
                success = inventory_system.use_item(self.game.player_entity_id, item_id)
                if success:
                    self.refresh_inventory()
                    event_bus.emit("message", f"使用了 {item_id}")
    
    def use_selected_item(self):
        """使用选中的物品"""
        current_item = self.item_list.currentItem()
        if current_item:
            self.use_item(current_item)