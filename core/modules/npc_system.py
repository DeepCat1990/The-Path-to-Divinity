import random
import json
from ..events import event_bus
from ..data_core import data_core
from ..ecs.components import AttributeComponent, SkillComponent, StateComponent, InventoryComponent

class NPCSystem:
    """NPC系统 - 管理NPC生成、行为和互动"""
    
    def __init__(self, world_manager):
        self.world_manager = world_manager
        self.npc_entities = []
        self.npc_templates = self._load_npc_templates()
        self._setup_event_handlers()
        self._spawn_initial_npcs()
    
    def _load_npc_templates(self):
        """加载NPC模板"""
        try:
            with open("data/npc_templates.json", "r", encoding="utf-8") as f:
                return json.load(f)["npc_templates"]
        except:
            return {}
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("day_changed", self._handle_daily_npc_actions)
        event_bus.subscribe("npc_interaction", self._handle_npc_interaction)
    
    def _spawn_initial_npcs(self):
        """生成初始NPC"""
        npc_count = random.randint(3, 6)
        for _ in range(npc_count):
            template_name = random.choice(list(self.npc_templates.keys()))
            self._create_npc(template_name)
    
    def _create_npc(self, template_name):
        """创建NPC"""
        template = self.npc_templates.get(template_name)
        if not template:
            return None
        
        entity = self.world_manager.entity_manager.create_entity()
        
        # 随机生成属性
        attrs = template["base_attributes"]
        stats = template["initial_stats"]
        
        constitution = random.randint(*attrs["constitution"])
        comprehension = random.randint(*attrs["comprehension"])
        charm = random.randint(*attrs["charm"])
        luck = random.randint(*attrs["luck"])
        spiritual_root = random.randint(*attrs["spiritual_root"])
        
        age = random.randint(*stats["age_range"])
        power = random.randint(*stats["power_range"])
        
        # 添加组件
        entity.add_component("AttributeComponent", AttributeComponent(
            health=stats["health"],
            max_health=stats["health"],
            mana=stats["mana"],
            max_mana=stats["mana"],
            constitution=constitution,
            comprehension=comprehension,
            charm=charm,
            luck=luck,
            spiritual_root=spiritual_root,
            age=age,
            physical_attack=power // 2,
            spell_attack=power // 3
        ))
        
        entity.add_component("SkillComponent", SkillComponent())
        entity.add_component("StateComponent", StateComponent())
        entity.add_component("InventoryComponent", InventoryComponent())
        
        # NPC特有数据
        npc_name = random.choice(template["name_pool"])
        entity.npc_data = {
            "name": npc_name,
            "template": template_name,
            "behavior": template["behavior"],
            "personality": template["personality"],
            "power": power
        }
        
        self.npc_entities.append(entity.id)
        
        event_bus.emit("message", f"{npc_name} 来到了这个世界")
        return entity.id
    
    def _handle_daily_npc_actions(self, current_day):
        """处理NPC每日行为"""
        for npc_id in self.npc_entities[:]:  # 复制列表避免修改时出错
            npc_entity = self.world_manager.get_entity(npc_id)
            if not npc_entity:
                self.npc_entities.remove(npc_id)
                continue
            
            self._execute_npc_daily_action(npc_entity)
    
    def _execute_npc_daily_action(self, npc_entity):
        """执行NPC每日行为"""
        behavior = npc_entity.npc_data["behavior"]
        npc_name = npc_entity.npc_data["name"]
        
        rand = random.random()
        
        if rand < behavior["train_probability"]:
            self._npc_train(npc_entity)
        elif rand < behavior["train_probability"] + behavior["adventure_probability"]:
            self._npc_adventure(npc_entity)
        elif rand < behavior["train_probability"] + behavior["adventure_probability"] + behavior["interact_probability"]:
            self._npc_interact_with_player(npc_entity)
    
    def _npc_train(self, npc_entity):
        """NPC修炼"""
        attr = npc_entity.get_component("AttributeComponent")
        if not attr:
            return
        
        # 修炼提升
        gain = random.randint(1, 3) + attr.comprehension // 3
        npc_entity.npc_data["power"] += gain
        attr.physical_attack += gain // 2
        attr.spell_attack += gain // 3
        
        npc_name = npc_entity.npc_data["name"]
        if random.random() < 0.3:  # 30%概率显示消息
            event_bus.emit("message", f"{npc_name} 在静心修炼")
    
    def _npc_adventure(self, npc_entity):
        """NPC历练"""
        attr = npc_entity.get_component("AttributeComponent")
        inventory = npc_entity.get_component("InventoryComponent")
        npc_name = npc_entity.npc_data["name"]
        
        if not attr or not inventory:
            return
        
        # 历练可能的结果
        outcomes = [
            {"type": "gain_item", "item": "qi_gathering_pill", "count": random.randint(1, 3)},
            {"type": "gain_power", "amount": random.randint(2, 5)},
            {"type": "injury", "damage": random.randint(5, 15)},
            {"type": "breakthrough", "power_gain": random.randint(10, 20)}
        ]
        
        outcome = random.choice(outcomes)
        
        if outcome["type"] == "gain_item":
            inventory.add_item(outcome["item"], outcome["count"])
            if random.random() < 0.2:
                event_bus.emit("message", f"{npc_name} 历练归来，收获颇丰")
        
        elif outcome["type"] == "gain_power":
            npc_entity.npc_data["power"] += outcome["amount"]
            if random.random() < 0.2:
                event_bus.emit("message", f"{npc_name} 历练中有所感悟")
        
        elif outcome["type"] == "injury":
            attr.health = max(1, attr.health - outcome["damage"])
            if random.random() < 0.3:
                event_bus.emit("message", f"{npc_name} 历练时受了些伤")
        
        elif outcome["type"] == "breakthrough":
            npc_entity.npc_data["power"] += outcome["power_gain"]
            if random.random() < 0.5:
                event_bus.emit("message", f"{npc_name} 历练中突破了境界！")
    
    def _npc_interact_with_player(self, npc_entity):
        """NPC与玩家互动"""
        npc_name = npc_entity.npc_data["name"]
        template = npc_entity.npc_data["template"]
        
        # 根据NPC类型决定互动内容
        if template == "mysterious_elder":
            self._elder_interaction(npc_entity)
        elif template == "sect_disciple":
            self._disciple_interaction(npc_entity)
        else:
            self._general_interaction(npc_entity)
    
    def _elder_interaction(self, npc_entity):
        """长者互动 - 可能传授技能或给予指点"""
        npc_name = npc_entity.npc_data["name"]
        
        interactions = [
            f"{npc_name}: 年轻人，修仙之路漫漫，切勿急躁。",
            f"{npc_name}: 我观你骨骼清奇，是个修仙的好苗子。",
            f"{npc_name}: 修炼不仅要勤奋，更要有悟性。"
        ]
        
        # 有小概率传授技能
        if random.random() < 0.1:
            event_bus.emit("message", f"{npc_name} 传授了你一些修炼心得")
            event_bus.emit("experience_gained", {
                "entity_id": self.world_manager.player_entity_id,
                "amount": random.randint(20, 50)
            })
        else:
            event_bus.emit("message", random.choice(interactions))
    
    def _disciple_interaction(self, npc_entity):
        """弟子互动 - 可能切磋或交流"""
        npc_name = npc_entity.npc_data["name"]
        
        interactions = [
            f"{npc_name}: 道友，可愿与我切磋一二？",
            f"{npc_name}: 最近修炼遇到了瓶颈，不知道友有何见解？",
            f"{npc_name}: 听闻道友天赋异禀，久仰大名！"
        ]
        
        event_bus.emit("message", random.choice(interactions))
        
        # 有概率发生切磋
        if random.random() < 0.2:
            self._sparring_match(npc_entity)
    
    def _general_interaction(self, npc_entity):
        """一般互动"""
        npc_name = npc_entity.npc_data["name"]
        
        interactions = [
            f"{npc_name}: 道友，修仙路上多保重。",
            f"{npc_name}: 这世道，修仙不易啊。",
            f"{npc_name}: 道友面相不凡，必有大成就。"
        ]
        
        event_bus.emit("message", random.choice(interactions))
    
    def _sparring_match(self, npc_entity):
        """切磋比试"""
        npc_name = npc_entity.npc_data["name"]
        npc_power = npc_entity.npc_data["power"]
        
        # 获取玩家实体
        player_entity = self.world_manager.get_entity(self.world_manager.player_entity_id)
        if not player_entity:
            return
        
        player_attr = player_entity.get_component("AttributeComponent")
        if not player_attr:
            return
        
        player_power = getattr(player_attr, 'power', 20)  # 默认修为
        
        event_bus.emit("message", f"与 {npc_name} 开始切磋...")
        
        # 简单的胜负判定
        if player_power > npc_power * 1.2:
            event_bus.emit("message", "你轻松获胜，获得了修炼经验！")
            event_bus.emit("experience_gained", {
                "entity_id": self.world_manager.player_entity_id,
                "amount": random.randint(10, 30)
            })
        elif player_power < npc_power * 0.8:
            event_bus.emit("message", "你败下阵来，但也有所收获。")
            event_bus.emit("experience_gained", {
                "entity_id": self.world_manager.player_entity_id,
                "amount": random.randint(5, 15)
            })
        else:
            event_bus.emit("message", "势均力敌，平分秋色。")
            event_bus.emit("experience_gained", {
                "entity_id": self.world_manager.player_entity_id,
                "amount": random.randint(8, 20)
            })
    
    def _handle_npc_interaction(self, event_data):
        """处理NPC互动事件"""
        npc_id = event_data.get("npc_id")
        if npc_id in self.npc_entities:
            npc_entity = self.world_manager.get_entity(npc_id)
            if npc_entity:
                self._npc_interact_with_player(npc_entity)
    
    def get_nearby_npcs(self):
        """获取附近的NPC列表"""
        nearby_npcs = []
        for npc_id in self.npc_entities:
            npc_entity = self.world_manager.get_entity(npc_id)
            if npc_entity and hasattr(npc_entity, 'npc_data'):
                nearby_npcs.append({
                    "id": npc_id,
                    "name": npc_entity.npc_data["name"],
                    "template": npc_entity.npc_data["template"],
                    "power": npc_entity.npc_data["power"]
                })
        return nearby_npcs