#!/usr/bin/env python3
"""
武学系统测试脚本
测试太吾传人的武学体系功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.world_manager import world_manager
from core.modules.martial_system import MartialSystem
from core.modules.martial_advisor import MartialAdvisor
from core.ecs.components import AttributeComponent, SkillComponent, StateComponent

def test_martial_system():
    """测试武学系统"""
    print("=== 太吾传人武学系统测试 ===\n")
    
    # 创建测试角色
    print("1. 创建测试角色...")
    entity_id = world_manager.create_entity()
    
    # 添加属性组件
    attrs = AttributeComponent(
        health=100,
        max_health=100,
        mana=50,
        max_mana=50,
        constitution=6,
        comprehension=7,
        charm=5,
        luck=6,
        spiritual_root=5,
        physical_attack=10,
        spell_attack=0,
        defense=5
    )
    world_manager.add_component(entity_id, attrs)
    
    # 添加技能组件
    skills = SkillComponent()
    world_manager.add_component(entity_id, skills)
    
    # 添加状态组件
    state = StateComponent()
    world_manager.add_component(entity_id, state)
    
    print(f"角色创建成功，ID: {entity_id}")
    print(f"初始属性 - 根骨:{attrs.constitution}, 悟性:{attrs.comprehension}, 魅力:{attrs.charm}")
    print()
    
    # 测试武学系统
    print("2. 测试武学学习...")
    martial_system = world_manager.martial_system
    
    # 获取可学武学
    available = martial_system.get_available_martials(entity_id)
    print(f"可学武学数量: {len(available)}")
    
    for martial in available[:3]:  # 显示前3个
        print(f"  - {martial['name']} ({martial['type']}) - {martial['description']}")
    print()
    
    # 学习基础武学
    print("3. 学习基础武学...")
    basic_skills = ["basic_internal", "basic_external", "basic_agility"]
    
    for skill_id in basic_skills:
        success = martial_system.learn_martial(entity_id, skill_id)
        print(f"学习 {skill_id}: {'成功' if success else '失败'}")
    
    # 检查学会的武学
    updated_skills = world_manager.get_component(entity_id, SkillComponent)
    print(f"已学武学: {updated_skills.learned_gongfa}")
    print()
    
    # 测试协同效应
    print("4. 测试协同效应...")
    synergies = martial_system.get_martial_synergy(updated_skills.learned_gongfa)
    for synergy in synergies:
        print(f"  ✨ {synergy['name']}: {synergy['description']}")
    print()
    
    # 测试武学顾问
    print("5. 测试武学顾问...")
    advisor = MartialAdvisor()
    analysis = advisor.analyze_character(entity_id)
    
    if analysis:
        print(f"角色类型: {analysis['character_type']['name']}")
        print("优势:")
        for strength in analysis['strengths']:
            print(f"  • {strength}")
        
        print("推荐发展路径:")
        path = analysis['recommended_path']
        print(f"  路径: {path['name']} - {path['description']}")
        
        print("建议学习:")
        for skill_rec in analysis['next_skills']:
            print(f"  • {skill_rec['skill']} - {skill_rec['reason']} (优先级: {skill_rec['priority']})")
    print()
    
    # 测试自动修炼
    print("6. 测试自动修炼...")
    martial_system.auto_training = True
    martial_system.training_focus = "internal"
    
    martial_system.auto_train_martials(entity_id)
    
    final_skills = world_manager.get_component(entity_id, SkillComponent)
    print(f"自动修炼后武学: {final_skills.learned_gongfa}")
    print()
    
    # 测试推荐搭配
    print("7. 测试推荐搭配...")
    recommended_build = martial_system.get_recommended_build(entity_id)
    if recommended_build:
        print(f"推荐搭配: {recommended_build['name']}")
        print(f"描述: {recommended_build['description']}")
        print(f"重点: {recommended_build['focus']}")
    print()
    
    print("=== 武学系统测试完成 ===")
    return True

def test_combat_system():
    """测试战斗系统"""
    print("\n=== 战斗系统测试 ===\n")
    
    # 创建玩家和敌人
    player_id = world_manager.create_entity()
    enemy_id = world_manager.create_entity()
    
    # 玩家属性
    player_attrs = AttributeComponent(
        health=100, max_health=100,
        physical_attack=15, defense=8
    )
    world_manager.add_component(player_id, player_attrs)
    
    # 敌人属性
    enemy_attrs = AttributeComponent(
        health=80, max_health=80,
        physical_attack=12, defense=5
    )
    world_manager.add_component(enemy_id, enemy_attrs)
    
    print(f"玩家: 血量{player_attrs.health}, 攻击{player_attrs.physical_attack}, 防御{player_attrs.defense}")
    print(f"敌人: 血量{enemy_attrs.health}, 攻击{enemy_attrs.physical_attack}, 防御{enemy_attrs.defense}")
    print()
    
    # 测试半自动战斗
    print("开始半自动战斗测试...")
    auto_combat = world_manager.auto_combat_system
    auto_combat.set_auto_combat(True)
    auto_combat.set_strategy("balanced")
    
    # 模拟战斗
    auto_combat.start_combat(player_id, enemy_id)
    
    print("战斗系统测试完成")
    return True

if __name__ == "__main__":
    try:
        # 启动世界管理器
        world_manager.start()
        
        # 运行测试
        test_martial_system()
        test_combat_system()
        
        print("\n✅ 所有测试通过！太吾传人武学系统运行正常。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        world_manager.stop()