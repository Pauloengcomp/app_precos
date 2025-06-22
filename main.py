import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog
)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selecionar Pasta")
        self.setFixedSize(500, 300)

        # Campo de texto para mostrar o caminho
        self.caminho_pasta = QLineEdit()
        self.caminho_pasta.setPlaceholderText("Nenhuma pasta selecionada")

        # Botão para abrir o seletor de pasta
        self.botao_buscar_pasta = QPushButton("Buscar Pasta")
        self.botao_buscar_pasta.clicked.connect(self.selecionar_pasta)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.caminho_pasta)
        layout.addWidget(self.botao_buscar_pasta)
        self.setLayout(layout)

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if pasta:
            self.caminho_pasta.setText(pasta)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())
