from app.extensions import db
from datetime import datetime
import uuid


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # CORREÇÃO AQUI

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(100), unique=True, default=lambda: str(uuid.uuid4()))

    # Informações básicas
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Perfil
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(200))

    # Permissões e status
    role = db.Column(db.String(20), default='user')  # 'admin', 'user', 'viewer'
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)

    # Empresa associada
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relacionamentos
    company = db.relationship('Company', backref='users')

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'company_id': self.company_id,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def has_permission(self, permission):
        """Verifica se usuário tem permissão específica"""
        permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'user': ['read', 'write'],
            'viewer': ['read']
        }
        return permission in permissions.get(self.role, [])