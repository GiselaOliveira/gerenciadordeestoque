import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class SistemaEstoque:
    def __init__(self):
        self.conn = sqlite3.connect("estoque.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT UNIQUE,
            quantidade INTEGER,
            preco REAL
        )
        """)

        self.conn.commit()

        self.janela = Tk()
        self.janela.title("Sistema de Estoque")
        self.janela.geometry("700x500")

        # Título
        titulo = Label(
            self.janela,
            text="Sistema de Gestão de Estoque",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Frame dos campos
        frame = Frame(self.janela)
        frame.pack(pady=10)

        Label(frame, text="Produto:").grid(row=0, column=0)
        self.entry_produto = Entry(frame, width=25)
        self.entry_produto.grid(row=0, column=1, padx=5)

        Label(frame, text="Quantidade:").grid(row=0, column=2)
        self.entry_quantidade = Entry(frame, width=10)
        self.entry_quantidade.grid(row=0, column=3, padx=5)

        Label(frame, text="Preço:").grid(row=0, column=4)
        self.entry_preco = Entry(frame, width=10)
        self.entry_preco.grid(row=0, column=5, padx=5)

        # Botões
        frame_botoes = Frame(self.janela)
        frame_botoes.pack(pady=10)

        Button(
            frame_botoes,
            text="Adicionar",
            width=15,
            command=self.adicionar_produto
        ).grid(row=0, column=0, padx=5)

        Button(
            frame_botoes,
            text="Remover",
            width=15,
            command=self.remover_produto
        ).grid(row=0, column=1, padx=5)

        Button(
            frame_botoes,
            text="Atualizar Tabela",
            width=15,
            command=self.listar_produtos
        ).grid(row=0, column=2, padx=5)

        # Tabela
        self.tabela = ttk.Treeview(
            self.janela,
            columns=("produto", "quantidade", "preco"),
            show="headings",
            height=15
        )

        self.tabela.heading("produto", text="Produto")
        self.tabela.heading("quantidade", text="Quantidade")
        self.tabela.heading("preco", text="Preço")

        self.tabela.column("produto", width=250)
        self.tabela.column("quantidade", width=100)
        self.tabela.column("preco", width=100)

        self.tabela.pack(pady=10)

        self.listar_produtos()

        self.janela.mainloop()

    def formatar(self, produto):
        return produto.strip().lower()

    def limpar_campos(self):
        self.entry_produto.delete(0, END)
        self.entry_quantidade.delete(0, END)
        self.entry_preco.delete(0, END)

    def adicionar_produto(self):
        produto = self.formatar(self.entry_produto.get())

        try:
            quantidade = int(self.entry_quantidade.get())
            preco = float(self.entry_preco.get().replace(",", "."))

        except ValueError:
            messagebox.showerror(
                "Erro",
                "Digite valores válidos."
            )
            return

        if not produto:
            messagebox.showerror(
                "Erro",
                "Digite o nome do produto."
            )
            return

        self.cursor.execute(
            "SELECT quantidade FROM estoque WHERE produto = ?",
            (produto,)
        )

        resultado = self.cursor.fetchone()

        if resultado:
            nova_quantidade = resultado[0] + quantidade

            self.cursor.execute("""
            UPDATE estoque
            SET quantidade = ?, preco = ?
            WHERE produto = ?
            """, (nova_quantidade, preco, produto))

            messagebox.showinfo(
                "Sucesso",
                "Estoque atualizado."
            )

        else:
            self.cursor.execute("""
            INSERT INTO estoque (produto, quantidade, preco)
            VALUES (?, ?, ?)
            """, (produto, quantidade, preco))

            messagebox.showinfo(
                "Sucesso",
                "Produto adicionado."
            )

        self.conn.commit()

        self.listar_produtos()
        self.limpar_campos()

    def remover_produto(self):
        item = self.tabela.selection()

        if not item:
            messagebox.showwarning(
                "Aviso",
                "Selecione um produto na tabela."
            )
            return

        try:
            quantidade_remover = int(self.entry_quantidade.get())

        except ValueError:
            messagebox.showerror(
                "Erro",
                "Digite uma quantidade válida."
            )
            return

        produto = self.tabela.item(item, "values")[0].lower()

        self.cursor.execute(
            "SELECT quantidade FROM estoque WHERE produto = ?",
            (produto,)
        )

        resultado = self.cursor.fetchone()

        if not resultado:
            messagebox.showerror(
                "Erro",
                "Produto não encontrado."
            )
            return

        estoque_atual = resultado[0]

        if quantidade_remover > estoque_atual:
            messagebox.showwarning(
                "Aviso",
                f"Estoque insuficiente. Disponível: {estoque_atual}"
            )
            return

        nova_quantidade = estoque_atual - quantidade_remover

        if nova_quantidade == 0:
            self.cursor.execute(
                "DELETE FROM estoque WHERE produto = ?",
                (produto,)
            )

        else:
            self.cursor.execute("""
            UPDATE estoque
            SET quantidade = ?
            WHERE produto = ?
            """, (nova_quantidade, produto))

        self.conn.commit()

        self.listar_produtos()
        self.limpar_campos()

        messagebox.showinfo(
            "Sucesso",
            "Estoque atualizado."
        )

    def listar_produtos(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.cursor.execute("""
        SELECT produto, quantidade, preco
        FROM estoque
        ORDER BY produto
        """)

        produtos = self.cursor.fetchall()

        for produto, quantidade, preco in produtos:
            self.tabela.insert(
                "",
                END,
                values=(
                    produto.title(),
                    quantidade,
                    f"R${preco:.2f}"
                )
            )


SistemaEstoque()
