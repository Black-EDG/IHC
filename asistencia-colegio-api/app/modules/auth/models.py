from sqlalchemy import Column, Integer, String, DateTime, text
from app.core.database import Base

class TokenRevocado(Base):
    """Registro de tokens revocados (logout / refresh)"""
    __tablename__ = "tokens_revocados"

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    usuario_id = Column(Integer, nullable=True)
    tipo_usuario = Column(String(20), nullable=False)  # 'personal' o 'apoderado'
    revocado_en = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    expira_en = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<TokenRevocado {self.token_jti[:20]}... ({self.tipo_usuario})>"