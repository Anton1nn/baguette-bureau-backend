# models/order.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class OrderStatusEnum(str, enum.Enum):
    en_attente = "en_attente"
    en_cours = "en_cours"
    livre = "livré"
    annule = "annulé"

class Order(Base):
    """
    Modèle SQLAlchemy représentant une commande passée par un client professionnel.
    La commande est liée à un client et à l'utilisateur propriétaire (boulanger).
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False, doc="Contenu de la commande (désignation, quantités, etc.)")
    delivery_date = Column(DateTime(timezone=True), nullable=False, doc="Date et heure prévue de livraison")
    status = Column(String, nullable=False, default=OrderStatusEnum.en_attente, doc="Statut de la commande")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), doc="Date de création automatique")

    # ForeignKey vers Client et User
    client_id = Column(Integer, ForeignKey('clients.id', ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)

    # Relations ORM
    client = relationship("Client", backref="orders")
    owner = relationship("User", backref="orders")

    def __repr__(self):
        return (
            f"<Order(id={self.id}, client_id={self.client_id}, "
            f"owner_id={self.owner_id}, status='{self.status}', delivery_date={self.delivery_date})>"
        )