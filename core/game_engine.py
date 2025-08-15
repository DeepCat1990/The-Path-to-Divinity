import time
from typing import Dict, Any
from .events import event_bus
from .world_manager import world_manager
from .data_core import data_core

class GameEngine:
    """游戏引擎 - 管理时间流逝和复杂事件循环"""
    
    def __init__(self):
        self.running = False
        self.last_update_time = time.time()
        self.game_speed = 1.0
        self.paused = False
        
        # 时间管理
        self.real_time_elapsed = 0.0
        self.game_time_elapsed = 0.0
        self.day_duration = 60.0  # 现实60秒 = 游戏1天
        self.month_duration = self.day_duration * 30  # 30天 = 1月
        
        # 当前游戏时间
        self.current_day = 1
        self.current_month = 1
        self.current_year = 1
        
        # 事件调度器
        self.scheduled_events = []
        self.recurring_events = {}
        
        self._setup_event_handlers()
        self._initialize_recurring_events()
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        event_bus.subscribe("game_speed_change", self._handle_speed_change)
        event_bus.subscribe("game_pause", self._handle_pause)
        event_bus.subscribe("schedule_event", self._handle_schedule_event)
    
    def _initialize_recurring_events(self):
        """初始化循环事件"""
        self.recurring_events = {
            "daily_events": {"interval": self.day_duration, "last_trigger": 0},
            "monthly_events": {"interval": self.month_duration, "last_trigger": 0},
            "npc_actions": {"interval": self.day_duration, "last_trigger": 0},
            "world_state_update": {"interval": self.day_duration * 7, "last_trigger": 0}  # 每周
        }
    
    def start(self):
        """启动游戏引擎"""
        self.running = True
        self.last_update_time = time.time()
        world_manager.start()
        event_bus.emit("engine_started", {})
    
    def stop(self):
        """停止游戏引擎"""
        self.running = False
        world_manager.stop()
        event_bus.emit("engine_stopped", {})
    
    def update(self):
        """主更新循环"""
        if not self.running or self.paused:
            return
        
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 更新时间
        self._update_time(delta_time)
        
        # 更新世界管理器
        world_manager.update()
        
        # 处理调度事件
        self._process_scheduled_events()
        
        # 处理循环事件
        self._process_recurring_events()
    
    def _update_time(self, delta_time):
        """更新游戏时间"""
        self.real_time_elapsed += delta_time
        self.game_time_elapsed += delta_time * self.game_speed
        
        # 计算新的游戏时间
        new_day = int(self.game_time_elapsed / self.day_duration) + 1
        new_month = int((new_day - 1) / 30) + 1
        new_year = int((new_month - 1) / 12) + 1
        
        # 检查日期变化
        if new_day > self.current_day:
            self._trigger_day_change(new_day)
        
        if new_month > self.current_month:
            self._trigger_month_change(new_month, new_year)
        
        if new_year > self.current_year:
            self._trigger_year_change(new_year)
    
    def _trigger_day_change(self, new_day):
        """触发日期变化"""
        old_day = self.current_day
        self.current_day = new_day
        
        event_bus.emit("day_changed", {
            "old_day": old_day,
            "new_day": new_day,
            "total_days": new_day
        })
    
    def _trigger_month_change(self, new_month, new_year):
        """触发月份变化"""
        old_month = self.current_month
        self.current_month = new_month % 12 if new_month % 12 != 0 else 12
        self.current_year = new_year
        
        total_months = (new_year - 1) * 12 + self.current_month
        
        event_bus.emit("month_changed", {
            "old_month": old_month,
            "new_month": self.current_month,
            "year": self.current_year,
            "total_months": total_months
        })
        
        # 触发太吾时间系统
        if hasattr(world_manager, 'time_system'):
            world_manager.time_system.current_month = self.current_month
            world_manager.time_system.current_year = self.current_year
            world_manager.time_system._handle_month_change({
                "month": self.current_month,
                "year": self.current_year,
                "total_months": total_months
            })
    
    def _trigger_year_change(self, new_year):
        """触发年份变化"""
        old_year = self.current_year
        self.current_year = new_year
        
        event_bus.emit("year_changed", {
            "old_year": old_year,
            "new_year": new_year
        })
    
    def _process_scheduled_events(self):
        """处理调度事件"""
        current_time = self.game_time_elapsed
        events_to_remove = []
        
        for i, event_data in enumerate(self.scheduled_events):
            if current_time >= event_data["trigger_time"]:
                event_bus.emit(event_data["event_type"], event_data["data"])
                events_to_remove.append(i)
        
        # 移除已触发的事件
        for i in reversed(events_to_remove):
            self.scheduled_events.pop(i)
    
    def _process_recurring_events(self):
        """处理循环事件"""
        current_time = self.game_time_elapsed
        
        for event_type, event_info in self.recurring_events.items():
            if current_time - event_info["last_trigger"] >= event_info["interval"]:
                event_info["last_trigger"] = current_time
                self._trigger_recurring_event(event_type)
    
    def _trigger_recurring_event(self, event_type):
        """触发循环事件"""
        if event_type == "daily_events":
            event_bus.emit("daily_cycle", {"day": self.current_day})
        elif event_type == "monthly_events":
            event_bus.emit("monthly_cycle", {"month": self.current_month, "year": self.current_year})
        elif event_type == "npc_actions":
            event_bus.emit("npc_daily_actions", {"day": self.current_day})
        elif event_type == "world_state_update":
            event_bus.emit("world_state_update", {"week": self.current_day // 7})
    
    def _handle_speed_change(self, event_data):
        """处理游戏速度变化"""
        new_speed = event_data.get("speed", 1.0)
        self.game_speed = max(0.1, min(10.0, new_speed))  # 限制在0.1x到10x之间
        event_bus.emit("message", f"游戏速度调整为 {self.game_speed}x")
    
    def _handle_pause(self, event_data):
        """处理游戏暂停"""
        self.paused = event_data.get("paused", not self.paused)
        status = "暂停" if self.paused else "继续"
        event_bus.emit("message", f"游戏{status}")
    
    def _handle_schedule_event(self, event_data):
        """处理事件调度"""
        trigger_time = self.game_time_elapsed + event_data.get("delay", 0)
        self.scheduled_events.append({
            "trigger_time": trigger_time,
            "event_type": event_data["event_type"],
            "data": event_data.get("data", {})
        })
    
    def schedule_event(self, event_type: str, delay: float, data: Dict[str, Any] = None):
        """调度事件"""
        event_bus.emit("schedule_event", {
            "event_type": event_type,
            "delay": delay,
            "data": data or {}
        })
    
    def set_game_speed(self, speed: float):
        """设置游戏速度"""
        event_bus.emit("game_speed_change", {"speed": speed})
    
    def pause_game(self, paused: bool = None):
        """暂停/继续游戏"""
        event_bus.emit("game_pause", {"paused": paused})
    
    def get_current_time_info(self) -> Dict[str, Any]:
        """获取当前时间信息"""
        return {
            "day": self.current_day,
            "month": self.current_month,
            "year": self.current_year,
            "game_time_elapsed": self.game_time_elapsed,
            "real_time_elapsed": self.real_time_elapsed,
            "game_speed": self.game_speed,
            "paused": self.paused
        }

# 全局游戏引擎实例
game_engine = GameEngine()