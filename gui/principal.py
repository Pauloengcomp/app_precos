from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QLabel, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import os, sys
from conversor.excel_para_txt import converter_df_para_txt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor Excel → TXT")
        # Determina o caminho correto para o ícone, mesmo no executável gerado com PyInstaller
        if getattr(sys, 'frozen', False):
            caminho_icone = os.path.join(sys._MEIPASS, 'icone.ico')
        else:
            caminho_icone = 'icone.ico'

        self.setWindowIcon(QIcon(caminho_icone))
        self.setFixedSize(500, 300)

        # Modelos de planilha
        self.perfis_planilhas = {
            "Modelo Original": {"skiprows": 0, "colunas": None},
            "Planserv Mat": {"skiprows": 0, "colunas": [0, 2, 4]},
            "Planserv Med": {"skiprows": 1, "colunas": [2, 3, 4, 6, 6]}
        }

        self.combo_modelo = QComboBox()
        self.combo_modelo.addItems(self.perfis_planilhas.keys())
        self.combo_modelo.currentTextChanged.connect(self.atualizar_preview_modelo)

        self.caminho_excel_atual = None

        self.caminho_arquivo = QLineEdit()
        self.caminho_arquivo.setPlaceholderText("Nenhum arquivo selecionado")

        self.botao_buscar_arquivo = QPushButton("Selecionar Arquivo Excel")
        self.botao_buscar_arquivo.clicked.connect(self.selecionar_arquivo)

        self.botao_converter = QPushButton("Converter para TXT")
        self.botao_converter.clicked.connect(self.converter_arquivo)

        self.preview_tabela = QTableWidget()
        self.preview_tabela.setRowCount(0)
        self.preview_tabela.setColumnCount(0)

        layout = QVBoxLayout()
        
        layout.addWidget(self.caminho_arquivo)
        layout.addWidget(self.botao_buscar_arquivo)

        layout.addWidget(QLabel("Modelo de planilha:"))
        layout.addWidget(self.combo_modelo)

        layout.addWidget(self.preview_tabela)
        layout.addWidget(self.botao_converter)

        rodape = QLabel("Desenvolvido por Paulo Lima - Alphacare")
        rodape.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rodape.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(rodape)
        self.setLayout(layout)

    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Excel", "", "Arquivos Excel (*.xlsx)"
        )
        if arquivo:
            self.caminho_arquivo.setText(arquivo)
            self.caminho_excel_atual = arquivo
            self.atualizar_preview_modelo()

    def atualizar_preview_modelo(self):
        if not self.caminho_excel_atual:
            return

        try:
            import pandas as pd
            df = pd.read_excel(self.caminho_excel_atual)

            # Remove quebras de linha apenas de células que forem texto (evita aplicar str duas vezes)
            df = df.applymap(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)

            # Remove linhas completamente em branco
            df = df.dropna(how='all')

            modelo = self.combo_modelo.currentText()
            config = self.perfis_planilhas.get(modelo, {"skiprows": 0, "colunas": None})

            df = df.iloc[config["skiprows"]:]
            df.columns = df.iloc[0]
            df = df[1:]

            if config["colunas"] is not None:
                colunas = config["colunas"]
                df_selecionado = df.iloc[:, colunas]

            # Caso especial para Planserv Med
                if modelo == "Planserv Med":
                    
                    
                    df = df.reset_index(drop=True)

                    # Seleciona as colunas relevantes por nome
                    df_selecionado = df.iloc[:, [2, 3, 4, 6]].copy()
                    # Substitui ponto por vírgula nas colunas numéricas (original)
                    for col in df_selecionado.columns[3:5]:  # índices 3 e 4
                        df_selecionado[col] = df_selecionado[col].astype(str).str.replace(".", ",", regex=False)

                    # Duplicação da coluna 6 e aplica a conversão
                    col6_duplicada = df.iloc[:, 6].astype(str).str.replace(".", ",", regex=False)
                    df_selecionado["VALOR DUPLICADO"] = col6_duplicada

                    # Adiciona colunas extras
                    df_selecionado["CAMPO NULO"] = ""

                    # Adiciona a coluna de índice 0 (posição após CAMPO NULO)
                    coluna_indice_0 = df.iloc[:, 0].astype(str).fillna("")
                    df_selecionado.insert(len(df_selecionado.columns), df.columns[0], coluna_indice_0)

                    df_selecionado["CAMPO ZERADO 1"] = "0"
                    df_selecionado["CAMPO ZERADO 2"] = "0"

                    df = df_selecionado

                # Reordena e processa colunas para Planserv Mat
            if modelo == "Planserv Mat":
                df = df.reset_index(drop=True)

                # Define os índices conforme pedido
                indices = [7, 8, 12, 12, 1, 2, 3, 0, 9]
                df_selecionado = df.iloc[:, indices].copy()

                # Renomeia a coluna duplicada para evitar conflito
                df_selecionado.columns = [
                    f"{col}_{idx}" if idx != df_selecionado.columns.tolist().index(col) else col
                    for idx, col in enumerate(df_selecionado.columns)
                ]

                # Substitui ponto por vírgula apenas nas duas colunas duplicadas de índice 12
                col_valor1 = df_selecionado.columns[2]
                col_valor2 = df_selecionado.columns[3]
                df_selecionado[col_valor1] = df_selecionado[col_valor1].astype(str).str.replace('.', ',', regex=False)
                df_selecionado[col_valor2] = df_selecionado[col_valor2].astype(str).str.replace('.', ',', regex=False)

                df = df_selecionado

            self.df_processado = df

            preview_df = df.head()

            self.preview_tabela.setRowCount(len(preview_df))
            self.preview_tabela.setColumnCount(len(preview_df.columns))
            self.preview_tabela.setHorizontalHeaderLabels(preview_df.columns.astype(str).tolist())

            for row in range(len(preview_df)):
                for col in range(len(preview_df.columns)):
                    valor = str(preview_df.iat[row, col])
                    self.preview_tabela.setItem(row, col, QTableWidgetItem(valor))

            self.preview_tabela.resizeColumnsToContents()

        except Exception as e:
            self.preview_tabela.setRowCount(0)
            self.preview_tabela.setColumnCount(0)
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar visualização:\n{str(e)}")

    def converter_arquivo(self):
        if not hasattr(self, 'df_processado') or self.df_processado is None:
            QMessageBox.warning(self, "Atenção", "Nenhum dado processado para converter.")
            return

        try:
            from conversor.excel_para_txt import converter_df_para_txt
            # Abre diálogo para salvar o arquivo
            caminho_salvar, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Arquivo TXT",
                "arquivo_convertido.txt",
                "Arquivos de Texto (*.txt)"
            )

            if not caminho_salvar:
                return  # Usuário cancelou

            caminho_txt = converter_df_para_txt(self.df_processado, caminho_salvar)
            QMessageBox.information(self, "Sucesso", f"Arquivo convertido com sucesso:\n{caminho_txt}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao converter o arquivo:\n{str(e)}")