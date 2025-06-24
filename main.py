import sys
from PySide6.QtWidgets import QApplication
from gui.principal import MainWindow  # sua janela vai pra um módulo separado

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())
