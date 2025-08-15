from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QTextEdit, QProgressBar, QMenuBar, QMenu, QListWidget
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QAction
from core.events import event_bus
from .theme_manager import theme_manager
from .inventory_window import InventoryWindow
from .skills_window import SkillsWindow
from .character_window import CharacterWindow
from .npc_window import NPCWindow
from .taiwu_window import TaiwuWindow


class MainWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setup_ui()
        self.setup_events()
        
    def setup_ui(self):
        self.setWindowTitle("The Path to Divinity")
        self.setFixedSize(750, 750)
        
        # 设置初始主题
        self.setStyleSheet(theme_manager.get_stylesheet())
        
        # 创建菜单栏
        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 角色信息面板
        char = self.game.character
        
        # 时间信息
        time_layout = QHBoxLayout()
        self.time_label = QLabel("第1年 第1月 第1天")
        self.time_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.season_label = QLabel("春")
        self.season_label.setStyleSheet("color: #00aa00; font-weight: bold;")
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: #ff6600; font-weight: bold;")
        
        # 游戏速度控制
        self.speed_label = QLabel("1.0x")
        self.speed_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.season_label)
        time_layout.addStretch()
        time_layout.addWidget(self.speed_label)
        time_layout.addWidget(self.countdown_label)
        layout.addLayout(time_layout)
        
        # 相枢入侵信息
        self.xiangshu_label = QLabel("相枢威胁: 无")
        self.xiangshu_label.setStyleSheet("color: #aa0000; font-weight: bold;")
        layout.addWidget(self.xiangshu_label)
        
        # 基础属性
        stats_layout = QHBoxLayout()
        self.power_label = QLabel(f"修为: {char.power}")
        self.age_label = QLabel(f"年龄: {char.age}")
        self.lifespan_label = QLabel(f"寿命: {getattr(char, 'lifespan', 80)}")
        self.talent_label = QLabel(f"天赋: {char.talent}")
        stats_layout.addWidget(self.power_label)
        stats_layout.addWidget(self.age_label)
        stats_layout.addWidget(self.lifespan_label)
        stats_layout.addWidget(self.talent_label)
        layout.addLayout(stats_layout)
        
        # 立场信息
        stance_layout = QHBoxLayout()
        self.stance_label = QLabel("立场: 中庸")
        self.stance_label.setStyleSheet("color: #666666; font-weight: bold;")
        self.mood_label = QLabel("心情: 普通")
        self.mood_label.setStyleSheet("color: #0066aa;")
        stance_layout.addWidget(self.stance_label)
        stance_layout.addWidget(self.mood_label)
        stance_layout.addStretch()
        layout.addLayout(stance_layout)
        
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
        
        # 技能显示 - 使用列表显示
        skills_container = QVBoxLayout()
        skills_header = QLabel("已学功法技艺:")
        skills_header.setStyleSheet("color: #0066cc; font-weight: bold;")
        skills_container.addWidget(skills_header)
        
        self.skills_list = QListWidget()
        self.skills_list.setMaximumHeight(80)
        self.skills_list.setStyleSheet("QListWidget { font-size: 10px; }")
        skills_container.addWidget(self.skills_list)
        layout.addLayout(skills_container)
        
        # 状态显示
        self.status_label = QLabel(self._get_status(char))
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # 主要按钮
        main_button_layout = QHBoxLayout()
        self.train_btn = QPushButton("修炼 (60秒)")
        self.adventure_btn = QPushButton("历练 (30秒)")
        self.train_btn.clicked.connect(lambda: self.start_action("train", 60))
        self.adventure_btn.clicked.connect(lambda: self.start_action("adventure", 30))
        main_button_layout.addWidget(self.train_btn)
        main_button_layout.addWidget(self.adventure_btn)
        layout.addLayout(main_button_layout)
        
        # 功能按钮第一行
        function_button_layout1 = QHBoxLayout()
        self.character_btn = QPushButton("角色")
        self.inventory_btn = QPushButton("背包")
        self.skills_btn = QPushButton("技能")
        self.npc_btn = QPushButton("江湖")
        
        self.character_btn.clicked.connect(self.open_character_window)
        self.inventory_btn.clicked.connect(self.open_inventory_window)
        self.skills_btn.clicked.connect(self.open_skills_window)
        self.npc_btn.clicked.connect(self.open_npc_window)
        
        function_button_layout1.addWidget(self.character_btn)
        function_button_layout1.addWidget(self.inventory_btn)
        function_button_layout1.addWidget(self.skills_btn)
        function_button_layout1.addWidget(self.npc_btn)
        layout.addLayout(function_button_layout1)
        
        # 功能按钮第二行
        function_button_layout2 = QHBoxLayout()
        self.taiwu_btn = QPushButton("太吾系统")
        self.pause_btn = QPushButton("暂停")
        self.speed_btn = QPushButton("加速")
        self.theme_btn = QPushButton("切换主题")
        
        self.taiwu_btn.clicked.connect(self.open_taiwu_window)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.speed_btn.clicked.connect(self.cycle_speed)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        function_button_layout2.addWidget(self.taiwu_btn)
        function_button_layout2.addWidget(self.pause_btn)
        function_button_layout2.addWidget(self.speed_btn)
        function_button_layout2.addWidget(self.theme_btn)
        layout.addLayout(function_button_layout2)
        
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
        
        # 初始化时同步ECS实体数据
        self.sync_character_data()
        
    def setup_events(self):
        event_bus.subscribe("character_updated", self.update_character_info)
        event_bus.subscribe("message", self.add_message)
        event_bus.subscribe("day_changed", self.update_day)
        event_bus.subscribe("skill_learned", self.update_skills)
        event_bus.subscribe("sect_joined", self.update_sect)
        event_bus.subscribe("month_changed", self.update_month)
        event_bus.subscribe("stance_changed", self.update_stance)
        event_bus.subscribe("xiangshu_phase_change", self.update_xiangshu)
        
        # 定期同步数据
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_character_data)
        self.sync_timer.start(1000)  # 每秒同步一次
        
        # 时间更新定时器
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(500)  # 每0.5秒更新一次
        
        # 游戏速度状态
        self.current_speed_index = 0
        self.speed_options = [0.5, 1.0, 2.0, 5.0]
        
    def update_character_info(self, character_data):
        self.power_label.setText(f"修为: {character_data['power']}")
        self.age_label.setText(f"年龄: {character_data['age']}")
        self.lifespan_label.setText(f"寿命: {character_data.get('lifespan', 80)}")
        self.talent_label.setText(f"天赋: {character_data['talent']}")
        self.physical_attack_label.setText(f"物理攻击: {character_data['physical_attack']}")
        self.spell_attack_label.setText(f"法术攻击: {character_data['spell_attack']}")
        self.health_label.setText(f"生命值: {character_data['health']}/100")
        self.health_bar.setValue(character_data['health'])
        self.mana_label.setText(f"法力值: {character_data['mana']}/{character_data['max_mana']}")
        self.mana_bar.setValue(character_data['mana'])
        self.status_label.setText(self._get_status(character_data))
        
        # 更新心情
        mood = character_data.get('mood', 50)
        if mood > 70:
            mood_text = "心情: 愉悦"
        elif mood > 30:
            mood_text = "心情: 普通"
        else:
            mood_text = "心情: 低落"
        self.mood_label.setText(mood_text)
        
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
        # 旧的日期更新方法，保留兼容性
        pass
        
    def update_time_display(self):
        """更新时间显示"""
        time_info = self.game.get_time_info()
        self.time_label.setText(f"第{time_info['year']}年 第{time_info['month']}月 第{time_info['day']}天")
        self.speed_label.setText(f"{time_info['game_speed']:.1f}x")
        
        # 更新季节
        month = time_info['month']
        if month in [1, 2, 3]:
            season = "春"
            color = "#00aa00"
        elif month in [4, 5, 6]:
            season = "夏"
            color = "#ff6600"
        elif month in [7, 8, 9]:
            season = "秋"
            color = "#cc6600"
        else:
            season = "冬"
            color = "#0066cc"
        
        self.season_label.setText(season)
        self.season_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # 更新暂停按钮文本
        if time_info['paused']:
            self.pause_btn.setText("继续")
        else:
            self.pause_btn.setText("暂停")
    
    def toggle_pause(self):
        """切换暂停状态"""
        self.game.pause_game()
    
    def cycle_speed(self):
        """循环切换游戏速度"""
        self.current_speed_index = (self.current_speed_index + 1) % len(self.speed_options)
        new_speed = self.speed_options[self.current_speed_index]
        self.game.set_game_speed(new_speed)
        
    def update_skills(self, skill_data):
        self.skills_list.clear()
        learned = self.game.skill_manager.get_learned_skills()
        
        if learned:
            for skill_id, skill in learned:
                skill_text = f"{skill['name']} ({skill.get('realm', skill.get('grade', '未知'))})"
                self.skills_list.addItem(skill_text)
        else:
            self.skills_list.addItem("尚未学会任何功法")
            
        # 更新攻击力
        physical, spell = self.game.skill_manager.get_total_attack_power()
        char = self.game.character
        char.physical_attack = 5 + physical
        char.spell_attack = spell
        event_bus.emit("character_updated", char.__dict__)
        
    def sync_character_data(self):
        """同步角色数据从 ECS 实体到主界面"""
        from core.world_manager import world_manager
        if hasattr(self.game, 'player_entity_id'):
            player_entity = world_manager.get_entity(self.game.player_entity_id)
            if player_entity:
                attr = player_entity.get_component("AttributeComponent")
                if attr:
                    # 更新主界面显示的数据
                    char_data = {
                        'power': getattr(attr, 'power', self.game.character.power),
                        'age': attr.age,
                        'talent': getattr(attr, 'talent', self.game.character.talent),
                        'physical_attack': attr.physical_attack,
                        'spell_attack': attr.spell_attack,
                        'health': attr.health,
                        'max_health': attr.max_health,
                        'mana': attr.mana,
                        'max_mana': attr.max_mana
                    }
                    self.update_character_info(char_data)
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        from core.game_engine import game_engine
        game_engine.stop()
        event.accept()
        
    def update_sect(self, sect_data):
        sect = sect_data["sect"]
        self.sect_label.setText(f"门派: {sect['name']} ({sect['type']})")
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 游戏菜单
        game_menu = menubar.addMenu('游戏')
        
        character_action = QAction('角色信息', self)
        character_action.triggered.connect(self.open_character_window)
        game_menu.addAction(character_action)
        
        inventory_action = QAction('背包', self)
        inventory_action.triggered.connect(self.open_inventory_window)
        game_menu.addAction(inventory_action)
        
        skills_action = QAction('技能', self)
        skills_action.triggered.connect(self.open_skills_window)
        game_menu.addAction(skills_action)
        
        npc_action = QAction('江湖人士', self)
        npc_action.triggered.connect(self.open_npc_window)
        game_menu.addAction(npc_action)
        
        taiwu_action = QAction('太吾系统', self)
        taiwu_action.triggered.connect(self.open_taiwu_window)
        game_menu.addAction(taiwu_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('设置')
        
        theme_action = QAction('切换主题', self)
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)
    
    def open_character_window(self):
        """打开角色界面"""
        dialog = CharacterWindow(self.game, self)
        dialog.exec()
    
    def open_inventory_window(self):
        """打开背包界面"""
        dialog = InventoryWindow(self.game, self)
        dialog.exec()
    
    def open_skills_window(self):
        """打开技能界面"""
        dialog = SkillsWindow(self.game, self)
        dialog.exec()
    
    def open_npc_window(self):
        """打开NPC互动界面"""
        dialog = NPCWindow(self.game, self)
        dialog.exec()
    
    def open_taiwu_window(self):
        """打开太吾系统界面"""
        dialog = TaiwuWindow(self.game, self)
        dialog.exec()
    
    def update_month(self, month_data):
        """更新月份信息"""
        # 时间显示会在update_time_display中处理
        pass
    
    def update_stance(self, stance_data):
        """更新立场信息"""
        stance_names = {
            "righteous": "刚正",
            "benevolent": "仁善",
            "neutral": "中庸",
            "rebellious": "叛逆",
            "selfish": "唯我"
        }
        stance_name = stance_names.get(stance_data['new_stance'], '未知')
        self.stance_label.setText(f"立场: {stance_name}")
    
    def update_xiangshu(self, phase_data):
        """更新相枢入侵信息"""
        phase_name = phase_data.get('name', '未知阶段')
        threat_level = phase_data.get('effects', {}).get('danger_level', 1.0)
        
        if threat_level > 1.4:
            color = "#ff0000"  # 红色
        elif threat_level > 1.2:
            color = "#ff6600"  # 橙色
        elif threat_level > 1.0:
            color = "#ffaa00"  # 黄色
        else:
            color = "#00aa00"  # 绿色
        
        self.xiangshu_label.setText(f"相枢威胁: {phase_name}")
        self.xiangshu_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def toggle_theme(self):
        """切换主题"""
        new_stylesheet = theme_manager.toggle_theme()
        self.setStyleSheet(new_stylesheet)
        
        # 更新进度条颜色
        theme = theme_manager.themes[theme_manager.current_theme]
        self.health_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {theme['health_bar']}; }}")
        self.mana_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {theme['mana_bar']}; }}")