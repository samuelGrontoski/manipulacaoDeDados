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
        self.root['bg'] = '#d9d9d9'

        largura_tela = root.winfo_screenwidth() - 100
        altura_tela = root.winfo_screenheight() - 100
        root.geometry(f"{largura_tela}x{altura_tela}+0+0")
        root.state('zoomed')

        # Configurações do banco de dados
        self.gerenciador_bd = GerenciadorBancoDados(
            host='10.161.100.11',
            user='bct_write',
            password='bcwriter22',
            database='better_call_test'
        )

        # Criando widgets
        self.label_tabela = tk.Label(
            root,
            text="Tabela:"
        )
        self.entry_tabela = ttk.Combobox(root)
        self.entry_tabela.bind(
            "<<ComboboxSelected>>",
            self.atualizar_colunas
        )
        self.entry_tabela.bind(
            "<KeyRelease>",
            self.filtrar_tabelas
        )

        self.label_coluna = tk.Label(
            root,
            text="Coluna (id):"
        )
        self.entry_coluna = ttk.Combobox(root)
        self.entry_coluna.bind(
            "<KeyRelease>",
            self.filtrar_colunas
        )

        self.botao_listar = tk.Button(
            root,
            text="Listar Elementos",
            command=self.listar_elementos
        )

        # Carregar imagem
        seta_esquerda_img = Image.open('./assets/seta_esquerda.png')
        seta_esquerda_img = seta_esquerda_img.resize((10, 10), Image.ANTIALIAS)
        # Converter para incluir canal alfa
        seta_esquerda_img = seta_esquerda_img.convert("RGBA")
        # Adicionar fundo
        bg_color = (217, 217, 217)  # Cor #d9d9d9 em RGB
        seta_esquerda_img_with_bg = Image.new('RGBA', seta_esquerda_img.size, bg_color)
        seta_esquerda_img_with_bg.paste(seta_esquerda_img, (0, 0), seta_esquerda_img)
        self.seta_esquerda_photo = ImageTk.PhotoImage(seta_esquerda_img_with_bg)

        self.botao_anterior = tk.Button(
            root,
            text="",
            command=self.pagina_anterior,
            image=self.seta_esquerda_photo,
            compound=tk.LEFT
        )

        # Carregar imagem
        seta_direita_img = Image.open('./assets/seta_direita.png')
        seta_direita_img = seta_direita_img.resize((10, 10), Image.ANTIALIAS)
        # Converter para incluir canal alfa
        seta_direita_img = seta_direita_img.convert("RGBA")
        # Adicionar fundo
        bg_color = (217, 217, 217)  # Cor #d9d9d9 em RGB
        seta_direita_img_with_bg = Image.new('RGBA', seta_direita_img.size, bg_color)
        seta_direita_img_with_bg.paste(seta_direita_img, (0, 0), seta_direita_img)
        self.seta_direita_photo = ImageTk.PhotoImage(seta_direita_img_with_bg)

        self.botao_proxima = tk.Button(
            root,
            text="",
            command=self.proxima_pagina,
            image=self.seta_direita_photo,
            compound=tk.LEFT
        )

        self.criadores = tk.Label(
            root,
            text="Desenvolvido por Marcos Tullio Silva de Souza e Samuel Grontoski"
        )

        # Criando Treeview
        self.tree_resultados = ttk.Treeview(
            root,
            show='headings'
        )
        self.scrollbar_y = ttk.Scrollbar(
            root,
            orient='vertical',
            command=self.tree_resultados.yview
        )
        self.scrollbar_x = ttk.Scrollbar(
            root, orient='horizontal',
            command=self.tree_resultados.xview
        )
        self.tree_resultados.configure(
            yscroll=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )
        self.frame_treeview = tk.Frame(root)
        self.frame_treeview.place(x=20, y=150)

        # Posicionando widgets
        self.label_tabela.grid(row=0, column=0, padx=30, pady=5, sticky='w')
        self.entry_tabela.grid(row=0, column=1, padx=30, pady=5, sticky='w')

        self.label_coluna.grid(row=1, column=0, padx=30, pady=5, sticky='w')
        self.entry_coluna.grid(row=1, column=1, padx=30, pady=5, sticky='w')

        self.botao_listar.grid(row=2, column=0, columnspan=2, padx=30, pady=5, sticky='ew')
        self.botao_anterior.place(x=600, y=560)
        self.botao_proxima.place(x=640, y=560)

        self.criadores.place(x=30, y=660)

        self.tree_resultados.place(x=30, y=150, height=400, width=1200)
        self.scrollbar_y.place(x=0 + self.tree_resultados.winfo_reqwidth(), y=150, height=400)
        self.scrollbar_x.place(x=30, y=560, width=400)

        # Estilos widgets
        self.label_tabela.config(font=("Helvetica", 10, "bold"), background='#d9d9d9')
        self.label_coluna.config(font=("Helvetica", 10, "bold"), background='#d9d9d9')
        self.entry_tabela.config(width=40)
        self.entry_coluna.config(width=40)
        self.botao_listar.config(bg="#1B2451", fg="#d9d9d9", font=("Helvetica", 10, "bold"), borderwidth=0, cursor="hand2")
        self.botao_anterior.config(cursor="hand2", borderwidth=0, background='#d9d9d9')
        self.botao_proxima.config(cursor="hand2", borderwidth=0, background='#d9d9d9')
        self.criadores.config(font=("Helvetica", 10, "bold"), background='#d9d9d9')

        # Inicializar variáveis
        self.pagina_atual = 0

        # Armazenar todas as tabelas e colunas para filtragem
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
        if tabela:
            self.gerenciador_bd.conectar()
            total_elementos = self.gerenciador_bd.total_elementos(tabela)
            if total_elementos == 0:
                self.gerenciador_bd.desconectar()
                messagebox.showinfo("Aviso", "Não há elementos nesta tabela.")
                return

            resultados = self.gerenciador_bd.listar_elementos(tabela, self.pagina_atual, coluna_id)
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
