# models/processed_order.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from database import Base

class ProcessedOrder(Base):
    """
    Modèle SQLAlchemy pour archiver les commandes WhatsApp traitées par GPT.
    Permet le suivi, la recherche et la gestion des PDF de commandes envoyées.
    """
    __tablename__ = "processed_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Clé étrangère vers Client, ondelete="SET NULL" => le client peut être supprimé, la commande reste archivée !
    client_id = Column(Integer, ForeignKey('clients.id', ondelete="SET NULL"), nullable=True, index=True)
    # Clé étrangère vers User (le boulanger), même principe d'archivage
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True, index=True)

    delivery_date = Column(DateTime(timezone=True), nullable=False, doc="Date de livraison demandée")
    items = Column(Text, nullable=False, doc="Représentation JSON ou texte des produits commandés")
    pdf_path = Column(String, nullable=True, doc="Chemin ou URL du PDF généré pour cette commande")
    status = Column(String, nullable=False, default="envoyé", doc="Statut de l'archive ('envoyé', 'erreur', 'en attente')")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), doc="Date de création de l'archive")

    # Relations ORM (optionnelles, utiles pour joints ou navigation)
    client = relationship("Client", backref="processed_orders")
    owner = relationship("User", backref="processed_orders")

    def __repr__(self):
        return (
            f"<ProcessedOrder(id={self.id}, client_id={self.client_id}, owner_id={self.owner_id}, "
            f"delivery_date={self.delivery_date}, status='{self.status}')>"
        )