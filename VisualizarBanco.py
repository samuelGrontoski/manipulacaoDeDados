import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql.cursors

class GerenciadorBancoDados:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8',  # Definindo o conjunto de caracteres como utf8
        }
        self.pagina_atual = 0
        self.resultados_por_pagina = 15  # Definindo o número de resultados por página

    def conectar(self):
        self.conexao = pymysql.connect(**self.config)
        self.cursor = self.conexao.cursor()

    def desconectar(self):
        if hasattr(self, 'conexao') and self.conexao.open:
            self.conexao.close()

    def listar_tabelas(self):
        query = "SHOW TABLES"
        self.cursor.execute(query)
        tabelas = [row[0] for row in self.cursor.fetchall()]
        return tabelas

    def listar_colunas(self, tabela):
        query = f"SHOW COLUMNS FROM {tabela}"
        self.cursor.execute(query)
        colunas = [row[0] for row in self.cursor.fetchall()]
        return colunas

    def listar_elementos(self, tabela, pagina, coluna_id):
        offset = pagina * self.resultados_por_pagina
        query = f"SELECT * FROM {tabela} ORDER BY {coluna_id} DESC LIMIT {self.resultados_por_pagina} OFFSET {offset}"
        self.cursor.execute(query)
        resultados = self.cursor.fetchall()
        return resultados

    def total_elementos(self, tabela):
        query = f"SELECT COUNT(*) FROM {tabela}"
        self.cursor.execute(query)
        total = self.cursor.fetchone()[0]
        return total

class Aplicacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta Banco de Dados")

        # Configurações do banco de dados
        self.gerenciador_bd = GerenciadorBancoDados(
            host='10.161.100.11',
            user='bct_write',
            password='bcwriter22',
            database='better_call_test'
        )

        # Criando widgets
        self.label_tabela = tk.Label(root, text="Tabela:")
        self.entry_tabela = ttk.Combobox(root)
        self.entry_tabela.bind("<<ComboboxSelected>>", self.atualizar_colunas)

        self.label_coluna = tk.Label(root, text="Coluna (id):")
        self.entry_coluna = ttk.Combobox(root)

        self.botao_listar = tk.Button(root, text="Listar Elementos", command=self.listar_elementos)
        self.botao_anterior = tk.Button(root, text="Página Anterior", command=self.pagina_anterior)
        self.botao_proxima = tk.Button(root, text="Próxima Página", command=self.proxima_pagina)
        self.lista_resultados = tk.Listbox(root, width=200, height=20, borderwidth=2)

        # Posicionando widgets
        self.label_tabela.grid(row=0, column=0, padx=5, pady=5)
        self.entry_tabela.grid(row=0, column=1, padx=10, pady=5)
        self.label_coluna.grid(row=1, column=0, padx=10, pady=5)
        self.entry_coluna.grid(row=1, column=1, padx=10, pady=5)
        self.botao_listar.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.botao_anterior.grid(row=3, column=0, padx=10, pady=5)
        self.botao_proxima.grid(row=3, column=1, padx=10, pady=5)
        self.lista_resultados.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Inicializar variáveis
        self.pagina_atual = 0

        # Carregar nomes das tabelas no Combobox
        self.carregar_tabelas()

    def carregar_tabelas(self):
        self.gerenciador_bd.conectar()
        tabelas = self.gerenciador_bd.listar_tabelas()
        self.gerenciador_bd.desconectar()
        self.entry_tabela['values'] = tabelas

    def atualizar_colunas(self, event):
        tabela = self.entry_tabela.get()
        if tabela:
            self.gerenciador_bd.conectar()
            colunas = self.gerenciador_bd.listar_colunas(tabela)
            self.gerenciador_bd.desconectar()
            self.entry_coluna['values'] = colunas

    def listar_elementos(self):
        tabela = self.entry_tabela.get()
        coluna_id = self.entry_coluna.get()
        if tabela:
            self.gerenciador_bd.conectar()
            total_elementos = self.gerenciador_bd.total_elementos(tabela)
            if total_elementos == 0:
                self.gerenciador_bd.desconectar()
                messagebox.showinfo("Informação", "Não há elementos nesta tabela.")
                return

            resultados = self.gerenciador_bd.listar_elementos(tabela, self.pagina_atual, coluna_id)
            self.gerenciador_bd.desconectar()

            self.lista_resultados.delete(0, tk.END)
            for resultado in resultados:
                self.lista_resultados.insert(tk.END, resultado)
        else:
            messagebox.showerror("Erro", "Por favor, insira o nome da tabela.")

    def proxima_pagina(self):
        self.pagina_atual += 1
        self.listar_elementos()

    def pagina_anterior(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self.listar_elementos()
        else:
            messagebox.showinfo("Informação", "Você está na primeira página.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()
