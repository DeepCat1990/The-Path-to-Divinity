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
        self.character = Character(self.config["character"])
        self.skill_manager = SkillManager()
        self.sect_manager = SectManager()
        self.day = 1
        
        # 启动游戏引擎
        game_engine.start()
        self.player_entity_id = world_manager.create_player_entity()
        
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
                
        # 检查是否可以加入门派
        if not self.sect_manager.current_sect and random.random() < 0.1:
            available_sects = self.sect_manager.get_available_sects(self.character)
            if available_sects:
                sect_id, sect = random.choice(available_sects)
                self.sect_manager.join_sect(sect_id, self.character)
        
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