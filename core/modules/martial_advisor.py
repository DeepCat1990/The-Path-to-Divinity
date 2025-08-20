from ..events import event_bus

class MartialAdvisor:
    """武学顾问系统 - 为新手提供建议"""
    
    def __init__(self):
        self.advice_history = []
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        event_bus.subscribe("martial_advice_request", self._handle_advice_request)
        event_bus.subscribe("character_analysis_request", self._handle_analysis_request)
    
    def analyze_character(self, character_id):
        """分析角色并给出建议"""
        from ..world_manager import world_manager
        from ..ecs.components import AttributeComponent, SkillComponent
        
        if not world_manager.has_component(character_id, AttributeComponent):
            return None
        
        attrs = world_manager.get_component(character_id, AttributeComponent)
        skills = world_manager.get_component(character_id, SkillComponent)
        
        analysis = {
            "character_type": self._determine_character_type(attrs),
            "strengths": self._identify_strengths(attrs),
            "weaknesses": self._identify_weaknesses(attrs),
            "recommended_path": self._recommend_path(attrs, skills),
            "next_skills": self._recommend_next_skills(attrs, skills),
            "combat_style": self._recommend_combat_style(attrs, skills)
        }
        
        return analysis
    
    def _determine_character_type(self, attrs):
        """判断角色类型"""
        scores = {
            "warrior": attrs.constitution + attrs.physical_attack,
            "mage": attrs.comprehension + attrs.spiritual_root,
            "agile": attrs.charm + (attrs.luck if hasattr(attrs, 'luck') else 5),
            "balanced": (attrs.constitution + attrs.comprehension + attrs.charm) // 3
        }
        
        max_type = max(scores, key=scores.get)
        
        type_names = {
            "warrior": "武者型",
            "mage": "法师型", 
            "agile": "敏捷型",
            "balanced": "全能型"
        }
        
        return {
            "type": max_type,
            "name": type_names[max_type],
            "score": scores[max_type]
        }
    
    def _identify_strengths(self, attrs):
        """识别角色优势"""
        strengths = []
        
        if attrs.constitution >= 7:
            strengths.append("体质强健，适合修炼外功")
        if attrs.comprehension >= 7:
            strengths.append("悟性极高，适合修炼内功")
        if attrs.charm >= 7:
            strengths.append("魅力出众，适合社交和身法")
        if hasattr(attrs, 'luck') and attrs.luck >= 7:
            strengths.append("福缘深厚，容易获得奇遇")
        if attrs.spiritual_root >= 6:
            strengths.append("灵根优异，法术天赋卓越")
        
        if not strengths:
            strengths.append("属性均衡，发展潜力巨大")
        
        return strengths
    
    def _identify_weaknesses(self, attrs):
        """识别角色弱点"""
        weaknesses = []
        
        if attrs.constitution <= 3:
            weaknesses.append("体质较弱，需要加强锻炼")
        if attrs.comprehension <= 3:
            weaknesses.append("悟性不足，学习较慢")
        if attrs.charm <= 3:
            weaknesses.append("魅力欠缺，社交困难")
        if attrs.spiritual_root <= 2:
            weaknesses.append("灵根资质一般，法术修炼困难")
        
        return weaknesses
    
    def _recommend_path(self, attrs, skills):
        """推荐发展路径"""
        char_type = self._determine_character_type(attrs)
        
        paths = {
            "warrior": {
                "name": "刚猛武者",
                "description": "专精外功，以力破巧",
                "priority": ["basic_external", "iron_body", "tiger_fist"],
                "style": "近战强攻"
            },
            "mage": {
                "name": "内力大师",
                "description": "深厚内功，法术无双",
                "priority": ["basic_internal", "deep_meditation", "qi_burst"],
                "style": "远程法术"
            },
            "agile": {
                "name": "身法高手",
                "description": "身轻如燕，变化莫测",
                "priority": ["basic_agility", "light_step", "shadow_clone"],
                "style": "灵活机动"
            },
            "balanced": {
                "name": "全能修士",
                "description": "内外兼修，攻防并重",
                "priority": ["basic_internal", "basic_external", "basic_agility"],
                "style": "均衡发展"
            }
        }
        
        return paths.get(char_type["type"], paths["balanced"])
    
    def _recommend_next_skills(self, attrs, skills):
        """推荐下一个学习的技能"""
        learned = skills.learned_gongfa if skills else []
        recommendations = []
        
        # 基础技能推荐
        if "basic_internal" not in learned and attrs.constitution >= 3:
            recommendations.append({
                "skill": "basic_internal",
                "reason": "基础内功是所有修炼的根基",
                "priority": "高"
            })
        
        if "basic_external" not in learned and attrs.constitution >= 4:
            recommendations.append({
                "skill": "basic_external", 
                "reason": "强身健体，提升战斗能力",
                "priority": "高"
            })
        
        if "basic_agility" not in learned and attrs.constitution >= 3:
            recommendations.append({
                "skill": "basic_agility",
                "reason": "身法是保命的关键",
                "priority": "中"
            })
        
        # 进阶技能推荐
        if "basic_external" in learned and attrs.constitution >= 6:
            if "iron_body" not in learned:
                recommendations.append({
                    "skill": "iron_body",
                    "reason": "大幅提升防御力",
                    "priority": "中"
                })
            if "tiger_fist" not in learned:
                recommendations.append({
                    "skill": "tiger_fist",
                    "reason": "强力攻击技能",
                    "priority": "中"
                })
        
        if "basic_internal" in learned and attrs.comprehension >= 7:
            if "deep_meditation" not in learned:
                recommendations.append({
                    "skill": "deep_meditation",
                    "reason": "大幅提升法力和法术攻击",
                    "priority": "高"
                })
        
        return recommendations[:3]  # 最多返回3个推荐
    
    def _recommend_combat_style(self, attrs, skills):
        """推荐战斗风格"""
        learned = skills.learned_gongfa if skills else []
        
        # 根据已学技能推荐战斗风格
        external_count = sum(1 for skill in learned if skill in ["basic_external", "iron_body", "tiger_fist"])
        internal_count = sum(1 for skill in learned if skill in ["basic_internal", "deep_meditation", "qi_burst"])
        agility_count = sum(1 for skill in learned if skill in ["basic_agility", "light_step", "shadow_clone"])
        
        if external_count >= 2:
            return {
                "style": "aggressive",
                "name": "激进攻击",
                "description": "利用强大的外功直接压制敌人"
            }
        elif internal_count >= 2:
            return {
                "style": "technical",
                "name": "技巧流",
                "description": "运用内功和法术巧妙制胜"
            }
        elif agility_count >= 2:
            return {
                "style": "defensive",
                "name": "稳健防守",
                "description": "依靠身法和防御消耗敌人"
            }
        else:
            return {
                "style": "balanced",
                "name": "攻防平衡",
                "description": "根据情况灵活应对"
            }
    
    def get_beginner_tips(self):
        """获取新手提示"""
        tips = [
            "💡 建议先学习基础内功和外功，打好根基",
            "⚡ 武学之间存在协同效应，合理搭配事半功倍",
            "🎯 根据自己的属性特点选择发展方向",
            "🔄 启用自动修炼可以节省时间",
            "⚔️ 半自动战斗适合新手，关键时刻可以手动干预",
            "📈 定期查看武学推荐，优化发展路径"
        ]
        return tips
    
    def get_synergy_advice(self, learned_skills):
        """获取协同效应建议"""
        advice = []
        
        # 检查常见组合
        if "basic_internal" in learned_skills and "basic_external" in learned_skills:
            advice.append("✨ 内外兼修：你已经掌握了内外功的基础，可以考虑学习更高级的技能")
        
        if "iron_body" in learned_skills and "tiger_fist" not in learned_skills:
            advice.append("🥊 建议学习猛虎拳，与铁布衫形成刚猛无双的组合")
        
        if "deep_meditation" in learned_skills and "qi_burst" not in learned_skills:
            advice.append("💥 建议学习真气爆发，发挥深厚内力的优势")
        
        if len(learned_skills) >= 3 and not any(skill in learned_skills for skill in ["shadow_clone", "qi_burst"]):
            advice.append("🌟 可以考虑学习一些绝技，增加战斗的变化")
        
        return advice
    
    def _handle_advice_request(self, event_data):
        """处理建议请求"""
        character_id = event_data.get("character_id")
        if character_id:
            analysis = self.analyze_character(character_id)
            if analysis:
                event_bus.emit("martial_advice_response", {
                    "character_id": character_id,
                    "analysis": analysis
                })
    
    def _handle_analysis_request(self, event_data):
        """处理分析请求"""
        character_id = event_data.get("character_id")
        if character_id:
            analysis = self.analyze_character(character_id)
            if analysis:
                # 生成建议文本
                advice_text = self._generate_advice_text(analysis)
                event_bus.emit("character_analysis_response", {
                    "character_id": character_id,
                    "advice_text": advice_text
                })