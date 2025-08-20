#!/usr/bin/env python3
"""
游戏功能演示脚本
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from core.events import event_bus
from core.world_manager import world_manager

def demo_game_features():
    """演示游戏功能"""
    print("=== The Path to Divinity - 功能演示 ===\n")
    
    # 设置消息监听
    messages = []
    def on_message(message):
        messages.append(message)
        print(f"[游戏消息] {message}")
    
    event_bus.subscribe("message", on_message)
    
    # 创建游戏
    print("1. 创建角色...")
    game = Game()
    char = game.character
    
    print(f"   角色创建完成！")
    print(f"   修为: {char.power}, 年龄: {char.age}, 天赋: {char.talent}")
    print(f"   生命值: {char.health}, 法力值: {char.mana}")
    print()
    
    # 检查初始法术
    print("2. 检查初始法术...")
    player_entity = world_manager.get_entity(game.player_entity_id)
    skill_component = player_entity.get_component("SkillComponent")
    print(f"   已学法术: {skill_component.learned_spells}")
    print()
    
    # 演示法术施放
    print("3. 演示法术施放...")
    if skill_component.learned_spells:
        spell_id = skill_component.learned_spells[0]
        attr_before = player_entity.get_component("AttributeComponent")
        mana_before = attr_before.mana
        
        print(f"   施放前法力值: {mana_before}")
        event_bus.emit("request_cast_spell", {
            "caster_id": game.player_entity_id,
            "spell_id": spell_id,
            "target_id": None
        })
        
        attr_after = player_entity.get_component("AttributeComponent")
        mana_after = attr_after.mana
        print(f"   施放后法力值: {mana_after}")
        print(f"   消耗法力: {mana_before - mana_after}")
    print()
    
    # 演示修炼
    print("4. 演示修炼系统...")
    power_before = char.power
    print(f"   修炼前修为: {power_before}")
    
    game.train()
    
    power_after = char.power
    print(f"   修炼后修为: {power_after}")
    print(f"   修为增长: {power_after - power_before}")
    print()
    
    # 演示历练
    print("5. 演示历练系统...")
    print("   开始历练...")
    game.adventure()
    print()
    
    # 演示奇遇系统
    print("6. 演示奇遇系统...")
    if hasattr(world_manager, 'encounter_system'):
        print("   尝试触发奇遇...")
        context = {
            "current_day": 7,  # 满足时间触发器
            "world_manager": world_manager
        }
        world_manager.encounter_system._check_encounters_for_entity(game.player_entity_id, context)
    print()
    
    # 显示最终状态
    print("7. 最终角色状态...")
    char = game.character
    print(f"   修为: {char.power}, 年龄: {char.age}")
    print(f"   生命值: {char.health}, 法力值: {char.mana}")
    print(f"   物理攻击: {char.physical_attack}, 法术攻击: {char.spell_attack}")
    
    # 显示已学技能
    learned = game.skill_manager.get_learned_skills()
    if learned:
        print("   已学功法:")
        for skill_id, skill in learned:
            print(f"     - {skill['name']} ({skill.get('grade', '未知')})")
    
    # 显示背包
    inventory = player_entity.get_component("InventoryComponent")
    if inventory and inventory.items:
        print("   背包物品:")
        for item_id, count in inventory.items.items():
            print(f"     - {item_id} x{count}")
    
    print("\n=== 演示完成 ===")
    print(f"总共产生了 {len(messages)} 条游戏消息")

if __name__ == "__main__":
    demo_game_features()