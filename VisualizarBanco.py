import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import pymysql.cursors
import tkinter.font as tkFont

class GerenciadorBancoDados:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8',
        }
        self.pagina_atual = 0
        self.resultados_por_pagina = 19

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

    def listar_elementos(self, tabela, pagina, coluna_id, termo_pesquisa=None):
        offset = pagina * self.resultados_por_pagina
        if termo_pesquisa:
            query = f"SELECT * FROM {tabela} WHERE {coluna_id} LIKE %s ORDER BY {coluna_id} DESC LIMIT {self.resultados_por_pagina} OFFSET {offset}"
            self.cursor.execute(query, ('%' + termo_pesquisa + '%',))
        else:
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
        self.root.geometry("1250x700")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg="#f0f0f0")

        self.gerenciador_bd = GerenciadorBancoDados(
            host='10.161.100.11',
            user='bct_write',
            password='bcwriter22',
            database='better_call_test'
        )

        # Criando widgets
        self.label_tabela = tk.Label(root, text="Tabela: ", bg="#f0f0f0", font=("Helvetica", 12))
        self.entry_tabela = ttk.Combobox(root, width=175)
        self.entry_tabela.bind("<<ComboboxSelected>>", self.atualizar_colunas)
        self.entry_tabela.bind("<KeyRelease>", self.filtrar_tabelas)

        self.label_coluna = tk.Label(root, text="Coluna: ", bg="#f0f0f0", font=("Helvetica", 12))
        self.entry_coluna = ttk.Combobox(root, width=175)
        self.entry_coluna.bind("<KeyRelease>", self.filtrar_colunas)

        self.label_pesquisa = tk.Label(root, text="Pesquisar: ", bg="#f0f0f0", font=("Helvetica", 12))
        self.entry_pesquisa = tk.Entry(root, width=175)

        self.botao_listar = tk.Button(root, text="Listar Elementos", command=self.listar_elementos, bg="#1B2451", fg="#f0f0f0", font=("Helvetica", 10, "bold"), cursor="hand2")
        self.botao_pesquisar = tk.Button(root, text="Pesquisar", command=self.pesquisar_elementos, bg="#1B2451", fg="#f0f0f0", font=("Helvetica", 10, "bold"), cursor="hand2")

        # Carregar imagem das setas
        seta_esquerda_img = Image.open('./assets/seta_esquerda.png').resize((20, 20))
        seta_esquerda_img = ImageTk.PhotoImage(seta_esquerda_img)
        self.botao_anterior = tk.Button(root, image=seta_esquerda_img, command=self.pagina_anterior, bg="#f0f0f0", cursor="hand2", borderwidth=0)
        self.botao_anterior.image = seta_esquerda_img

        seta_direita_img = Image.open('./assets/seta_direita.png').resize((20, 20))
        seta_direita_img = ImageTk.PhotoImage(seta_direita_img)
        self.botao_proxima = tk.Button(root, image=seta_direita_img, command=self.proxima_pagina, bg="#f0f0f0", cursor="hand2", borderwidth=0)
        self.botao_proxima.image = seta_direita_img

        self.criadores = tk.Label(root, text="Desenvolvido por Marcos Tullio Silva de Souza e Samuel Grontoski", bg="#f0f0f0", font=("Helvetica", 10))

        # Criando Treeview
        self.tree_resultados = ttk.Treeview(root, show='headings', height=20)
        self.scrollbar_y = ttk.Scrollbar(root, orient='vertical', command=self.tree_resultados.yview)
        self.scrollbar_x = ttk.Scrollbar(root, orient='horizontal', command=self.tree_resultados.xview)
        self.tree_resultados.configure(yscroll=self.scrollbar_y.set, xscroll=self.scrollbar_x.set)

        # Configurar grid
        for i in range(8):
            root.grid_rowconfigure(i, weight=1)
        for i in range(2):
            root.grid_columnconfigure(i, weight=1)

        # Posicionando widgets
        self.label_tabela.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.entry_tabela.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.label_coluna.grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.entry_coluna.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.label_pesquisa.grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.entry_pesquisa.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.botao_listar.grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        self.botao_pesquisar.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        self.tree_resultados.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.scrollbar_y.grid(row=4, column=2, padx=10, pady=10, sticky='ns')
        self.scrollbar_x.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.botao_anterior.grid(row=6, column=0, padx=10, pady=10, sticky='w')
        self.botao_proxima.grid(row=6, column=1, padx=10, pady=10, sticky='e')
        self.criadores.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Inicializar variáveis
        self.pagina_atual = 0
        self.todas_tabelas = []
        self.todas_colunas = []

        # Carregar nomes das tabelas no Combobox
        self.carregar_tabelas()

    def carregar_tabelas(self):
        self.gerenciador_bd.conectar()
        tabelas = self.gerenciador_bd.listar_tabelas()
        self.gerenciador_bd.desconectar()
        self.todas_tabelas = tabelas
        self.entry_tabela['values'] = tabelas

    def atualizar_colunas(self, event):
        tabela = self.entry_tabela.get()
        if tabela:
            self.gerenciador_bd.conectar()
            colunas = self.gerenciador_bd.listar_colunas(tabela)
            self.gerenciador_bd.desconectar()
            self.todas_colunas = colunas
            self.entry_coluna['values'] = colunas

    def filtrar_tabelas(self, event):
        valor = self.entry_tabela.get().lower()
        if valor == '':
            data = self.todas_tabelas
        else:
            data = [item for item in self.todas_tabelas if valor in item.lower()]
        self.entry_tabela['values'] = data
        self.entry_tabela.event_generate('<Down>')

    def filtrar_colunas(self, event):
        valor = self.entry_coluna.get().lower()
        if valor == '':
            data = self.todas_colunas
        else:
            data = [item for item in self.todas_colunas if valor in item.lower()]
        self.entry_coluna['values'] = data
        self.entry_coluna.event_generate('<Down>')

    def listar_elementos(self):
        tabela = self.entry_tabela.get()
        coluna_id = self.entry_coluna.get()
        termo_pesquisa = self.entry_pesquisa.get()
        if tabela:
            self.gerenciador_bd.conectar()
            total_elementos = self.gerenciador_bd.total_elementos(tabela)
            if total_elementos == 0:
                self.gerenciador_bd.desconectar()
                messagebox.showinfo("Aviso", "Não há elementos nesta tabela.")
                return

            resultados = self.gerenciador_bd.listar_elementos(tabela, self.pagina_atual, coluna_id, termo_pesquisa)
            colunas = self.gerenciador_bd.listar_colunas(tabela)
            self.gerenciador_bd.desconectar()

            self.tree_resultados.delete(*self.tree_resultados.get_children())
            self.tree_resultados["columns"] = colunas
            for col in colunas:
                self.tree_resultados.heading(col, text=col)

            # Ajustar largura das colunas
            font = tkFont.Font()
            for col in colunas:
                max_width = font.measure(col)
                for row in resultados:
                    item_width = font.measure(str(row[colunas.index(col)]))
                    if item_width > max_width:
                        max_width = item_width
                self.tree_resultados.column(col, width=max_width + 5, anchor=tk.CENTER)

            for resultado in resultados:
                self.tree_resultados.insert("", "end", values=resultado)
        else:
            messagebox.showerror("Erro", "Por favor, insira o nome da tabela.")

    def pesquisar_elementos(self):
        self.pagina_atual = 0
        self.listar_elementos()

    def proxima_pagina(self):
        self.pagina_atual += 1
        self.listar_elementos()

    def pagina_anterior(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self.listar_elementos()
        else:
            messagebox.showinfo("Aviso", "Você está na primeira página.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()
