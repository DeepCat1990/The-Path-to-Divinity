import random
from ..events import event_bus
from ..ecs.components import AttributeComponent, SkillComponent, StateComponent

class GenerationSystem:
    """世代传承系统 - 太吾传人核心"""
    
    def __init__(self):
        self.current_generation = 1
        self.family_tree = {}
        self.current_character_id = None
        self.marriage_candidates = []
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        event_bus.subscribe("character_death", self._handle_character_death)
        event_bus.subscribe("marriage_proposal", self._handle_marriage)
    
    def create_character(self, name="太吾传人", parent_ids=None):
        """创建新角色"""
        from ..world_manager import world_manager
        
        # 生成基础属性
        attributes = self._generate_attributes(parent_ids)
        skills = SkillComponent()
        state = StateComponent()
        
        # 如果有父母，继承部分技能
        if parent_ids:
            skills = self._inherit_skills(parent_ids)
        
        # 创建实体
        entity_id = world_manager.create_entity()
        world_manager.add_component(entity_id, attributes)
        world_manager.add_component(entity_id, skills)
        world_manager.add_component(entity_id, state)
        
        # 记录家族信息
        self.family_tree[entity_id] = {
            "name": name,
            "generation": self.current_generation,
            "parents": parent_ids or [],
            "children": [],
            "spouse": None,
            "birth_year": getattr(world_manager.time_system, 'current_year', 1)
        }
        
        self.current_character_id = entity_id
        
        event_bus.emit("character_created", {
            "entity_id": entity_id,
            "name": name,
            "generation": self.current_generation
        })
        
        return entity_id
    
    def _generate_attributes(self, parent_ids=None):
        """生成角色属性"""
        if not parent_ids:
            # 初代角色 - 随机属性
            return AttributeComponent(
                health=random.randint(80, 120),
                max_health=random.randint(80, 120),
                constitution=random.randint(3, 8),
                comprehension=random.randint(3, 8),
                charm=random.randint(3, 8),
                luck=random.randint(3, 8),
                spiritual_root=random.randint(2, 5),
                age=16,
                lifespan=random.randint(70, 90)
            )
        else:
            # 继承父母属性
            return self._inherit_attributes(parent_ids)
    
    def _inherit_attributes(self, parent_ids):
        """继承父母属性"""
        from ..world_manager import world_manager
        
        # 获取父母属性
        parent_attrs = []
        for parent_id in parent_ids:
            if world_manager.has_component(parent_id, AttributeComponent):
                parent_attrs.append(world_manager.get_component(parent_id, AttributeComponent))
        
        if not parent_attrs:
            return self._generate_attributes()
        
        # 计算平均值并加入随机变异
        avg_constitution = sum(p.constitution for p in parent_attrs) // len(parent_attrs)
        avg_comprehension = sum(p.comprehension for p in parent_attrs) // len(parent_attrs)
        avg_charm = sum(p.charm for p in parent_attrs) // len(parent_attrs)
        avg_luck = sum(p.luck for p in parent_attrs) // len(parent_attrs)
        avg_spiritual_root = sum(p.spiritual_root for p in parent_attrs) // len(parent_attrs)
        
        # 变异范围 ±2
        return AttributeComponent(
            health=random.randint(80, 120),
            max_health=random.randint(80, 120),
            constitution=max(1, min(10, avg_constitution + random.randint(-2, 2))),
            comprehension=max(1, min(10, avg_comprehension + random.randint(-2, 2))),
            charm=max(1, min(10, avg_charm + random.randint(-2, 2))),
            luck=max(1, min(10, avg_luck + random.randint(-2, 2))),
            spiritual_root=max(1, min(10, avg_spiritual_root + random.randint(-1, 1))),
            age=16,
            lifespan=random.randint(70, 90)
        )
    
    def _inherit_skills(self, parent_ids):
        """继承父母技能"""
        from ..world_manager import world_manager
        
        inherited_skills = SkillComponent()
        
        for parent_id in parent_ids:
            if world_manager.has_component(parent_id, SkillComponent):
                parent_skills = world_manager.get_component(parent_id, SkillComponent)
                
                # 30%概率继承每个法术
                for spell in parent_skills.learned_spells:
                    if random.random() < 0.3:
                        inherited_skills.learned_spells.append(spell)
                
                # 50%概率继承每个功法
                for gongfa in parent_skills.learned_gongfa:
                    if random.random() < 0.5:
                        inherited_skills.learned_gongfa.append(gongfa)
        
        # 去重
        inherited_skills.learned_spells = list(set(inherited_skills.learned_spells))
        inherited_skills.learned_gongfa = list(set(inherited_skills.learned_gongfa))
        
        return inherited_skills
    
    def find_marriage_candidates(self):
        """寻找婚配对象"""
        from ..world_manager import world_manager
        
        candidates = []
        
        # 生成3-5个候选人
        for _ in range(random.randint(3, 5)):
            candidate = {
                "name": self._generate_npc_name(),
                "age": random.randint(18, 30),
                "constitution": random.randint(3, 8),
                "comprehension": random.randint(3, 8),
                "charm": random.randint(3, 8),
                "compatibility": random.randint(60, 95)  # 相性
            }
            candidates.append(candidate)
        
        self.marriage_candidates = candidates
        
        event_bus.emit("marriage_candidates_found", {"candidates": candidates})
        return candidates
    
    def propose_marriage(self, candidate_index):
        """求婚"""
        if 0 <= candidate_index < len(self.marriage_candidates):
            candidate = self.marriage_candidates[candidate_index]
            
            # 成功率基于相性和魅力
            from ..world_manager import world_manager
            if self.current_character_id and world_manager.has_component(self.current_character_id, AttributeComponent):
                attrs = world_manager.get_component(self.current_character_id, AttributeComponent)
                success_rate = (candidate["compatibility"] + attrs.charm * 5) / 150
                
                if random.random() < success_rate:
                    # 求婚成功
                    self.family_tree[self.current_character_id]["spouse"] = candidate
                    
                    event_bus.emit("marriage_success", {
                        "character_id": self.current_character_id,
                        "spouse": candidate
                    })
                    event_bus.emit("message", f"与{candidate['name']}结为夫妻！")
                    return True
                else:
                    event_bus.emit("message", f"{candidate['name']}拒绝了求婚")
                    return False
        return False
    
    def have_child(self):
        """生育子女"""
        if not self.current_character_id:
            return None
        
        character_info = self.family_tree.get(self.current_character_id)
        if not character_info or not character_info["spouse"]:
            event_bus.emit("message", "需要先结婚才能生育")
            return None
        
        # 创建子女
        child_name = f"{character_info['name']}之子"
        child_id = self.create_character(child_name, [self.current_character_id])
        
        # 更新家族关系
        self.family_tree[self.current_character_id]["children"].append(child_id)
        
        event_bus.emit("child_born", {
            "parent_id": self.current_character_id,
            "child_id": child_id,
            "child_name": child_name
        })
        event_bus.emit("message", f"喜得贵子：{child_name}")
        
        return child_id
    
    def switch_to_next_generation(self, child_id=None):
        """切换到下一代"""
        if not child_id:
            # 自动选择第一个子女
            character_info = self.family_tree.get(self.current_character_id)
            if character_info and character_info["children"]:
                child_id = character_info["children"][0]
            else:
                event_bus.emit("message", "没有子女可以传承")
                return False
        
        if child_id in self.family_tree:
            self.current_character_id = child_id
            self.current_generation += 1
            
            event_bus.emit("generation_changed", {
                "new_character_id": child_id,
                "generation": self.current_generation
            })
            event_bus.emit("message", f"传承至第{self.current_generation}代")
            return True
        
        return False
    
    def _handle_character_death(self, event_data):
        """处理角色死亡"""
        character_id = event_data.get("character_id")
        if character_id == self.current_character_id:
            # 当前角色死亡，尝试传承
            character_info = self.family_tree.get(character_id)
            if character_info and character_info["children"]:
                self.switch_to_next_generation()
            else:
                event_bus.emit("game_over", {"reason": "血脉断绝"})
    
    def _handle_marriage(self, event_data):
        """处理婚姻事件"""
        candidate_index = event_data.get("candidate_index")
        if candidate_index is not None:
            self.propose_marriage(candidate_index)
    
    def _generate_npc_name(self):
        """生成NPC姓名"""
        surnames = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        given_names = ["雪儿", "月儿", "花儿", "玉儿", "凤儿", "燕儿", "莲儿", "梅儿"]
        return random.choice(surnames) + random.choice(given_names)
    
    def create_character_with_attributes(self, name, char_data):
        """使用指定属性创建角色"""
        from ..world_manager import world_manager
        
        # 使用自定义属性
        attributes = char_data.get("attributes", {})
        
        custom_attrs = AttributeComponent(
            health=random.randint(80, 120),
            max_health=random.randint(80, 120),
            constitution=attributes.get("constitution", 5),
            comprehension=attributes.get("comprehension", 5),
            charm=attributes.get("charm", 5),
            luck=attributes.get("luck", 5),
            spiritual_root=attributes.get("spiritual_root", 5),
            age=16,
            lifespan=random.randint(70, 90)
        )
        
        skills = SkillComponent()
        state = StateComponent()
        
        # 添加推荐配置的技能
        selected_build = char_data.get("selected_build")
        if selected_build and "starting_skills" in selected_build:
            skills.learned_spells.extend(selected_build["starting_skills"])
        
        # 创建实体
        entity_id = world_manager.create_entity()
        world_manager.add_component(entity_id, custom_attrs)
        world_manager.add_component(entity_id, skills)
        world_manager.add_component(entity_id, state)
        
        # 记录家族信息
        self.family_tree[entity_id] = {
            "name": name,
            "generation": self.current_generation + 1,
            "parents": [],
            "children": [],
            "spouse": None,
            "birth_year": getattr(world_manager.time_system, 'current_year', 1),
            "custom_created": True
        }
        
        event_bus.emit("character_created", {
            "entity_id": entity_id,
            "name": name,
            "generation": self.current_generation + 1
        })
        
        return entity_id
    
    def get_family_info(self):
        """获取家族信息"""
        return {
            "current_generation": self.current_generation,
            "current_character": self.current_character_id,
            "family_tree": self.family_tree
        }