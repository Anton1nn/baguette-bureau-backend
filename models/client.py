# models/client.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Client(Base):
    """
    Modèle SQLAlchemy représentant un client professionnel (restaurant, hôtel, école...) 
    enregistré par un utilisateur (boulanger).
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)   # nom du client, obligatoire
    email = Column(String, nullable=True)               # email du client, optionnel
    phone = Column(String, nullable=True)               # téléphone du client, optionnel
    address = Column(String, nullable=True)             # adresse du client, optionnelle
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relation ORM avec le propriétaire (boulanger)
    owner = relationship("User", backref="clients")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"