# models/product.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    """
    Modèle SQLAlchemy représentant un produit spécifique disponible pour un client professionnel.
    Un produit est lié à un client, et sera supprimé automatiquement si le client est supprimé.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True, doc="Nom du produit (ex: baguette, croissant, etc.)")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), doc="Date de création automatique")
    
    # Foreign key vers le client, suppression en cascade
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)

    # Relation ORM avec le modèle Client
    client = relationship("Client", backref="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', client_id={self.client_id})>"