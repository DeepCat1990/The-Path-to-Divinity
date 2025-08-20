import random
from ..events import event_bus
from ..data_core import data_core

class DamageCalculator:
    """伤害计算器 - 可配置的伤害公式"""
    
    @staticmethod
    def calculate_physical_damage(attacker_attr, target_attr, base_damage):
        """计算物理伤害"""
        # 基础伤害 + 攻击力加成 - 防御减免
        damage = base_damage + attacker_attr.physical_attack
        defense_reduction = target_attr.defense * 0.5
        final_damage = max(1, damage - defense_reduction)
        
        # 暴击计算
        crit_chance = attacker_attr.luck * 0.01
        if random.random() < crit_chance:
            final_damage *= 2
            return int(final_damage), True
        
        return int(final_damage), False
    
    @staticmethod
    def calculate_spell_damage(caster_attr, target_attr, base_damage, element="neutral"):
        """计算法术伤害"""
        # 基础伤害 + 法术攻击力加成
        damage = base_damage + caster_attr.spell_attack
        
        # 元素抗性（如果目标有的话）
        state = target_attr  # 简化处理
        resistance = 0  # 可以从装备或状态中获取抗性
        
        final_damage = max(1, damage * (1 - resistance))
        
        # 法术暴击
        crit_chance = caster_attr.comprehension * 0.005
        if random.random() < crit_chance:
            final_damage *= 1.5
            return int(final_damage), True
        
        return int(final_damage), False

class CombatSystem:
    """战斗系统 - 处理战斗逻辑和伤害计算"""
    
    def __init__(self, world_manager):
        self.world_manager = world_manager
        self.damage_calculator = DamageCalculator()
        self.active_combats = {}
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("combat_start", self._handle_combat_start)
        event_bus.subscribe("attack_request", self._handle_attack_request)
        event_bus.subscribe("spell_cast", self._handle_spell_damage)
        event_bus.subscribe("entity_death", self._handle_entity_death)
    
    def _handle_combat_start(self, event_data):
        """处理战斗开始"""
        attacker_id = event_data["attacker_id"]
        defender_id = event_data["defender_id"]
        
        combat_id = f"{attacker_id}_{defender_id}"
        self.active_combats[combat_id] = {
            "attacker": attacker_id,
            "defender": defender_id,
            "turn": attacker_id,
            "round": 1
        }
        
        event_bus.emit("message", "战斗开始！")
    
    def _handle_attack_request(self, event_data):
        """处理攻击请求"""
        attacker_id = event_data["attacker_id"]
        target_id = event_data["target_id"]
        attack_type = event_data.get("attack_type", "physical")
        
        attacker = self.world_manager.get_entity(attacker_id)
        target = self.world_manager.get_entity(target_id)
        
        if not attacker or not target:
            return
        
        attacker_attr = attacker.get_component("AttributeComponent")
        target_attr = target.get_component("AttributeComponent")
        
        if not attacker_attr or not target_attr:
            return
        
        if attack_type == "physical":
            self._execute_physical_attack(attacker_attr, target_attr, attacker_id, target_id)
        elif attack_type == "spell":
            # 法术攻击通过spell_cast事件处理
            pass
    
    def _execute_physical_attack(self, attacker_attr, target_attr, attacker_id, target_id):
        """执行物理攻击"""
        base_damage = attacker_attr.physical_attack
        damage, is_crit = self.damage_calculator.calculate_physical_damage(
            attacker_attr, target_attr, base_damage
        )
        
        # 应用伤害
        target_attr.health = max(0, target_attr.health - damage)
        
        # 发布伤害事件
        event_bus.emit("damage_dealt", {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "damage": damage,
            "is_crit": is_crit,
            "damage_type": "physical"
        })
        
        crit_text = " (暴击!)" if is_crit else ""
        event_bus.emit("message", f"造成 {damage} 点物理伤害{crit_text}")
        
        # 检查死亡
        if target_attr.health <= 0:
            event_bus.emit("entity_death", {"entity_id": target_id})
    
    def _handle_spell_damage(self, event_data):
        """处理法术伤害"""
        caster_id = event_data["caster_id"]
        target_id = event_data.get("target_id")
        spell_data = event_data["spell_data"]
        
        if not target_id:
            return
        
        caster = self.world_manager.get_entity(caster_id)
        target = self.world_manager.get_entity(target_id)
        
        if not caster or not target:
            return
        
        caster_attr = caster.get_component("AttributeComponent")
        target_attr = target.get_component("AttributeComponent")
        
        if not caster_attr or not target_attr:
            return
        
        effects = spell_data.get("effects", {})
        if "damage" in effects:
            base_damage = effects["damage"]
            element = spell_data.get("element", "neutral")
            
            damage, is_crit = self.damage_calculator.calculate_spell_damage(
                caster_attr, target_attr, base_damage, element
            )
            
            # 应用伤害
            target_attr.health = max(0, target_attr.health - damage)
            
            # 发布伤害事件
            event_bus.emit("damage_dealt", {
                "attacker_id": caster_id,
                "target_id": target_id,
                "damage": damage,
                "is_crit": is_crit,
                "damage_type": "spell",
                "element": element
            })
            
            crit_text = " (暴击!)" if is_crit else ""
            event_bus.emit("message", f"法术造成 {damage} 点{element}伤害{crit_text}")
            
            # 检查死亡
            if target_attr.health <= 0:
                event_bus.emit("entity_death", {"entity_id": target_id})
    
    def _handle_entity_death(self, event_data):
        """处理实体死亡"""
        entity_id = event_data["entity_id"]
        
        # 结束相关战斗
        combats_to_end = []
        for combat_id, combat_data in self.active_combats.items():
            if entity_id in [combat_data["attacker"], combat_data["defender"]]:
                combats_to_end.append(combat_id)
        
        for combat_id in combats_to_end:
            del self.active_combats[combat_id]
            event_bus.emit("combat_end", {"combat_id": combat_id})
        
        event_bus.emit("message", "战斗结束！")
    
    def handle_encounter_combat(self, entity_id, enemy_data):
        """处理奇遇战斗"""
        # 创建敌人实体
        enemy_entity = self.world_manager.entity_manager.create_entity()
        from ..ecs.components import AttributeComponent, StateComponent
        
        enemy_attr = AttributeComponent(
            health=enemy_data.get("health", 80),
            max_health=enemy_data.get("health", 80),
            physical_attack=enemy_data.get("attack", 15),
            defense=enemy_data.get("defense", 5)
        )
        enemy_entity.add_component("AttributeComponent", enemy_attr)
        enemy_entity.add_component("StateComponent", StateComponent())
        
        # 开始自动战斗
        self._auto_combat(entity_id, enemy_entity.id, enemy_data.get("name", "未知敌人"))
    
    def _auto_combat(self, player_id, enemy_id, enemy_name):
        """自动战斗"""
        player = self.world_manager.get_entity(player_id)
        enemy = self.world_manager.get_entity(enemy_id)
        
        if not player or not enemy:
            return
        
        player_attr = player.get_component("AttributeComponent")
        enemy_attr = enemy.get_component("AttributeComponent")
        
        event_bus.emit("message", f"与{enemy_name}展开激战！")
        
        # 简单的回合制战斗
        rounds = 0
        while player_attr.health > 0 and enemy_attr.health > 0 and rounds < 10:
            rounds += 1
            
            # 玩家攻击
            player_damage = max(1, player_attr.physical_attack + player_attr.spell_attack - enemy_attr.defense)
            enemy_attr.health = max(0, enemy_attr.health - player_damage)
            
            if enemy_attr.health <= 0:
                event_bus.emit("message", f"击败了{enemy_name}！")
                event_bus.emit("combat_victory", {"player_id": player_id, "enemy_name": enemy_name})
                break
            
            # 敌人攻击
            enemy_damage = max(1, enemy_attr.physical_attack - player_attr.defense)
            player_attr.health = max(0, player_attr.health - enemy_damage)
            
            if player_attr.health <= 0:
                event_bus.emit("message", f"被{enemy_name}击败了...")
                event_bus.emit("combat_defeat", {"player_id": player_id, "enemy_name": enemy_name})
                break
        
        # 清理敌人实体
        self.world_manager.entity_manager.remove_entity(enemy_id)
    
    def start_combat(self, attacker_id, defender_id):
        """开始战斗"""
        event_bus.emit("combat_start", {
            "attacker_id": attacker_id,
            "defender_id": defender_id
        })
    
    def request_attack(self, attacker_id, target_id, attack_type="physical"):
        """请求攻击"""
        event_bus.emit("attack_request", {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "attack_type": attack_type
        })