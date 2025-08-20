import json
import random
from .character import Character
from .skills import SkillManager
from .sects import SectManager
from .events import event_bus
from .world_manager import world_manager
from .game_engine import game_engine

class Game:
    def __init__(self):
        with open("data/config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        # 显示角色创建界面
        self.character_data = self._show_character_creation()
        
        self.character = Character(self.config["character"])
        self.skill_manager = SkillManager()
        self.sect_manager = SectManager()
        self.day = 1
        
        # 启动游戏引擎
        game_engine.start()
        self.player_entity_id = world_manager.create_player_entity()
        
        # 将玩家实体ID存储到world_manager中供其他模块使用
        world_manager.player_entity_id = self.player_entity_id
        
        # 应用角色创建数据
        self._apply_character_creation_data()
        
        # 初始化时给玩家一个基础法术
        player_entity = world_manager.get_entity(self.player_entity_id)
        if player_entity:
            skill_component = player_entity.get_component("SkillComponent")
            if skill_component and not skill_component.learned_spells:
                skill_component.learned_spells.append("spirit_missile")
                event_bus.emit("message", "你天生掌握了灵力弹法术！")
        
    def train(self):
        self.character.train(self.config["events"]["train"])
        self._sync_character_to_entity()
        self.next_day()
        
    def adventure(self):
        self.character.adventure(self.config["events"]["adventure"])
        self._check_skill_learning()
        self._sync_character_to_entity()
        self.next_day()
        
    def _check_skill_learning(self):
        # 检查普通技能
        available = self.skill_manager.get_available_skills(self.character.power)
        if available and random.random() < 0.2:
            skill_id, skill = random.choice(available)
            self.skill_manager.learn_skill(skill_id)
            event_bus.emit("message", f"领悟了 {skill['name']}！")
            
            # 同步学会的法术到ECS实体
            self._sync_learned_spells(skill_id)
            
        # 检查门派技能
        if self.sect_manager.current_sect:
            sect_skills = self.sect_manager.get_sect_skills(self.sect_manager.current_sect)
            available_sect_skills = [(sid, skill) for sid, skill in sect_skills 
                                   if self.sect_manager.can_learn_sect_skill(sid, self.character)
                                   and sid not in self.skill_manager.learned_skills]
            if available_sect_skills and random.random() < 0.25:
                skill_id, skill = random.choice(available_sect_skills)
                self.skill_manager.learn_skill(skill_id)
                event_bus.emit("message", f"修习了门派绝学 {skill['name']}！")
                self._sync_learned_spells(skill_id)
                
        # 检查是否可以加入门派
        if not self.sect_manager.current_sect and random.random() < 0.1:
            available_sects = self.sect_manager.get_available_sects(self.character)
            if available_sects:
                sect_id, sect = random.choice(available_sects)
                self.sect_manager.join_sect(sect_id, self.character)
    
    def _sync_learned_spells(self, skill_id):
        """同步学会的法术到ECS实体"""
        if hasattr(self, 'player_entity_id'):
            player_entity = world_manager.get_entity(self.player_entity_id)
            if player_entity:
                skill_component = player_entity.get_component("SkillComponent")
                if skill_component:
                    # 从技能数据中获取关联的法术
                    from .data_manager import data_manager
                    technique_data = data_manager.get_technique('combat_techniques', skill_id)
                    if technique_data and 'spells' in technique_data:
                        for spell_id in technique_data['spells']:
                            if spell_id not in skill_component.learned_spells:
                                skill_component.learned_spells.append(spell_id)
                                event_bus.emit("message", f"学会了法术：{spell_id}")
        
    def next_day(self):
        self.day += 1
        event_bus.emit("day_changed", self.day)
        
    def update(self):
        """更新游戏世界"""
        game_engine.update()
        
    def get_time_info(self):
        """获取时间信息"""
        return game_engine.get_current_time_info()
        
    def set_game_speed(self, speed):
        """设置游戏速度"""
        game_engine.set_game_speed(speed)
        
    def pause_game(self, paused=None):
        """暂停/继续游戏"""
        game_engine.pause_game(paused)
        
    def get_sect_info(self):
        return self.sect_manager.get_current_sect_info()
        
    def _sync_character_to_entity(self):
        """同步角色数据到ECS实体"""
        if hasattr(self, 'player_entity_id'):
            player_entity = world_manager.get_entity(self.player_entity_id)
            if player_entity:
                attr = player_entity.get_component("AttributeComponent")
                if attr:
                    # 同步基础属性
                    attr.age = self.character.age
                    attr.health = self.character.health
                    attr.mana = self.character.mana
                    attr.max_mana = self.character.max_mana
                    attr.physical_attack = self.character.physical_attack
                    attr.spell_attack = self.character.spell_attack
                    
                    # 如果没有power属性，添加它
                    if not hasattr(attr, 'power'):
                        attr.power = self.character.power
                    else:
                        attr.power = self.character.power
                        
                    if not hasattr(attr, 'talent'):
                        attr.talent = self.character.talent
                    else:
                        attr.talent = self.character.talent
    
    def _show_character_creation(self):
        """显示角色创建界面"""
        from ui.character_creation_window import CharacterCreationWindow
        
        creation_dialog = CharacterCreationWindow()
        if creation_dialog.exec() == creation_dialog.accepted:
            return creation_dialog.get_character_data()
        else:
            # 使用默认配置
            return {
                "attributes": {
                    "constitution": 3,
                    "determination": 3,
                    "bone_root": 3,
                    "comprehension": 3,
                    "charm": 3,
                    "luck": 3
                },
                "birthplace": None,
                "zhuazhou": None,
                "traits": []
            }
    
    def _apply_character_creation_data(self):
        """应用角色创建数据"""
        if not self.character_data:
            return
        
        from core.world_manager import world_manager
        from core.ecs.components import AttributeComponent
        
        if world_manager.has_component(self.player_entity_id, AttributeComponent):
            attrs = world_manager.get_component(self.player_entity_id, AttributeComponent)
            
            # 应用自定义属性
            custom_attrs = self.character_data.get("attributes", {})
            attrs.constitution = custom_attrs.get("constitution", 3)
            if not hasattr(attrs, 'determination'):
                attrs.determination = custom_attrs.get("determination", 3)
            if not hasattr(attrs, 'bone_root'):
                attrs.bone_root = custom_attrs.get("bone_root", 3)
            attrs.comprehension = custom_attrs.get("comprehension", 3)
            attrs.charm = custom_attrs.get("charm", 3)
            attrs.luck = custom_attrs.get("luck", 3)
            
            # 应用特质效果
            traits = self.character_data.get("traits", [])
            for trait_id, trait_data in traits:
                # 应用特质的其他效果
                if "lifespan_bonus" in trait_data:
                    attrs.lifespan += trait_data["lifespan_bonus"]
                if "health_bonus" in trait_data:
                    attrs.max_health += trait_data["health_bonus"]
                    attrs.health += trait_data["health_bonus"]
            
            # 应用特质的起始技能
            from core.ecs.components import SkillComponent
            if world_manager.has_component(self.player_entity_id, SkillComponent):
                skills = world_manager.get_component(self.player_entity_id, SkillComponent)
                
                for trait_id, trait_data in traits:
                    if "starting_gongfa" in trait_data:
                        skills.learned_gongfa.extend(trait_data["starting_gongfa"])
                        event_bus.emit("message", f"由于{trait_data['name']}，获得了高级功法！")
            
            # 显示创建结果
            birthplace = self.character_data.get("birthplace")
            zhuazhou = self.character_data.get("zhuazhou")
            
            if birthplace:
                event_bus.emit("message", f"出生于{birthplace[1]['name']}，{birthplace[1]['description']}")
            if zhuazhou:
                event_bus.emit("message", f"抓周时选中了{zhuazhou[1]['name']}，{zhuazhou[1]['description']}")
            if traits:
                trait_names = [t[1]['name'] for t in traits]
                event_bus.emit("message", f"获得了特质：{', '.join(trait_names)}")