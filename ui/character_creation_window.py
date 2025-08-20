from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, QTextEdit,
                               QSlider, QSpinBox, QGroupBox, QGridLayout, QComboBox,
                               QCheckBox, QTabWidget, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import json

class CharacterCreationWindow(QDialog):
    """角色创建界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_build = None
        self.selected_birthplace = None
        self.selected_zhuazhou = None
        self.selected_traits = []
        self.trait_points = 10
        self.custom_attributes = {
            "constitution": 3,
            "determination": 3,
            "bone_root": 3,
            "comprehension": 3, 
            "charm": 3,
            "luck": 3
        }
        self.remaining_points = 12
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        self.setWindowTitle("创建太吾传人")
        self.setFixedSize(800, 700)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("创建新的太吾传人")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 出生设定标签页
        birth_tab = QWidget()
        self.setup_birth_tab(birth_tab)
        tab_widget.addTab(birth_tab, "出生设定")
        
        # 属性分配标签页
        attr_tab = QWidget()
        self.setup_attributes_tab(attr_tab)
        tab_widget.addTab(attr_tab, "属性分配")
        
        # 特质选择标签页
        trait_tab = QWidget()
        self.setup_traits_tab(trait_tab)
        tab_widget.addTab(trait_tab, "特质选择")
        
        layout.addWidget(tab_widget)
        

        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("创建角色")
        self.create_btn.clicked.connect(self.create_character)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def setup_birth_tab(self, tab):
        """设置出生设定标签页"""
        layout = QVBoxLayout(tab)
        
        # 出生地
        layout.addWidget(QLabel("出生地:"))
        self.birthplace_combo = QComboBox()
        self.birthplace_combo.currentTextChanged.connect(self.select_birthplace)
        layout.addWidget(self.birthplace_combo)
        
        self.birthplace_desc = QTextEdit()
        self.birthplace_desc.setMaximumHeight(60)
        self.birthplace_desc.setReadOnly(True)
        layout.addWidget(self.birthplace_desc)
        
        # 抓周物品
        layout.addWidget(QLabel("抓周物品:"))
        self.zhuazhou_combo = QComboBox()
        self.zhuazhou_combo.currentTextChanged.connect(self.select_zhuazhou)
        layout.addWidget(self.zhuazhou_combo)
        
        self.zhuazhou_desc = QTextEdit()
        self.zhuazhou_desc.setMaximumHeight(60)
        self.zhuazhou_desc.setReadOnly(True)
        layout.addWidget(self.zhuazhou_desc)
    
    def setup_attributes_tab(self, tab):
        """设置属性分配标签页"""
        layout = QVBoxLayout(tab)
        
        # 六维属性
        attr_group = QGroupBox("六维属性")
        attr_layout = QGridLayout(attr_group)
        
        self.attribute_sliders = {}
        self.attribute_labels = {}
        
        attributes = [
            ("constitution", "体质"),
            ("determination", "定力"),
            ("bone_root", "根骨"),
            ("comprehension", "悟性"),
            ("charm", "魅力"),
            ("luck", "幸运")
        ]
        
        for i, (attr_id, attr_name) in enumerate(attributes):
            name_label = QLabel(f"{attr_name}:")
            attr_layout.addWidget(name_label, i, 0)
            
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(1)
            slider.setMaximum(10)
            slider.setValue(3)
            slider.valueChanged.connect(lambda v, a=attr_id: self.update_attribute(a, v))
            self.attribute_sliders[attr_id] = slider
            attr_layout.addWidget(slider, i, 1)
            
            value_label = QLabel("3")
            self.attribute_labels[attr_id] = value_label
            attr_layout.addWidget(value_label, i, 2)
        
        self.points_label = QLabel(f"剩余点数: {self.remaining_points}")
        self.points_label.setFont(QFont("Arial", 10, QFont.Bold))
        attr_layout.addWidget(self.points_label, len(attributes), 0, 1, 3)
        
        layout.addWidget(attr_group)
    
    def setup_traits_tab(self, tab):
        """设置特质选择标签页"""
        layout = QVBoxLayout(tab)
        
        # 特质点数
        self.trait_points_label = QLabel(f"特质点数: {self.trait_points}")
        self.trait_points_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.trait_points_label)
        
        # 特质列表
        self.traits_list = QListWidget()
        layout.addWidget(self.traits_list)
        
        # 特质描述
        self.trait_description = QTextEdit()
        self.trait_description.setMaximumHeight(100)
        self.trait_description.setReadOnly(True)
        layout.addWidget(self.trait_description)
    
    def load_config(self):
        """加载配置"""
        try:
            with open("data/character_creation.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            # 加载出生地
            for bp_id, bp_data in self.config["birthplaces"].items():
                self.birthplace_combo.addItem(bp_data["name"], bp_id)
            
            # 加载抓周物品
            for item_id, item_data in self.config["zhuazhou_items"].items():
                self.zhuazhou_combo.addItem(item_data["name"], item_id)
            
            # 加载特质
            for trait_id, trait_data in self.config["initial_traits"].items():
                item = QListWidgetItem(f"{trait_data['name']} ({trait_data['cost']}点)")
                item.setData(Qt.UserRole, (trait_id, trait_data))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.traits_list.addItem(item)
            
            self.traits_list.itemChanged.connect(self.trait_selection_changed)
            self.traits_list.itemClicked.connect(self.show_trait_description)
                
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def select_birthplace(self, name):
        """选择出生地"""
        bp_id = self.birthplace_combo.currentData()
        if bp_id and bp_id in self.config["birthplaces"]:
            bp_data = self.config["birthplaces"][bp_id]
            self.selected_birthplace = (bp_id, bp_data)
            self.birthplace_desc.setText(f"{bp_data['name']}: {bp_data['description']}")
    
    def select_zhuazhou(self, name):
        """选择抓周物品"""
        item_id = self.zhuazhou_combo.currentData()
        if item_id and item_id in self.config["zhuazhou_items"]:
            item_data = self.config["zhuazhou_items"][item_id]
            self.selected_zhuazhou = (item_id, item_data)
            self.zhuazhou_desc.setText(f"{item_data['name']}: {item_data['description']}")
    
    def trait_selection_changed(self, item):
        """特质选择变化"""
        trait_id, trait_data = item.data(Qt.UserRole)
        cost = trait_data["cost"]
        
        if item.checkState() == Qt.Checked:
            if self.trait_points >= cost:
                self.selected_traits.append((trait_id, trait_data))
                self.trait_points -= cost
            else:
                item.setCheckState(Qt.Unchecked)
        else:
            if (trait_id, trait_data) in self.selected_traits:
                self.selected_traits.remove((trait_id, trait_data))
                self.trait_points += cost
        
        self.trait_points_label.setText(f"特质点数: {self.trait_points}")
    
    def show_trait_description(self, item):
        """显示特质描述"""
        trait_id, trait_data = item.data(Qt.UserRole)
        desc = f"{trait_data['name']} ({trait_data['cost']}点)\n{trait_data['description']}"
        self.trait_description.setText(desc)
    
    def update_attribute(self, attr_id, value):
        """更新属性值"""
        old_value = self.custom_attributes[attr_id]
        self.custom_attributes[attr_id] = value
        self.attribute_labels[attr_id].setText(str(value))
        
        self.calculate_remaining_points()
        
        # 如果点数不足，恢复原值
        if self.remaining_points < 0:
            self.custom_attributes[attr_id] = old_value
            self.attribute_sliders[attr_id].setValue(old_value)
            self.attribute_labels[attr_id].setText(str(old_value))
            self.calculate_remaining_points()
    
    def calculate_remaining_points(self):
        """计算剩余点数"""
        total_used = sum(self.custom_attributes.values()) - 18  # 基础值3*6=18
        self.remaining_points = 12 - total_used
        self.points_label.setText(f"剩余点数: {self.remaining_points}")
        
        # 更新创建按钮状态
        self.create_btn.setEnabled(self.remaining_points >= 0)
    
    def create_character(self):
        """创建角色"""
        self.accept()
    
    def get_character_data(self):
        """获取角色数据"""
        # 计算最终属性
        final_attributes = self.custom_attributes.copy()
        
        # 应用出生地加成
        if self.selected_birthplace:
            bp_data = self.selected_birthplace[1]
            for attr, bonus in bp_data.get("attribute_bonus", {}).items():
                final_attributes[attr] = final_attributes.get(attr, 3) + bonus
        
        # 应用抓周物品加成
        if self.selected_zhuazhou:
            item_data = self.selected_zhuazhou[1]
            for attr, bonus in item_data.get("attribute_bonus", {}).items():
                final_attributes[attr] = final_attributes.get(attr, 3) + bonus
        
        # 应用特质加成
        for trait_id, trait_data in self.selected_traits:
            for attr, bonus in trait_data.get("attribute_bonus", {}).items():
                final_attributes[attr] = final_attributes.get(attr, 3) + bonus
        
        return {
            "attributes": final_attributes,
            "birthplace": self.selected_birthplace,
            "zhuazhou": self.selected_zhuazhou,
            "traits": self.selected_traits
        }