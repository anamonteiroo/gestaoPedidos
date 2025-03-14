from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy #ORM
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
import uuid
from flask_cors import CORS 

# Configuração inicial do pacote Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurações para as respostas em JSON exibirem caracteres especiais
app.json.ensure_ascii = False
app.json.mimetype = "application/json; charset=utf-8"

# Criação de Banco de Dados SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pedidos.db"

db = SQLAlchemy(app)

# Model do pedido
class Pedido(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    cliente = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    data_criacao = db.Column(db.DateTime(timezone=True), default=func.now())
    descricao = db.Column(db.String(50), nullable=False)

    # Função de Data Transfer Object (DTO) para transformar o resultado da query em JSON
    def to_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente,
            "valor": self.valor,
            "data_criacao": self.data_criacao,
            "descricao": self.descricao
        }

# Criação do contexto e do DB    
with app.app_context():
    db.create_all()

# Criação de Rotas
# Rota Base
@app.route("/")
def home():
    return jsonify({"message": "Hello World"})

# Rota POST para criação de pedido
@app.route("/pedidos",methods=["POST"])
def add_pedido():

    data = request.get_json()

    novo_pedido = Pedido(
        cliente = data["cliente"],
        valor = data["valor"],
        descricao = data["descricao"]
    )

    db.session.add(novo_pedido)
    db.session.commit()
    return (novo_pedido.to_dict(), 201)

# Rota GET para todos os pedidos
@app.route("/pedidos",methods=["GET"])
def get_pedidos():

    pedidos = Pedido.query.all()

    if pedidos != []:
        lista_pedidos = []

        # Loop para pegar pedido a pedido e adicionar dentro da lista de resposta
        for pedido in pedidos:
            lista_pedidos.append(pedido.to_dict())

        return jsonify(lista_pedidos)
    
    # Tratamento para envio de lista vazia caso não encontre pedido
    else:
        return jsonify(pedidos)

# Rota GET para pedido específico
@app.route("/pedidos/<uuid:id>",methods=["GET"])
def get_pedido(id):

    pedido = Pedido.query.get(id)

    if pedido:
        return jsonify(pedido.to_dict())
    else:
        return jsonify({"erro": "Pedido não encontrado!"}), 404

# Rota PUT para pedido específico    
@app.route("/pedidos/<uuid:id>",methods=["PUT"])
def update_pedido(id):

    data = request.get_json()
    pedido = Pedido.query.get(id)
    
    if pedido:
        pedido.cliente = data.get("cliente", pedido.cliente)
        pedido.valor = data.get("valor", pedido.valor)
        pedido.descricao = data.get("descricao", pedido.descricao)

        db.session.commit()

        return jsonify(pedido.to_dict())
    else:
        return jsonify({"erro": "Pedido não encontrado!"}), 404

# Rota DELETE para pedido específico    
@app.route("/pedidos/<uuid:id>",methods=["DELETE"])
def delete_pedido(id):

    pedido = Pedido.query.get(id)
    if pedido:
        db.session.delete(pedido)
        db.session.commit()
        
        return jsonify({"mensagem": "Pedido deletado"}), 200 #testar com 204
    else:
        return jsonify({"erro": "Pedido não encontrado!"}), 404

# Rota GET para busca do indicador
@app.route("/indicador",methods=["GET"])
def indicador():

    # Querys para busca da quantidade de pedidos e da quantidade de clientes
    qtd_pedidos = db.session.execute(text("SELECT count() as pedidos FROM pedido;")).fetchone()
    qtd_clientes = db.session.execute(text("SELECT count(DISTINCT(cliente)) as clientes FROM pedido;")).fetchone()

    # Retorno fazendo a divisão de pedidos por clientes, o que gera a média de pedidos por cliente
    return jsonify({"indicador": (qtd_pedidos.pedidos/qtd_clientes.clientes)})

# Inicialização da API permitindo debug
if __name__ == "__main__":
    app.run(debug=True)