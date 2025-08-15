class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                "background": "#ffffff",
                "text": "#000000",
                "button": "#f0f0f0",
                "button_hover": "#e0e0e0",
                "progress_bg": "#e0e0e0",
                "health_bar": "#ff4444",
                "mana_bar": "#4444ff"
            },
            "dark": {
                "background": "#2b2b2b",
                "text": "#ffffff",
                "button": "#404040",
                "button_hover": "#505050",
                "progress_bg": "#404040",
                "health_bar": "#ff6666",
                "mana_bar": "#6666ff"
            }
        }
    
    def get_stylesheet(self):
        """获取当前主题样式表"""
        theme = self.themes[self.current_theme]
        return f"""
            QMainWindow {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button']};
                color: {theme['text']};
                border: 1px solid #666;
                padding: 5px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:disabled {{
                background-color: #888;
                color: #ccc;
            }}
            QProgressBar {{
                border: 1px solid #666;
                border-radius: 3px;
                background-color: {theme['progress_bg']};
            }}
            QTextEdit {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid #666;
            }}
        """
    
    def toggle_theme(self):
        """切换主题"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        return self.get_stylesheet()

theme_manager = ThemeManager()