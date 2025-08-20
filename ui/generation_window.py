from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, QTabWidget, 
                               QWidget, QProgressBar, QTextEdit, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.events import event_bus
from .character_creation_window import CharacterCreationWindow

class GenerationWindow(QDialog):
    """世代传承界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.generation_system = None
        self.setup_ui()
        self._setup_event_handlers()
        
    def setup_ui(self):
        self.setWindowTitle("太吾传承")
        self.setFixedSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 家族信息标签页
        family_tab = QWidget()
        self.setup_family_tab(family_tab)
        tab_widget.addTab(family_tab, "家族")
        
        # 婚配标签页
        marriage_tab = QWidget()
        self.setup_marriage_tab(marriage_tab)
        tab_widget.addTab(marriage_tab, "婚配")
        
        # 传承标签页
        inheritance_tab = QWidget()
        self.setup_inheritance_tab(inheritance_tab)
        tab_widget.addTab(inheritance_tab, "传承")
        
        layout.addWidget(tab_widget)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def setup_family_tab(self, tab):
        """设置家族信息标签页"""
        layout = QVBoxLayout(tab)
        
        # 当前世代信息
        self.generation_label = QLabel("第1代 太吾传人")
        self.generation_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(self.generation_label)
        
        # 当前角色属性
        layout.addWidget(QLabel("当前角色属性:"))
        self.attributes_text = QTextEdit()
        self.attributes_text.setMaximumHeight(150)
        self.attributes_text.setReadOnly(True)
        layout.addWidget(self.attributes_text)
        
        # 家族树
        layout.addWidget(QLabel("家族成员:"))
        self.family_tree_list = QListWidget()
        layout.addWidget(self.family_tree_list)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新信息")
        refresh_btn.clicked.connect(self.refresh_family_info)
        layout.addWidget(refresh_btn)
    
    def setup_marriage_tab(self, tab):
        """设置婚配标签页"""
        layout = QVBoxLayout(tab)
        
        # 当前婚姻状态
        self.marriage_status = QLabel("未婚")
        self.marriage_status.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.marriage_status)
        
        # 寻找对象按钮
        find_btn = QPushButton("寻找婚配对象")
        find_btn.clicked.connect(self.find_marriage_candidates)
        layout.addWidget(find_btn)
        
        # 候选人列表
        layout.addWidget(QLabel("婚配候选人:"))
        self.candidates_list = QListWidget()
        layout.addWidget(self.candidates_list)
        
        # 求婚按钮
        propose_btn = QPushButton("向选中对象求婚")
        propose_btn.clicked.connect(self.propose_marriage)
        layout.addWidget(propose_btn)
        
        # 生育按钮
        self.birth_btn = QPushButton("生育子女")
        self.birth_btn.clicked.connect(self.have_child)
        self.birth_btn.setEnabled(False)
        layout.addWidget(self.birth_btn)
    
    def setup_inheritance_tab(self, tab):
        """设置传承标签页"""
        layout = QVBoxLayout(tab)
        
        # 子女列表
        layout.addWidget(QLabel("子女列表:"))
        self.children_list = QListWidget()
        layout.addWidget(self.children_list)
        
        # 传承按钮
        inherit_btn = QPushButton("传承给选中子女")
        inherit_btn.clicked.connect(self.switch_generation)
        layout.addWidget(inherit_btn)
        
        # 创建新角色按钮
        create_btn = QPushButton("创建新角色")
        create_btn.clicked.connect(self.create_new_character)
        layout.addWidget(create_btn)
        
        # 传承预览
        layout.addWidget(QLabel("传承效果预览:"))
        self.inheritance_preview = QTextEdit()
        self.inheritance_preview.setMaximumHeight(150)
        self.inheritance_preview.setReadOnly(True)
        layout.addWidget(self.inheritance_preview)
    
    def _setup_event_handlers(self):
        """设置事件处理"""
        event_bus.subscribe("character_created", self._on_character_created)
        event_bus.subscribe("marriage_success", self._on_marriage_success)
        event_bus.subscribe("child_born", self._on_child_born)
        event_bus.subscribe("generation_changed", self._on_generation_changed)
        event_bus.subscribe("marriage_candidates_found", self._on_candidates_found)
    
    def showEvent(self, event):
        """窗口显示时初始化"""
        super().showEvent(event)
        from core.world_manager import world_manager
        self.generation_system = world_manager.generation_system
        self.refresh_family_info()
    
    def refresh_family_info(self):
        """刷新家族信息"""
        if not self.generation_system:
            return
        
        family_info = self.generation_system.get_family_info()
        
        # 更新世代标签
        self.generation_label.setText(f"第{family_info['current_generation']}代 太吾传人")
        
        # 更新当前角色属性
        self._update_character_attributes()
        
        # 更新家族树
        self._update_family_tree(family_info['family_tree'])
        
        # 更新婚姻状态
        self._update_marriage_status()
        
        # 更新子女列表
        self._update_children_list()
    
    def _update_character_attributes(self):
        """更新角色属性显示"""
        if not self.generation_system or not self.generation_system.current_character_id:
            return
        
        from core.world_manager import world_manager
        from core.ecs.components import AttributeComponent
        
        char_id = self.generation_system.current_character_id
        if world_manager.has_component(char_id, AttributeComponent):
            attrs = world_manager.get_component(char_id, AttributeComponent)
            
            attr_text = f"""生命: {attrs.health}/{attrs.max_health}
法力: {attrs.mana}/{attrs.max_mana}
根骨: {attrs.constitution}
悟性: {attrs.comprehension}
魅力: {attrs.charm}
福缘: {attrs.luck}
灵根: {attrs.spiritual_root}
年龄: {attrs.age}
寿命: {attrs.lifespan}"""
            
            self.attributes_text.setText(attr_text)
    
    def _update_family_tree(self, family_tree):
        """更新家族树显示"""
        self.family_tree_list.clear()
        
        for char_id, info in family_tree.items():
            item_text = f"第{info['generation']}代 - {info['name']}"
            if info['spouse']:
                item_text += f" (配偶: {info['spouse']['name']})"
            if info['children']:
                item_text += f" (子女: {len(info['children'])}人)"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, char_id)
            self.family_tree_list.addItem(item)
    
    def _update_marriage_status(self):
        """更新婚姻状态"""
        if not self.generation_system or not self.generation_system.current_character_id:
            return
        
        char_id = self.generation_system.current_character_id
        char_info = self.generation_system.family_tree.get(char_id)
        
        if char_info and char_info['spouse']:
            spouse_name = char_info['spouse']['name']
            self.marriage_status.setText(f"已婚 (配偶: {spouse_name})")
            self.birth_btn.setEnabled(True)
        else:
            self.marriage_status.setText("未婚")
            self.birth_btn.setEnabled(False)
    
    def _update_children_list(self):
        """更新子女列表"""
        self.children_list.clear()
        
        if not self.generation_system or not self.generation_system.current_character_id:
            return
        
        char_id = self.generation_system.current_character_id
        char_info = self.generation_system.family_tree.get(char_id)
        
        if char_info and char_info['children']:
            for child_id in char_info['children']:
                child_info = self.generation_system.family_tree.get(child_id)
                if child_info:
                    item = QListWidgetItem(child_info['name'])
                    item.setData(Qt.UserRole, child_id)
                    self.children_list.addItem(item)
    
    def find_marriage_candidates(self):
        """寻找婚配对象"""
        if self.generation_system:
            self.generation_system.find_marriage_candidates()
    
    def propose_marriage(self):
        """求婚"""
        current_item = self.candidates_list.currentItem()
        if current_item and self.generation_system:
            candidate_index = self.candidates_list.row(current_item)
            self.generation_system.propose_marriage(candidate_index)
    
    def have_child(self):
        """生育子女"""
        if self.generation_system:
            self.generation_system.have_child()
    
    def switch_generation(self):
        """切换世代"""
        current_item = self.children_list.currentItem()
        if current_item and self.generation_system:
            child_id = current_item.data(Qt.UserRole)
            
            # 确认对话框
            reply = QMessageBox.question(self, "确认传承", 
                                       f"确定要传承给 {current_item.text()} 吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.generation_system.switch_to_next_generation(child_id)
    
    def create_new_character(self):
        """创建新角色"""
        if not self.generation_system:
            return
            
        # 打开角色创建界面
        creation_dialog = CharacterCreationWindow(self)
        if creation_dialog.exec() == QDialog.Accepted:
            char_data = creation_dialog.get_character_data()
            
            # 创建角色
            char_name = f"第{self.generation_system.current_generation + 1}代太吾传人"
            char_id = self.generation_system.create_character_with_attributes(char_name, char_data)
            
            if char_id:
                event_bus.emit("message", f"创建了新角色：{char_name}")
                self.refresh_family_info()
    
    def _on_character_created(self, event_data):
        """角色创建事件"""
        self.refresh_family_info()
    
    def _on_marriage_success(self, event_data):
        """婚姻成功事件"""
        self.refresh_family_info()
    
    def _on_child_born(self, event_data):
        """子女出生事件"""
        self.refresh_family_info()
    
    def _on_generation_changed(self, event_data):
        """世代变更事件"""
        self.refresh_family_info()
    
    def _on_candidates_found(self, event_data):
        """找到候选人事件"""
        self.candidates_list.clear()
        
        for i, candidate in enumerate(event_data['candidates']):
            item_text = f"{candidate['name']} (年龄:{candidate['age']}, 相性:{candidate['compatibility']}%)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)
            self.candidates_list.addItem(item)