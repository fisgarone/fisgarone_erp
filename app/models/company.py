# app/models/company.py - VERSÃO CORRIGIDA E FINAL
from app.extensions import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia
        }


class CompanyConfig(db.Model):
    __tablename__ = 'company_configs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Configurações gerais
    timezone = db.Column(db.String(50), default='America/Sao_Paulo')
    idioma = db.Column(db.String(10), default='pt_BR')
    moeda = db.Column(db.String(10), default='BRL')

    # Automatizações
    auto_sincronizar_estoque = db.Column(db.Boolean, default=True)
    auto_processar_pedidos = db.Column(db.Boolean, default=True)
    intervalo_sincronizacao = db.Column(db.Integer, default=30)  # minutos

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'timezone': self.timezone,
            'idioma': self.idioma,
            'moeda': self.moeda,
            'auto_sincronizar_estoque': self.auto_sincronizar_estoque,
            'auto_processar_pedidos': self.auto_processar_pedidos,
            'intervalo_sincronizacao': self.intervalo_sincronizacao
        }


class IntegrationConfig(db.Model):
    __tablename__ = 'integration_configs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Mercado Livre
    ml_ativo = db.Column(db.Boolean, default=False)
    ml_app_id = db.Column(db.String(100))
    ml_client_secret = db.Column(db.String(100))
    ml_access_token = db.Column(db.Text)
    ml_refresh_token = db.Column(db.Text)
    ml_token_expires = db.Column(db.DateTime)

    # Shopee
    shopee_ativo = db.Column(db.Boolean, default=False)
    shopee_partner_id = db.Column(db.String(100))
    shopee_secret_key = db.Column(db.String(100))
    shopee_access_token = db.Column(db.Text)
    shopee_refresh_token = db.Column(db.Text)

    # Configurações de sincronização automática
    sincronizar_pedidos_auto = db.Column(db.Boolean, default=True)
    sincronizar_produtos_auto = db.Column(db.Boolean, default=True)
    sincronizar_estoque_auto = db.Column(db.Boolean, default=True)

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'ml_ativo': self.ml_ativo,
            'shopee_ativo': self.shopee_ativo,
            'sincronizar_pedidos_auto': self.sincronizar_pedidos_auto,
            'sincronizar_produtos_auto': self.sincronizar_produtos_auto,
            'sincronizar_estoque_auto': self.sincronizar_estoque_auto
        }

    def tem_integracao_ativa(self):
        return self.ml_ativo or self.shopee_ativo