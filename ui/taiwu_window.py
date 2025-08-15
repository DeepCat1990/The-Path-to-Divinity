from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar, QTabWidget, QWidget, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.events import event_bus

class TaiwuWindow(QDialog):
    """太吾系统界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("太吾系统")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 时间与立场标签页
        time_stance_tab = QWidget()
        self.setup_time_stance_tab(time_stance_tab)
        tab_widget.addTab(time_stance_tab, "时间立场")
        
        # 资质标签页
        aptitude_tab = QWidget()
        self.setup_aptitude_tab(aptitude_tab)
        tab_widget.addTab(aptitude_tab, "资质")
        
        # 地区标签页
        region_tab = QWidget()
        self.setup_region_tab(region_tab)
        tab_widget.addTab(region_tab, "地区")
        
        layout.addWidget(tab_widget)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def setup_time_stance_tab(self, tab):
        """设置时间立场标签页"""
        layout = QVBoxLayout(tab)
        
        # 时间信息
        from core.world_manager import world_manager
        time_system = world_manager.time_system
        
        time_info = QLabel(f"当前时间: 第{time_system.current_year}年 第{time_system.current_month}月")
        time_info.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(time_info)
        
        # 立场信息
        stance_system = world_manager.stance_system
        current_stance = stance_system.config.get(stance_system.player_stance, {})
        
        stance_info = QLabel(f"当前立场: {current_stance.get('name', '未知')}")
        stance_info.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(stance_info)
        
        stance_desc = QLabel(f"描述: {current_stance.get('description', '无描述')}")
        layout.addWidget(stance_desc)
        
        # 立场点数
        layout.addWidget(QLabel("立场倾向:"))
        for stance_id, points in stance_system.stance_points.items():
            stance_name = stance_system.config.get(stance_id, {}).get('name', stance_id)
            
            stance_layout = QHBoxLayout()
            stance_label = QLabel(f"{stance_name}:")
            stance_label.setFixedWidth(60)
            
            stance_bar = QProgressBar()
            stance_bar.setMaximum(100)
            stance_bar.setValue(min(100, points))
            
            stance_layout.addWidget(stance_label)
            stance_layout.addWidget(stance_bar)
            layout.addLayout(stance_layout)
        
        # 相枢入侵信息
        xiangshu_system = world_manager.xiangshu_system
        if xiangshu_system.is_invasion_active():
            threat_level = xiangshu_system.get_current_threat_level()
            invasion_info = QLabel(f"相枢威胁等级: {threat_level:.1f}")
            invasion_info.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(invasion_info)
        else:
            layout.addWidget(QLabel("相枢威胁: 暂无"))
    
    def setup_aptitude_tab(self, tab):
        """设置资质标签页"""
        layout = QVBoxLayout(tab)
        
        from core.world_manager import world_manager
        aptitude_system = world_manager.aptitude_system
        
        layout.addWidget(QLabel("资质一览:"))
        
        for category, skills in aptitude_system.aptitudes.items():
            category_names = {
                "combat": "战斗",
                "crafting": "技艺", 
                "social": "社交"
            }
            
            category_label = QLabel(f"=== {category_names.get(category, category)} ===")
            category_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(category_label)
            
            for skill_id, aptitude_value in skills.items():
                skill_config = aptitude_system.config.get(category, {}).get(skill_id, {})
                skill_name = skill_config.get('name', skill_id)
                
                skill_layout = QHBoxLayout()
                skill_label = QLabel(f"{skill_name}:")
                skill_label.setFixedWidth(80)
                
                # 资质条
                aptitude_bar = QProgressBar()
                aptitude_bar.setMaximum(10)
                aptitude_bar.setValue(aptitude_value)
                
                # 根据资质值设置颜色
                if aptitude_value >= 8:
                    color = "#00ff00"  # 绿色
                elif aptitude_value >= 6:
                    color = "#ffff00"  # 黄色
                elif aptitude_value >= 4:
                    color = "#ff8800"  # 橙色
                else:
                    color = "#ff0000"  # 红色
                
                aptitude_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
                
                skill_layout.addWidget(skill_label)
                skill_layout.addWidget(aptitude_bar)
                skill_layout.addWidget(QLabel(f"{aptitude_value}/10"))
                layout.addLayout(skill_layout)
    
    def setup_region_tab(self, tab):
        """设置地区标签页"""
        layout = QVBoxLayout(tab)
        
        from core.world_manager import world_manager
        region_system = world_manager.region_system
        
        # 当前地区
        current_region_data = region_system.get_current_region_data()
        current_info = QLabel(f"当前地区: {current_region_data.get('name', '未知')}")
        current_info.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(current_info)
        
        current_desc = QLabel(f"描述: {current_region_data.get('description', '无描述')}")
        layout.addWidget(current_desc)
        
        # 可用资源
        resources = region_system.get_available_resources()
        if resources:
            layout.addWidget(QLabel(f"可用资源: {', '.join(resources)}"))
        else:
            layout.addWidget(QLabel("可用资源: 无"))
        
        # 已发现地区
        layout.addWidget(QLabel("已发现地区:"))
        
        region_list = QListWidget()
        for region_id in region_system.discovered_regions:
            region_data = region_system.config.get(region_id, {})
            region_name = region_data.get('name', region_id)
            
            item = QListWidgetItem(region_name)
            item.setData(Qt.UserRole, region_id)
            region_list.addItem(item)
        
        region_list.itemDoubleClicked.connect(self.travel_to_region)
        layout.addWidget(region_list)
        
        # 旅行按钮
        travel_btn = QPushButton("前往选中地区")
        travel_btn.clicked.connect(lambda: self.travel_to_selected_region(region_list))
        layout.addWidget(travel_btn)
    
    def travel_to_region(self, item):
        """前往地区"""
        region_id = item.data(Qt.UserRole)
        from core.world_manager import world_manager
        
        if world_manager.region_system.travel_to_region(region_id):
            self.close()
    
    def travel_to_selected_region(self, region_list):
        """前往选中的地区"""
        current_item = region_list.currentItem()
        if current_item:
            self.travel_to_region(current_item)