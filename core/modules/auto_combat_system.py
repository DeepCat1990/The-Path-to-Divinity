import random
from ..events import event_bus

class AutoCombatSystem:
    """半自动战斗系统"""
    
    def __init__(self):
        self.auto_combat_enabled = False
        self.intervention_enabled = True
        self.current_strategy = "balanced"
        self.combat_stats = {"wins": 0, "losses": 0}
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        event_bus.subscribe("combat_start", self._handle_combat_start)
        event_bus.subscribe("combat_turn", self._handle_combat_turn)
        event_bus.subscribe("player_intervention", self._handle_intervention)
    
    def start_combat(self, player_id, enemy_id):
        """开始战斗"""
        combat_data = {
            "player_id": player_id,
            "enemy_id": enemy_id,
            "turn": 1,
            "auto_mode": self.auto_combat_enabled
        }
        
        event_bus.emit("combat_start", combat_data)
        
        if self.auto_combat_enabled:
            self._execute_auto_combat(combat_data)
        else:
            self._execute_manual_combat(combat_data)
    
    def _execute_auto_combat(self, combat_data):
        """执行自动战斗"""
        from ..world_manager import world_manager
        from ..ecs.components import AttributeComponent
        
        player_id = combat_data["player_id"]
        enemy_id = combat_data["enemy_id"]
        
        # 获取战斗双方属性
        player_attrs = world_manager.get_component(player_id, AttributeComponent)
        enemy_attrs = world_manager.get_component(enemy_id, AttributeComponent)
        
        if not player_attrs or not enemy_attrs:
            return
        
        # 简化的自动战斗循环
        max_turns = 10
        for turn in range(1, max_turns + 1):
            # 检查是否需要玩家干预
            if self._should_intervene(player_attrs, enemy_attrs, turn):
                event_bus.emit("combat_intervention_request", {
                    "turn": turn,
                    "player_health": player_attrs.health,
                    "enemy_health": enemy_attrs.health
                })
                return  # 等待玩家决策
            
            # 执行自动回合
            self._execute_auto_turn(player_id, enemy_id, turn)
            
            # 检查战斗结束条件
            if player_attrs.health <= 0:
                self._end_combat(False, "玩家败北")
                return
            elif enemy_attrs.health <= 0:
                self._end_combat(True, "战斗胜利")
                return
        
        # 超时平局
        self._end_combat(None, "战斗超时")
    
    def _execute_manual_combat(self, combat_data):
        """执行手动战斗"""
        event_bus.emit("combat_manual_turn", combat_data)
    
    def _execute_auto_turn(self, player_id, enemy_id, turn):
        """执行自动回合"""
        from ..world_manager import world_manager
        from ..ecs.components import AttributeComponent, SkillComponent
        
        player_attrs = world_manager.get_component(player_id, AttributeComponent)
        enemy_attrs = world_manager.get_component(enemy_id, AttributeComponent)
        player_skills = world_manager.get_component(player_id, SkillComponent)
        
        # 根据策略选择行动
        action = self._choose_action(player_attrs, enemy_attrs, player_skills)
        
        # 执行行动
        damage = self._execute_action(action, player_attrs, enemy_attrs)
        
        # 敌人反击
        enemy_damage = self._enemy_attack(enemy_attrs, player_attrs)
        
        event_bus.emit("combat_turn_result", {
            "turn": turn,
            "player_action": action,
            "player_damage": damage,
            "enemy_damage": enemy_damage,
            "player_health": player_attrs.health,
            "enemy_health": enemy_attrs.health
        })
    
    def _choose_action(self, player_attrs, enemy_attrs, player_skills):
        """根据策略选择行动"""
        health_ratio = player_attrs.health / player_attrs.max_health
        enemy_health_ratio = enemy_attrs.health / enemy_attrs.max_health
        
        # 根据当前策略决定行动
        if self.current_strategy == "aggressive":
            if enemy_health_ratio < 0.3 and player_skills.learned_spells:
                return {"type": "special", "skill": player_skills.learned_spells[0]}
            else:
                return {"type": "attack"}
        
        elif self.current_strategy == "defensive":
            if health_ratio < 0.4:
                return {"type": "heal"}
            elif health_ratio < 0.7:
                return {"type": "defend"}
            else:
                return {"type": "attack"}
        
        elif self.current_strategy == "technical":
            if player_skills.learned_spells and random.random() < 0.6:
                return {"type": "special", "skill": random.choice(player_skills.learned_spells)}
            else:
                return {"type": "attack"}
        
        else:  # balanced
            if health_ratio < 0.3:
                return {"type": "heal"}
            elif enemy_health_ratio < 0.2 and player_skills.learned_spells:
                return {"type": "special", "skill": player_skills.learned_spells[0]}
            else:
                return {"type": "attack"}
    
    def _execute_action(self, action, player_attrs, enemy_attrs):
        """执行玩家行动"""
        if action["type"] == "attack":
            damage = max(1, player_attrs.physical_attack - enemy_attrs.defense // 2)
            damage += random.randint(-2, 3)  # 随机变化
            enemy_attrs.health = max(0, enemy_attrs.health - damage)
            return damage
        
        elif action["type"] == "special":
            if player_attrs.mana >= 10:
                damage = max(1, player_attrs.spell_attack + player_attrs.physical_attack // 2)
                damage += random.randint(0, 5)
                player_attrs.mana -= 10
                enemy_attrs.health = max(0, enemy_attrs.health - damage)
                return damage
            else:
                # 法力不足，普通攻击
                return self._execute_action({"type": "attack"}, player_attrs, enemy_attrs)
        
        elif action["type"] == "heal":
            heal_amount = min(20, player_attrs.max_health - player_attrs.health)
            player_attrs.health += heal_amount
            return -heal_amount  # 负数表示治疗
        
        elif action["type"] == "defend":
            # 防御减少下回合受到的伤害
            return 0
        
        return 0
    
    def _enemy_attack(self, enemy_attrs, player_attrs):
        """敌人攻击"""
        damage = max(1, enemy_attrs.physical_attack - player_attrs.defense // 2)
        damage += random.randint(-1, 2)
        player_attrs.health = max(0, player_attrs.health - damage)
        return damage
    
    def _should_intervene(self, player_attrs, enemy_attrs, turn):
        """判断是否需要玩家干预"""
        if not self.intervention_enabled:
            return False
        
        health_ratio = player_attrs.health / player_attrs.max_health
        
        # 关键时刻需要干预
        if health_ratio < 0.25:  # 血量危险
            return True
        if turn == 1:  # 第一回合
            return True
        if enemy_attrs.health / enemy_attrs.max_health < 0.2:  # 敌人即将败北
            return True
        
        return False
    
    def _end_combat(self, victory, message):
        """结束战斗"""
        if victory is True:
            self.combat_stats["wins"] += 1
        elif victory is False:
            self.combat_stats["losses"] += 1
        
        event_bus.emit("combat_end", {
            "victory": victory,
            "message": message,
            "stats": self.combat_stats.copy()
        })
        
        event_bus.emit("message", message)
    
    def _handle_combat_start(self, event_data):
        """处理战斗开始"""
        event_bus.emit("message", "战斗开始！")
    
    def _handle_combat_turn(self, event_data):
        """处理战斗回合"""
        pass
    
    def _handle_intervention(self, event_data):
        """处理玩家干预"""
        action = event_data.get("action")
        if action:
            event_bus.emit("message", f"玩家选择：{action}")
    
    def set_auto_combat(self, enabled):
        """设置自动战斗"""
        self.auto_combat_enabled = enabled
        event_bus.emit("message", f"半自动战斗{'开启' if enabled else '关闭'}")
    
    def set_intervention(self, enabled):
        """设置干预模式"""
        self.intervention_enabled = enabled
        event_bus.emit("message", f"关键时刻干预{'开启' if enabled else '关闭'}")
    
    def set_strategy(self, strategy):
        """设置战斗策略"""
        self.current_strategy = strategy
        strategy_names = {
            "aggressive": "激进攻击",
            "defensive": "稳健防守",
            "balanced": "攻防平衡",
            "technical": "技巧流"
        }
        name = strategy_names.get(strategy, strategy)
        event_bus.emit("message", f"战斗策略设为：{name}")
    
    def get_combat_stats(self):
        """获取战斗统计"""
        total = self.combat_stats["wins"] + self.combat_stats["losses"]
        win_rate = (self.combat_stats["wins"] / total * 100) if total > 0 else 0
        
        return {
            "wins": self.combat_stats["wins"],
            "losses": self.combat_stats["losses"],
            "win_rate": win_rate
        }