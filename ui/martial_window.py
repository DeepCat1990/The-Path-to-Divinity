from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, QTabWidget, 
                               QWidget, QProgressBar, QTextEdit, QComboBox, QCheckBox,
                               QGroupBox, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from core.events import event_bus
import random
import json

class MartialWindow(QDialog):
    """武学系统界面"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.martial_system = None
        self.combat_strategy = None
        self.setup_ui()
        self._setup_event_handlers()
        
    def setup_ui(self):
        self.setWindowTitle("武学体系")
        self.setFixedSize(800, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 智能建议标签页
        advisor_tab = QWidget()
        self.setup_advisor_tab(advisor_tab)
        tab_widget.addTab(advisor_tab, "智能建议")
        
        # 武学学习标签页
        learning_tab = QWidget()
        self.setup_learning_tab(learning_tab)
        tab_widget.addTab(learning_tab, "武学学习")
        
        # 推荐搭配标签页
        builds_tab = QWidget()
        self.setup_builds_tab(builds_tab)
        tab_widget.addTab(builds_tab, "推荐搭配")
        
        # 自动修炼标签页
        training_tab = QWidget()
        self.setup_training_tab(training_tab)
        tab_widget.addTab(training_tab, "自动修炼")
        
        # 战斗策略标签页
        combat_tab = QWidget()
        self.setup_combat_tab(combat_tab)
        tab_widget.addTab(combat_tab, "战斗策略")
        
        layout.addWidget(tab_widget)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def setup_advisor_tab(self, tab):
        """设置智能建议标签页"""
        layout = QVBoxLayout(tab)
        
        # 角色分析
        analysis_group = QGroupBox("角色分析")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.character_type_label = QLabel("角色类型: 未分析")
        self.character_type_label.setFont(QFont("Arial", 11, QFont.Bold))
        analysis_layout.addWidget(self.character_type_label)
        
        self.strengths_text = QTextEdit()
        self.strengths_text.setMaximumHeight(80)
        self.strengths_text.setReadOnly(True)
        self.strengths_text.setPlaceholderText("点击分析按钮查看角色优势")
        analysis_layout.addWidget(self.strengths_text)
        
        analyze_btn = QPushButton("分析角色")
        analyze_btn.clicked.connect(self.analyze_character)
        analysis_layout.addWidget(analyze_btn)
        
        layout.addWidget(analysis_group)
        
        # 个性化建议
        advice_group = QGroupBox("个性化建议")
        advice_layout = QVBoxLayout(advice_group)
        
        self.next_skills_list = QListWidget()
        self.next_skills_list.setMaximumHeight(100)
        advice_layout.addWidget(QLabel("建议学习:"))
        advice_layout.addWidget(self.next_skills_list)
        
        self.combat_style_label = QLabel("推荐战斗风格: 未分析")
        advice_layout.addWidget(self.combat_style_label)
        
        layout.addWidget(advice_group)
        
        # 新手提示
        tips_group = QGroupBox("新手提示")
        tips_layout = QVBoxLayout(tips_group)
        
        self.tips_list = QListWidget()
        self.tips_list.setMaximumHeight(120)
        tips_layout.addWidget(self.tips_list)
        
        # 加载新手提示
        self.load_beginner_tips()
        
        layout.addWidget(tips_group)
        
        # 一键优化按钮
        optimize_btn = QPushButton("一键优化武学搭配")
        optimize_btn.clicked.connect(self.optimize_martial_build)
        layout.addWidget(optimize_btn)
    
    def setup_learning_tab(self, tab):
        """设置武学学习标签页"""
        layout = QVBoxLayout(tab)
        
        # 已学武学
        layout.addWidget(QLabel("已学武学:"))
        self.learned_list = QListWidget()
        self.learned_list.setMaximumHeight(150)
        layout.addWidget(self.learned_list)
        
        # 可学武学
        layout.addWidget(QLabel("可学武学:"))
        self.available_list = QListWidget()
        self.available_list.itemClicked.connect(self.show_martial_details)
        layout.addWidget(self.available_list)
        
        # 武学详情
        details_group = QGroupBox("武学详情")
        details_layout = QVBoxLayout(details_group)
        
        self.martial_name = QLabel("选择一个武学查看详情")
        self.martial_name.setFont(QFont("Arial", 12, QFont.Bold))
        details_layout.addWidget(self.martial_name)
        
        self.martial_description = QTextEdit()
        self.martial_description.setMaximumHeight(100)
        self.martial_description.setReadOnly(True)
        details_layout.addWidget(self.martial_description)
        
        # 学习按钮
        self.learn_btn = QPushButton("学习此武学")
        self.learn_btn.clicked.connect(self.learn_selected_martial)
        self.learn_btn.setEnabled(False)
        details_layout.addWidget(self.learn_btn)
        
        layout.addWidget(details_group)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新武学列表")
        refresh_btn.clicked.connect(self.refresh_martial_lists)
        layout.addWidget(refresh_btn)
    
    def setup_builds_tab(self, tab):
        """设置推荐搭配标签页"""
        layout = QVBoxLayout(tab)
        
        # 推荐搭配列表
        layout.addWidget(QLabel("推荐武学搭配:"))
        self.builds_list = QListWidget()
        self.builds_list.itemClicked.connect(self.show_build_details)
        layout.addWidget(self.builds_list)
        
        # 搭配详情
        build_details_group = QGroupBox("搭配详情")
        build_details_layout = QVBoxLayout(build_details_group)
        
        self.build_name = QLabel("选择一个搭配查看详情")
        self.build_name.setFont(QFont("Arial", 12, QFont.Bold))
        build_details_layout.addWidget(self.build_name)
        
        self.build_description = QTextEdit()
        self.build_description.setMaximumHeight(120)
        self.build_description.setReadOnly(True)
        build_details_layout.addWidget(self.build_description)
        
        # 协同效应
        layout.addWidget(QLabel("当前协同效应:"))
        self.synergy_list = QListWidget()
        self.synergy_list.setMaximumHeight(100)
        layout.addWidget(self.synergy_list)
        
        layout.addWidget(build_details_group)
        
        # 一键学习按钮
        self.auto_learn_btn = QPushButton("一键学习推荐搭配")
        self.auto_learn_btn.clicked.connect(self.auto_learn_build)
        layout.addWidget(self.auto_learn_btn)
    
    def setup_training_tab(self, tab):
        """设置自动修炼标签页"""
        layout = QVBoxLayout(tab)
        
        # 自动修炼开关
        self.auto_training_checkbox = QCheckBox("启用自动修炼")
        self.auto_training_checkbox.stateChanged.connect(self.toggle_auto_training)
        layout.addWidget(self.auto_training_checkbox)
        
        # 修炼重点选择
        focus_group = QGroupBox("修炼重点")
        focus_layout = QVBoxLayout(focus_group)
        
        self.focus_combo = QComboBox()
        self.focus_combo.addItems([
            "平衡发展",
            "内功专精", 
            "外功专精",
            "身法专精",
            "绝技专精"
        ])
        self.focus_combo.currentTextChanged.connect(self.change_training_focus)
        focus_layout.addWidget(self.focus_combo)
        
        layout.addWidget(focus_group)
        
        # 修炼进度
        progress_group = QGroupBox("修炼进度")
        progress_layout = QGridLayout(progress_group)
        
        martial_types = [
            ("内功", "internal"),
            ("外功", "external"), 
            ("身法", "agility"),
            ("绝技", "special")
        ]
        
        self.progress_bars = {}
        for i, (name, type_id) in enumerate(martial_types):
            label = QLabel(f"{name}:")
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            
            progress_layout.addWidget(label, i, 0)
            progress_layout.addWidget(progress_bar, i, 1)
            self.progress_bars[type_id] = progress_bar
        
        layout.addWidget(progress_group)
        
        # 一键修炼按钮
        training_buttons_layout = QHBoxLayout()
        self.one_click_train_btn = QPushButton("一键修炼")
        self.one_click_train_btn.clicked.connect(self.start_one_click_training)
        
        self.smart_train_btn = QPushButton("智能修炼")
        self.smart_train_btn.clicked.connect(self.start_smart_training)
        
        training_buttons_layout.addWidget(self.one_click_train_btn)
        training_buttons_layout.addWidget(self.smart_train_btn)
        layout.addLayout(training_buttons_layout)
        
        # 修炼状态
        self.training_status = QLabel("修炼状态: 空闲")
        layout.addWidget(self.training_status)
    
    def setup_combat_tab(self, tab):
        """设置战斗策略标签页"""
        layout = QVBoxLayout(tab)
        
        # 战斗策略选择
        strategy_group = QGroupBox("战斗策略")
        strategy_layout = QVBoxLayout(strategy_group)
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "攻防平衡",
            "激进攻击",
            "稳健防守", 
            "技巧流"
        ])
        self.strategy_combo.currentTextChanged.connect(self.change_combat_strategy)
        strategy_layout.addWidget(self.strategy_combo)
        
        # 策略描述
        self.strategy_description = QTextEdit()
        self.strategy_description.setMaximumHeight(80)
        self.strategy_description.setReadOnly(True)
        strategy_layout.addWidget(self.strategy_description)
        
        layout.addWidget(strategy_group)
        
        # 半自动战斗设置
        auto_combat_group = QGroupBox("半自动战斗")
        auto_combat_layout = QVBoxLayout(auto_combat_group)
        
        self.auto_combat_checkbox = QCheckBox("启用半自动战斗")
        self.auto_combat_checkbox.stateChanged.connect(self.toggle_auto_combat)
        auto_combat_layout.addWidget(self.auto_combat_checkbox)
        
        self.intervention_checkbox = QCheckBox("关键时刻手动干预")
        self.intervention_checkbox.setChecked(True)
        self.intervention_checkbox.stateChanged.connect(self.toggle_intervention)
        auto_combat_layout.addWidget(self.intervention_checkbox)
        
        layout.addWidget(auto_combat_group)
        
        # 战斗统计
        stats_group = QGroupBox("战斗统计")
        stats_layout = QGridLayout(stats_group)
        
        self.wins_label = QLabel("胜利: 0")
        self.losses_label = QLabel("失败: 0")
        self.win_rate_label = QLabel("胜率: 0%")
        
        stats_layout.addWidget(self.wins_label, 0, 0)
        stats_layout.addWidget(self.losses_label, 0, 1)
        stats_layout.addWidget(self.win_rate_label, 1, 0, 1, 2)
        
        layout.addWidget(stats_group)
        
        # 测试战斗按钮
        test_combat_btn = QPushButton("测试战斗")
        test_combat_btn.clicked.connect(self.test_combat)
        layout.addWidget(test_combat_btn)
    
    def _setup_event_handlers(self):
        """设置事件处理"""
        event_bus.subscribe("martial_learned", self._on_martial_learned)
        event_bus.subscribe("training_completed", self._on_training_completed)
        event_bus.subscribe("combat_result", self._on_combat_result)
    
    def showEvent(self, event):
        """窗口显示时初始化"""
        super().showEvent(event)
        from core.world_manager import world_manager
        self.martial_system = world_manager.martial_system if hasattr(world_manager, 'martial_system') else None
        self.refresh_all_data()
    
    def refresh_all_data(self):
        """刷新所有数据"""
        self.refresh_martial_lists()
        self.refresh_builds_list()
        self.refresh_synergy_effects()
        self.update_training_progress()
    
    def refresh_martial_lists(self):
        """刷新武学列表"""
        from core.world_manager import world_manager
        if not self.martial_system or not hasattr(world_manager, 'player_entity_id'):
            return
        
        # 清空列表
        self.learned_list.clear()
        self.available_list.clear()
        
        # 获取已学武学
        from core.ecs.components import SkillComponent
        
        if world_manager.has_component(world_manager.player_entity_id, SkillComponent):
            skills = world_manager.get_component(world_manager.player_entity_id, SkillComponent)
            
            for gongfa_id in skills.learned_gongfa:
                item = QListWidgetItem(f"✓ {gongfa_id}")
                item.setForeground(QColor("#00aa00"))
                self.learned_list.addItem(item)
        
        # 获取可学武学
        available = self.martial_system.get_available_martials(world_manager.player_entity_id)
        for martial in available:
            item_text = f"{martial['name']} ({martial['type']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, martial)
            self.available_list.addItem(item)
    
    def refresh_builds_list(self):
        """刷新推荐搭配列表"""
        if not self.martial_system:
            return
        
        self.builds_list.clear()
        
        try:
            with open("data/martial_system.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            
            builds = config.get("recommended_builds", [])
            for build in builds:
                item = QListWidgetItem(build["name"])
                item.setData(Qt.UserRole, build)
                self.builds_list.addItem(item)
        except:
            pass
    
    def refresh_synergy_effects(self):
        """刷新协同效应"""
        from core.world_manager import world_manager
        if not self.martial_system or not hasattr(world_manager, 'player_entity_id'):
            return
        
        self.synergy_list.clear()
        
        from core.ecs.components import SkillComponent
        
        if world_manager.has_component(world_manager.player_entity_id, SkillComponent):
            skills = world_manager.get_component(world_manager.player_entity_id, SkillComponent)
            synergies = self.martial_system.get_martial_synergy(skills.learned_gongfa)
            
            for synergy in synergies:
                item_text = f"⚡ {synergy['name']}: {synergy['description']}"
                item = QListWidgetItem(item_text)
                item.setForeground(QColor("#ff6600"))
                self.synergy_list.addItem(item)
    
    def show_martial_details(self, item):
        """显示武学详情"""
        martial = item.data(Qt.UserRole)
        if martial:
            self.martial_name.setText(martial["name"])
            
            details = f"类型: {martial['type']}\n"
            details += f"等级: {martial['level']}\n"
            details += f"描述: {martial['description']}\n\n"
            details += "效果:\n"
            
            for effect, value in martial.get("effects", {}).items():
                details += f"  {effect}: +{value}\n"
            
            requirements = martial.get("requirements", {})
            if requirements:
                details += "\n学习条件:\n"
                for req, value in requirements.items():
                    details += f"  {req}: {value}\n"
            
            self.martial_description.setText(details)
            self.learn_btn.setEnabled(True)
    
    def learn_selected_martial(self):
        """学习选中的武学"""
        current_item = self.available_list.currentItem()
        if current_item and self.martial_system:
            martial = current_item.data(Qt.UserRole)
            if martial:
                from core.world_manager import world_manager
                success = self.martial_system.learn_martial(world_manager.player_entity_id, martial["id"])
                if success:
                    self.refresh_martial_lists()
                    self.refresh_synergy_effects()
    
    def show_build_details(self, item):
        """显示搭配详情"""
        build = item.data(Qt.UserRole)
        if build:
            self.build_name.setText(build["name"])
            
            details = f"描述: {build['description']}\n\n"
            details += "包含武学:\n"
            for skill in build.get("skills", []):
                details += f"  • {skill}\n"
            
            details += "\n优势:\n"
            for advantage in build.get("advantages", []):
                details += f"  ✓ {advantage}\n"
            
            details += "\n劣势:\n"
            for disadvantage in build.get("disadvantages", []):
                details += f"  ✗ {disadvantage}\n"
            
            self.build_description.setText(details)
    
    def auto_learn_build(self):
        """一键学习推荐搭配"""
        current_item = self.builds_list.currentItem()
        if current_item and self.martial_system:
            build = current_item.data(Qt.UserRole)
            if build:
                skills = build.get("skills", [])
                learned_count = 0
                
                from core.world_manager import world_manager
                for skill_id in skills:
                    if self.martial_system.learn_martial(world_manager.player_entity_id, skill_id):
                        learned_count += 1
                
                if learned_count > 0:
                    QMessageBox.information(self, "学习完成", f"成功学会了 {learned_count} 个武学！")
                    self.refresh_martial_lists()
                    self.refresh_synergy_effects()
                else:
                    QMessageBox.warning(self, "学习失败", "没有学会任何新武学，请检查学习条件。")
    
    def toggle_auto_training(self, state):
        """切换自动修炼"""
        enabled = state == Qt.Checked
        event_bus.emit("auto_training_toggle", {"enabled": enabled})
    
    def change_training_focus(self, focus_text):
        """改变修炼重点"""
        focus_map = {
            "平衡发展": "balanced",
            "内功专精": "internal",
            "外功专精": "external", 
            "身法专精": "agility",
            "绝技专精": "special"
        }
        focus = focus_map.get(focus_text, "balanced")
        event_bus.emit("training_focus_change", {"focus": focus})
    
    def start_one_click_training(self):
        """开始一键修炼"""
        from core.world_manager import world_manager
        if not self.martial_system or not hasattr(world_manager, 'player_entity_id'):
            return
        
        self.training_status.setText("修炼状态: 修炼中...")
        self.one_click_train_btn.setEnabled(False)
        
        # 模拟修炼过程
        self._simulate_training_process()
    
    def _simulate_training_process(self):
        """模拟修炼过程"""
        from core.world_manager import world_manager
        from core.ecs.components import AttributeComponent
        
        if not world_manager.has_component(world_manager.player_entity_id, AttributeComponent):
            return
        
        attrs = world_manager.get_component(world_manager.player_entity_id, AttributeComponent)
        
        # 模拟修炼效果
        training_results = []
        
        # 根据修炼重点分配收益
        focus_map = {
            "平衡发展": "balanced",
            "内功专精": "internal",
            "外功专精": "external",
            "身法专精": "agility",
            "绝技专精": "special"
        }
        
        current_focus = focus_map.get(self.focus_combo.currentText(), "balanced")
        
        # 尝试学习新技能
        self.martial_system.auto_train_martials(world_manager.player_entity_id)
        training_results.append("学习了新的武学技能")
        
        # 属性提升
        if current_focus == "internal":
            if attrs.max_mana < 200:
                attrs.max_mana += random.randint(2, 5)
                attrs.mana = min(attrs.mana + 2, attrs.max_mana)
                training_results.append(f"法力上限提升至 {attrs.max_mana}")
        elif current_focus == "external":
            if attrs.physical_attack < 50:
                attrs.physical_attack += random.randint(1, 3)
                training_results.append(f"物理攻击提升至 {attrs.physical_attack}")
        elif current_focus == "balanced":
            # 平衡提升
            if random.random() < 0.5:
                attrs.max_mana += random.randint(1, 2)
                training_results.append("法力略有提升")
            if random.random() < 0.5:
                attrs.physical_attack += 1
                training_results.append("攻击力略有提升")
        
        # 显示结果
        if training_results:
            result_text = "修炼成果:\n" + "\n".join(f"• {r}" for r in training_results)
            QMessageBox.information(self, "修炼完成", result_text)
        else:
            QMessageBox.information(self, "修炼完成", "修炼完成，暂无明显提升")
        
        # 重置状态
        self.training_status.setText("修炼状态: 完成")
        self.one_click_train_btn.setEnabled(True)
        
        # 刷新界面
        self.refresh_martial_lists()
        self.update_training_progress()
        
        # 发送事件更新主界面
        event_bus.emit("character_updated", {
            "health": attrs.health,
            "max_health": attrs.max_health,
            "mana": attrs.mana,
            "max_mana": attrs.max_mana,
            "physical_attack": attrs.physical_attack,
            "spell_attack": attrs.spell_attack
        })
    
    def start_smart_training(self):
        """开始智能修炼"""
        from core.world_manager import world_manager
        if not hasattr(world_manager, 'player_entity_id'):
            return
        
        from core.modules.martial_advisor import MartialAdvisor
        
        advisor = MartialAdvisor()
        analysis = advisor.analyze_character(world_manager.player_entity_id)
        
        if analysis and analysis['next_skills']:
            # 按照建议学习技能
            learned_skills = []
            for skill_rec in analysis['next_skills']:
                if self.martial_system.learn_martial(world_manager.player_entity_id, skill_rec['skill']):
                    learned_skills.append(skill_rec['skill'])
            
            if learned_skills:
                skills_text = "\n".join(f"• {skill}" for skill in learned_skills)
                QMessageBox.information(self, "智能修炼完成", f"根据个性化建议学会了:\n{skills_text}")
                self.refresh_martial_lists()
            else:
                QMessageBox.information(self, "智能修炼", "暂无可学习的推荐技能")
        else:
            QMessageBox.information(self, "智能修炼", "请先在智能建议页面分析角色")
    
    def change_combat_strategy(self, strategy_text):
        """改变战斗策略"""
        strategy_map = {
            "攻防平衡": "balanced",
            "激进攻击": "aggressive",
            "稳健防守": "defensive",
            "技巧流": "technical"
        }
        strategy = strategy_map.get(strategy_text, "balanced")
        
        descriptions = {
            "balanced": "根据情况灵活应对，攻防并重",
            "aggressive": "优先使用攻击技能，快速解决战斗",
            "defensive": "优先防御和恢复，稳扎稳打",
            "technical": "依靠技巧和绝技取胜"
        }
        
        self.strategy_description.setText(descriptions.get(strategy, ""))
        event_bus.emit("combat_strategy_change", {"strategy": strategy})
    
    def update_training_progress(self):
        """更新修炼进度"""
        # 模拟进度数据
        progress_data = {
            "internal": 60,
            "external": 40,
            "agility": 30,
            "special": 20
        }
        
        for type_id, progress in progress_data.items():
            if type_id in self.progress_bars:
                self.progress_bars[type_id].setValue(progress)
    
    def update_combat_stats(self):
        """更新战斗统计"""
        from core.world_manager import world_manager
        
        if hasattr(world_manager, 'auto_combat_system'):
            stats = world_manager.auto_combat_system.get_combat_stats()
            self.wins_label.setText(f"胜利: {stats['wins']}")
            self.losses_label.setText(f"失败: {stats['losses']}")
            self.win_rate_label.setText(f"胜率: {stats['win_rate']:.1f}%")
    
    def toggle_auto_combat(self, state):
        """切换半自动战斗"""
        from core.world_manager import world_manager
        enabled = state == Qt.Checked
        if hasattr(world_manager, 'auto_combat_system'):
            world_manager.auto_combat_system.set_auto_combat(enabled)
    
    def toggle_intervention(self, state):
        """切换干预模式"""
        from core.world_manager import world_manager
        enabled = state == Qt.Checked
        if hasattr(world_manager, 'auto_combat_system'):
            world_manager.auto_combat_system.set_intervention(enabled)
    
    def test_combat(self):
        """测试战斗"""
        from core.world_manager import world_manager
        
        if not hasattr(world_manager, 'player_entity_id'):
            QMessageBox.warning(self, "测试失败", "无法找到玩家角色")
            return
        
        # 创建测试敌人
        enemy_id = self._create_test_enemy()
        if enemy_id:
            if hasattr(world_manager, 'auto_combat_system'):
                world_manager.auto_combat_system.start_combat(world_manager.player_entity_id, enemy_id)
            else:
                QMessageBox.information(self, "测试战斗", "模拟战斗开始！")
    
    def _create_test_enemy(self):
        """创建测试敌人"""
        from core.world_manager import world_manager
        from core.ecs.components import AttributeComponent
        
        enemy_id = world_manager.create_entity()
        enemy_attrs = AttributeComponent(
            health=80,
            max_health=80,
            physical_attack=8,
            defense=3
        )
        world_manager.add_component(enemy_id, enemy_attrs)
        
        return enemy_id
    
    def _on_martial_learned(self, event_data):
        """武学学习事件"""
        self.refresh_martial_lists()
        self.refresh_synergy_effects()
    
    def _on_training_completed(self, event_data):
        """修炼完成事件"""
        self.update_training_progress()
    
    def analyze_character(self):
        """分析角色"""
        from core.world_manager import world_manager
        if not hasattr(world_manager, 'player_entity_id'):
            return
        
        from core.modules.martial_advisor import MartialAdvisor
        
        advisor = MartialAdvisor()
        analysis = advisor.analyze_character(world_manager.player_entity_id)
        
        if analysis:
            # 更新角色类型
            char_type = analysis['character_type']
            self.character_type_label.setText(f"角色类型: {char_type['name']}")
            
            # 更新优势列表
            strengths_text = "优势:\n" + "\n".join(f"• {s}" for s in analysis['strengths'])
            if analysis['weaknesses']:
                strengths_text += "\n\n弱点:\n" + "\n".join(f"• {w}" for w in analysis['weaknesses'])
            self.strengths_text.setText(strengths_text)
            
            # 更新建议技能
            self.next_skills_list.clear()
            for skill_rec in analysis['next_skills']:
                item_text = f"{skill_rec['skill']} - {skill_rec['reason']} (优先级: {skill_rec['priority']})"
                self.next_skills_list.addItem(item_text)
            
            # 更新战斗风格
            combat_style = analysis['combat_style']
            self.combat_style_label.setText(f"推荐战斗风格: {combat_style['name']} - {combat_style['description']}")
    
    def load_beginner_tips(self):
        """加载新手提示"""
        from core.modules.martial_advisor import MartialAdvisor
        
        advisor = MartialAdvisor()
        tips = advisor.get_beginner_tips()
        
        for tip in tips:
            self.tips_list.addItem(tip)
    
    def optimize_martial_build(self):
        """一键优化武学搭配"""
        from core.world_manager import world_manager
        if not hasattr(world_manager, 'player_entity_id') or not self.martial_system:
            return
        
        from core.modules.martial_advisor import MartialAdvisor
        
        advisor = MartialAdvisor()
        analysis = advisor.analyze_character(world_manager.player_entity_id)
        
        if analysis and analysis['next_skills']:
            learned_count = 0
            for skill_rec in analysis['next_skills']:
                if skill_rec['priority'] == '高':
                    if self.martial_system.learn_martial(world_manager.player_entity_id, skill_rec['skill']):
                        learned_count += 1
            
            if learned_count > 0:
                QMessageBox.information(self, "优化完成", f"成功学会了 {learned_count} 个推荐技能！")
                self.refresh_martial_lists()
                self.analyze_character()  # 重新分析
            else:
                QMessageBox.information(self, "优化结果", "暂无可学习的高优先级技能")
    
    def _on_combat_result(self, event_data):
        """战斗结果事件"""
        self.update_combat_stats()