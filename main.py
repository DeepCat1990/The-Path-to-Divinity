import sys
from PySide6.QtWidgets import QApplication
from core.game import Game
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    window = MainWindow(game)
    window.show()
    sys.exit(app.exec())