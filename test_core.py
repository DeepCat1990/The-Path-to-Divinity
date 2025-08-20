#!/usr/bin/env python3
"""
核心功能测试脚本 - 不依赖GUI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from core.events import event_bus
from core.world_manager import world_manager

def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    # 创建游戏实例
    game = Game()
    print(f"游戏初始化完成，玩家实体ID: {game.player_entity_id}")
    
    # 测试角色属性
    char = game.character
    print(f"角色属性 - 修为: {char.power}, 年龄: {char.age}, 天赋: {char.talent}")
    print(f"生命值: {char.health}, 法力值: {char.mana}")
    
    # 测试ECS实体
    player_entity = world_manager.get_entity(game.player_entity_id)
    if player_entity:
        attr = player_entity.get_component("AttributeComponent")
        skill = player_entity.get_component("SkillComponent")
        print(f"ECS实体属性 - 生命: {attr.health}, 法力: {attr.mana}")
        print(f"已学法术: {skill.learned_spells}")
    
    return game

def test_spell_system(game):
    """测试法术系统"""
    print("\n=== 测试法术系统 ===")
    
    player_entity = world_manager.get_entity(game.player_entity_id)
    if player_entity:
        skill_component = player_entity.get_component("SkillComponent")
        if skill_component and skill_component.learned_spells:
            spell_id = skill_component.learned_spells[0]
            print(f"施放法术: {spell_id}")
            
            # 施放法术
            event_bus.emit("request_cast_spell", {
                "caster_id": game.player_entity_id,
                "spell_id": spell_id,
                "target_id": None
            })
            
            # 检查法力消耗
            attr = player_entity.get_component("AttributeComponent")
            print(f"施法后法力值: {attr.mana}")

def test_encounter_system(game):
    """测试奇遇系统"""
    print("\n=== 测试奇遇系统 ===")
    
    if hasattr(world_manager, 'encounter_system'):
        context = {
            "current_day": 7,
            "world_manager": world_manager
        }
        print("尝试触发奇遇...")
        world_manager.encounter_system._check_encounters_for_entity(game.player_entity_id, context)

def test_training(game):
    """测试修炼功能"""
    print("\n=== 测试修炼功能 ===")
    
    old_power = game.character.power
    print(f"修炼前修为: {old_power}")
    
    # 执行修炼
    game.train()
    
    new_power = game.character.power
    print(f"修炼后修为: {new_power}")
    print(f"修为增长: {new_power - old_power}")

def main():
    """主测试函数"""
    print("开始测试游戏核心功能...")
    
    # 设置消息监听
    def on_message(message):
        print(f"[消息] {message}")
    
    event_bus.subscribe("message", on_message)
    
    try:
        # 测试基础功能
        game = test_basic_functionality()
        
        # 测试法术系统
        test_spell_system(game)
        
        # 测试修炼
        test_training(game)
        
        # 测试奇遇系统
        test_encounter_system(game)
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()