# utils/gpt_prompt.py

from typing import List

def generate_prompt(client_name: str, product_list: List[str]) -> str:
    """
    Génère un prompt système destiné à ChatGPT pour l'analyse précise des commandes WhatsApp
    d'un client professionnel d'une boulangerie.

    Args:
        client_name (str): Nom du client professionnel.
        product_list (List[str]): Liste des produits personnalisés pour ce client.

    Returns:
        str: Prompt clair et professionnel à fournir à GPT.
    """
    products = ", ".join(f'"{p}"' for p in product_list)

    prompt = (
        f"Tu es un assistant expert dans la prise de commandes pour une boulangerie artisanale. "
        f"Le client professionnel s'appelle « {client_name} ».\n"
        f"Lorsqu'il envoie un message WhatsApp, ton rôle est d'analyser son texte et d'identifier une éventuelle commande "
        f"concernant UNIQUEMENT les produits suivants : {products}.\n"
        "Ignore tout produit ne figurant pas dans cette liste, même s'il en parle.\n"
        "Si tu détectes une commande, extrait de manière structurée :\n"
        "- le ou les produits commandés (uniquement ceux listés plus haut) avec la quantité demandée,\n"
        "- la date de livraison souhaitée si elle est mentionnée (format 'YYYY-MM-DD'),\n"
        "- un indicateur si le message correspond à une commande ou non.\n"
        "Retourne systématiquement ta réponse uniquement sous ce format JSON :\n"
        "{\n"
        "  \"is_order\": true,\n"
        "  \"delivery_date\": \"YYYY-MM-DD\",  // ou null si la date n'est pas précisée\n"
        "  \"items\": [\n"
        "    {\"name\": \"...\", \"quantity\": ...}\n"
        "  ]\n"
        "}\n"
        "Si le message ne correspond pas à une commande, répond simplement avec :\n"
        "{ \"is_order\": false }\n"
        "Respecte ce format à la lettre sans ajouter aucun commentaire ni explication."
    )
    return prompt