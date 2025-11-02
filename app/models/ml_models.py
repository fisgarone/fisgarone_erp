# app/models/ml_models.py - VERSÃO REVISADA E COM ADIÇÕES
from app.extensions import db
from datetime import datetime


class VendaML(db.Model):
    """Modelo para vendas do Mercado Livre"""
    __tablename__ = 'vendas_ml'
    __table_args__ = {'extend_existing': True}

    # ID Principal
    id_pedido = db.Column(db.String(100), primary_key=True)

    # Dados da Venda
    preco_unitario = db.Column(db.Numeric(10, 2), default=0)
    quantidade = db.Column(db.Integer, default=0)
    data_venda = db.Column(db.String(20))

    # Custos Brutos e Taxas da API
    taxa_mercado_livre = db.Column(db.Numeric(10, 2), default=0)  # Custo bruto unitário da API (sale_fee)

    # Custos Calculados (Lógica Revisada)
    taxa_fixa_ml = db.Column(db.Numeric(10, 2), default=0)
    comissoes = db.Column(db.Numeric(10, 2), default=0)
    comissao_percent = db.Column(db.Numeric(5, 2), default=0)
    frete_seller = db.Column(db.Numeric(10, 2), default=0)

    # Detalhamento de Fretes (Mantido)
    frete = db.Column(db.Numeric(10, 2), default=0)
    custo_frete_base = db.Column(db.Numeric(10, 2), default=0)
    custo_frete_opcional = db.Column(db.Numeric(10, 2), default=0)
    custo_pedido_frete = db.Column(db.Numeric(10, 2), default=0)
    custo_lista_frete = db.Column(db.Numeric(10, 2), default=0)
    custo_total_frete = db.Column(db.Numeric(10, 2), default=0)
    frete_comprador = db.Column(db.Numeric(10, 2), default=0)

    # Dados do Item e Comprador
    titulo = db.Column(db.String(500))
    mlb = db.Column(db.String(100))
    sku = db.Column(db.String(100))
    codigo_envio = db.Column(db.String(100))
    comprador = db.Column(db.String(100))

    # Dados de Logística e Status
    modo_envio = db.Column(db.String(100))
    tipo_logistica = db.Column(db.String(50))
    pago_por = db.Column(db.String(20), default='seller')
    situacao = db.Column(db.String(50))
    situacao_entrega = db.Column(db.String(50))
    cancelamentos = db.Column(db.String(20))
    data_liberacao = db.Column(db.String(20))

    # Custos Adicionais e Análises Financeiras
    preco_custo_ml = db.Column(db.Numeric(10, 2), default=0)
    custo_total_calculado = db.Column(db.Numeric(10, 2), default=0)  # Coluna antiga, pode ser reavaliada
    aliquota_percent = db.Column(db.Numeric(5, 2), default=0)
    imposto_rs = db.Column(db.Numeric(10, 2), default=0)

    # Colunas de Custo e Margem (Mantidas e Novas)
    custo_operacional = db.Column(db.Numeric(10, 2), default=0)  # Coluna antiga, pode ser reavaliada
    total_custo_operacional = db.Column(db.Numeric(10, 2), default=0)  # Coluna antiga, pode ser reavaliada
    mc_total = db.Column(db.Numeric(10, 2), default=0)  # Coluna antiga, pode ser reavaliada
    custo_fixo = db.Column(db.Numeric(10, 2), default=0)
    lucro_real = db.Column(db.Numeric(10, 2), default=0)
    lucro_real_percent = db.Column(db.Numeric(5, 2), default=0)

    # >>> NOVAS COLUNAS ADICIONADAS CONFORME O PLANO <<<
    custo_operacional_ml = db.Column(db.Numeric(10, 2), default=0,
                                     comment="Custo total da venda no canal ML (Comissão + Taxa Fixa + Frete)")
    mc_ml = db.Column(db.Numeric(10, 2), default=0,
                      comment="Margem de Contribuição da venda (Receita - Custo Canal - Custo Produto)")

    # Metadados
    conta = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id_pedido': self.id_pedido,
            'preco_unitario': float(self.preco_unitario) if self.preco_unitario else 0,
            'quantidade': self.quantidade,
            'data_venda': self.data_venda,
            'conta': self.conta,
            'titulo': self.titulo,
            'mlb': self.mlb,
            'sku': self.sku,
            'situacao': self.situacao,
            'lucro_real': float(self.lucro_real) if self.lucro_real else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RepasseML(db.Model):
    __tablename__ = 'repasses_ml'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.String(100))
    preco_unitario = db.Column(db.Numeric(10, 2), default=0)
    data_venda = db.Column(db.String(20))
    quantidade = db.Column(db.Integer, default=0)
    tipo_logistica = db.Column(db.String(50))
    situacao = db.Column(db.String(50))
    taxa_fixa_ml = db.Column(db.Numeric(10, 2), default=0)
    comissoes = db.Column(db.Numeric(10, 2), default=0)
    frete_seller = db.Column(db.Numeric(10, 2), default=0)
    data_liberacao = db.Column(db.String(20))
    data_repasse = db.Column(db.String(20))
    total_venda = db.Column(db.Numeric(10, 2), default=0)
    total_custo = db.Column(db.Numeric(10, 2), default=0)
    valor_repasse = db.Column(db.Numeric(10, 2), default=0)
    conta = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustoML(db.Model):
    __tablename__ = 'custos_ml'
    __table_args__ = {'extend_existing': True}

    mlb = db.Column(db.String(100), primary_key=True)
    custo = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

