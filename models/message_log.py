# models/message_log.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class MessageLog(Base):
    """
    Modèle SQLAlchemy pour enregistrer les messages WhatsApp entrants,
    leur traitement via GPT, et le statut de l'analyse.

    Ce modèle stocke le contenu original, le résultat structuré éventuel,
    et établit une relation facultative vers le client identifié.
    """
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    sender_number = Column(String, nullable=False, index=True, doc="Numéro WhatsApp de l'expéditeur")
    message_text = Column(Text, nullable=False, doc="Contenu brut du message reçu")
    
    status = Column(String, nullable=False, doc=(
        "Statut de l'analyse : 'commande détectée', 'pas une commande', 'erreur GPT', etc."
    ))
    
    # Client lié, nullable si aucun client reconnu
    client_id = Column(Integer, ForeignKey('clients.id', ondelete="SET NULL"), nullable=True, index=True)
    
    processed_content = Column(Text, nullable=True, doc="Contenu structuré JSON ou texte, résultat de l'analyse GPT")
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), doc="Date/heure d'enregistrement")

    # Relation ORM vers le client (optionnelle)
    client = relationship("Client", backref="message_logs")

    def __repr__(self):
        return f"<MessageLog(id={self.id}, sender_number='{self.sender_number}', status='{self.status}', created_at={self.created_at})>"