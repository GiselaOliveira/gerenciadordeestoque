import sqlite3


class GestaoEstoque:
    def __init__(self, banco):
        self.conn = sqlite3.connect(banco)
        self.criar_tabela()

    # Cria a tabela do estoque
    def criar_tabela(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT UNIQUE NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL
            )
        """)

        self.conn.commit()

    # Padroniza o nome do produto
    def formatar_produto(self, produto):
        return produto.strip().lower()

    # Adiciona produto ao estoque
    def adicionar_produto(self, produto, quantidade, preco):
        produto = self.formatar_produto(produto)

        # Validações
        if not produto:
            print("Nome do produto inválido.")
            return

        if quantidade <= 0:
            print("A quantidade deve ser maior que zero.")
            return

        if preco <= 0:
            print("O preço deve ser maior que zero.")
            return

        try:
            cursor = self.conn.cursor()

            # Verifica se o produto já existe
            cursor.execute("""
                SELECT quantidade
                FROM estoque
                WHERE produto = ?
            """, (produto,))

            resultado = cursor.fetchone()

            # Produto já existe
            if resultado:
                estoque_atual = resultado[0]

                print(
                    f"O produto '{produto.title()}' já existe."
                )

                print(
                    f"Quantidade atual em estoque: {estoque_atual}"
                )

                adicionar_mais = input(
                    "Deseja adicionar mais unidades? (s/n): "
                ).strip().lower()

                if adicionar_mais == "s":
                    nova_quantidade = estoque_atual + quantidade

                    cursor.execute("""
                        UPDATE estoque
                        SET quantidade = ?, preco = ?
                        WHERE produto = ?
                    """, (nova_quantidade, preco, produto))

                    self.conn.commit()

                    print(
                        f"Estoque atualizado para {nova_quantidade} unidade(s)."
                    )

                else:
                    print("Operação cancelada.")

            # Produto novo
            else:
                cursor.execute("""
                    INSERT INTO estoque (produto, quantidade, preco)
                    VALUES (?, ?, ?)
                """, (produto, quantidade, preco))

                self.conn.commit()

                print(
                    f"Produto '{produto.title()}' adicionado com sucesso."
                )

        except sqlite3.Error as erro:
            print(f"Erro no banco de dados: {erro}")

    # Remove produtos do estoque
    def remover_produto(self, produto, quantidade):
        produto = self.formatar_produto(produto)

        if not produto:
            print("Nome do produto inválido.")
            return

        if quantidade <= 0:
            print("A quantidade deve ser maior que zero.")
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT quantidade
                FROM estoque
                WHERE produto = ?
            """, (produto,))

            resultado = cursor.fetchone()

            if resultado is None:
                print("Produto não encontrado.")
                return

            estoque_atual = resultado[0]

            if quantidade > estoque_atual:
                print(
                    f"Estoque insuficiente. Disponível: {estoque_atual}"
                )
                return

            nova_quantidade = estoque_atual - quantidade

            # Remove produto se zerar estoque
            if nova_quantidade == 0:
                cursor.execute("""
                    DELETE FROM estoque
                    WHERE produto = ?
                """, (produto,))

                print(
                    f"Produto '{produto.title()}' removido do estoque."
                )

            else:
                cursor.execute("""
                    UPDATE estoque
                    SET quantidade = ?
                    WHERE produto = ?
                """, (nova_quantidade, produto))

                print(
                    f"{quantidade} unidade(s) removida(s)."
                )

            self.conn.commit()

        except sqlite3.Error as erro:
            print(f"Erro no banco de dados: {erro}")

    # Consulta um produto específico
    def consultar_estoque(self, produto):
        produto = self.formatar_produto(produto)

        if not produto:
            print("Nome do produto inválido.")
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT quantidade, preco
                FROM estoque
                WHERE produto = ?
            """, (produto,))

            resultado = cursor.fetchone()

            if resultado:
                quantidade, preco = resultado

                print(f"""
Produto: {produto.title()}
Quantidade: {quantidade}
Preço: R${preco:.2f}
""")

            else:
                print("Produto não encontrado.")

        except sqlite3.Error as erro:
            print(f"Erro no banco de dados: {erro}")

    # Lista todos os produtos
    def listar_produtos(self):
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT produto, quantidade, preco
                FROM estoque
                ORDER BY produto
            """)

            produtos = cursor.fetchall()

            if not produtos:
                print("Nenhum produto cadastrado.")
                return

            print("\n=== Produtos em Estoque ===")

            for produto, quantidade, preco in produtos:
                print(
                    f"- {produto.title()} | "
                    f"Quantidade: {quantidade} | "
                    f"Preço: R${preco:.2f}"
                )

        except sqlite3.Error as erro:
            print(f"Erro no banco de dados: {erro}")

    # Fecha conexão com o banco
    def fechar_conexao(self):
        self.conn.close()


# Lê números inteiros válidos
def ler_inteiro(mensagem):
    while True:
        try:
            valor = int(input(mensagem))

            if valor <= 0:
                print("Digite um valor maior que zero.")
                continue

            return valor

        except ValueError:
            print("Digite um número inteiro válido.")


# Lê números decimais válidos
def ler_float(mensagem):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))

            if valor <= 0:
                print("Digite um valor maior que zero.")
                continue

            return valor

        except ValueError:
            print("Digite um número válido.")


def main():
    sistema = GestaoEstoque("estoque.db")

    while True:
        print("""
=== Sistema de Gestão de Estoque ===

1 - Adicionar produto
2 - Remover produto
3 - Consultar produto
4 - Listar produtos
5 - Sair
""")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            produto = input("Nome do produto: ")

            quantidade = ler_inteiro(
                "Quantidade: "
            )

            preco = ler_float(
                "Preço: R$ "
            )

            sistema.adicionar_produto(
                produto,
                quantidade,
                preco
            )

        elif escolha == "2":
            produto = input("Nome do produto: ")

            quantidade = ler_inteiro(
                "Quantidade a remover: "
            )

            sistema.remover_produto(
                produto,
                quantidade
            )

        elif escolha == "3":
            produto = input("Nome do produto: ")

            sistema.consultar_estoque(produto)

        elif escolha == "4":
            sistema.listar_produtos()

        elif escolha == "5":
            sistema.fechar_conexao()

            print("Sistema encerrado.")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
