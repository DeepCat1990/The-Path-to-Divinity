#!/usr/bin/env python3
"""
游戏启动脚本 - 自动检测GUI依赖
"""

import sys
import os

def check_pyside6():
    """检查PySide6是否可用"""
    try:
        import PySide6
        return True
    except ImportError:
        return False

def run_gui_version():
    """运行GUI版本"""
    try:
        from PySide6.QtWidgets import QApplication
        from core.game import Game
        from ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        game = Game()
        window = MainWindow(game)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"GUI版本启动失败: {e}")
        return False

def run_console_version():
    """运行控制台版本"""
    print("=== The Path to Divinity - 控制台版本 ===")
    print("GUI依赖未安装，使用控制台模式")
    print()
    
    from core.game import Game
    from core.events import event_bus
    from core.world_manager import world_manager
    
    # 设置消息监听
    def on_message(message):
        print(f"[游戏] {message}")
    
    event_bus.subscribe("message", on_message)
    
    # 创建游戏
    game = Game()
    
    print(f"角色创建完成！")
    print(f"修为: {game.character.power}, 年龄: {game.character.age}")
    print(f"生命值: {game.character.health}, 法力值: {game.character.mana}")
    print()
    
    # 简单的游戏循环
    day = 1
    while True:
        print(f"=== 第 {day} 天 ===")
        print("1. 修炼 (增加修为)")
        print("2. 历练 (可能遇到奇遇)")
        print("3. 查看状态")
        print("4. 测试法术")
        print("5. 退出游戏")
        
        try:
            choice = input("请选择行动: ").strip()
            
            if choice == "1":
                print("开始修炼...")
                game.train()
                day += 1
                
            elif choice == "2":
                print("外出历练...")
                game.adventure()
                day += 1
                
            elif choice == "3":
                char = game.character
                print(f"修为: {char.power}, 年龄: {char.age}, 天赋: {char.talent}")
                print(f"生命值: {char.health}/{char.max_health}")
                print(f"法力值: {char.mana}/{char.max_mana}")
                print(f"物理攻击: {char.physical_attack}, 法术攻击: {char.spell_attack}")
                
                # 显示已学技能
                learned = game.skill_manager.get_learned_skills()
                if learned:
                    print("已学功法:")
                    for skill_id, skill in learned:
                        print(f"  - {skill['name']} ({skill.get('grade', '未知')})")
                else:
                    print("尚未学会任何功法")
                
            elif choice == "4":
                player_entity = world_manager.get_entity(game.player_entity_id)
                if player_entity:
                    skill_component = player_entity.get_component("SkillComponent")
                    if skill_component and skill_component.learned_spells:
                        spell_id = skill_component.learned_spells[0]
                        print(f"施放法术: {spell_id}")
                        event_bus.emit("request_cast_spell", {
                            "caster_id": game.player_entity_id,
                            "spell_id": spell_id,
                            "target_id": None
                        })
                    else:
                        print("尚未学会任何法术")
                
            elif choice == "5":
                print("感谢游玩！")
                break
                
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n游戏被中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

def main():
    """主函数"""
    print("正在启动 The Path to Divinity...")
    
    if check_pyside6():
        print("检测到GUI依赖，启动图形界面版本...")
        if not run_gui_version():
            print("GUI版本启动失败，切换到控制台版本")
            run_console_version()
    else:
        print("未检测到PySide6，启动控制台版本...")
        print("如需图形界面，请安装: pip install PySide6")
        print()
        run_console_version()

if __name__ == "__main__":
    main()