# routers/messages.py

import os
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, constr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import openai
from typing import List, Dict

from database import get_async_session
from models import Client, Product, ProcessedOrder, MessageLog

from services.make_order_pdf import generate_order_pdf
from services.send_email import send_order_email

import json
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("La clé OPENAI_API_KEY est requise dans .env")

router = APIRouter(tags=["messages"])

class MessageProcessPayload(BaseModel):
    phone_number: constr(min_length=5)
    message: constr(min_length=1)

def build_prompt(products: List[Product], user_message: str) -> str:
    product_list_str = ", ".join(p.name for p in products)
    prompt = (
        "Tu es un assistant de commande pour une boulangerie.\n"
        f"Les produits disponibles sont : {product_list_str}.\n"
        "Analyse le message du client ci-dessous et dis :\n"
        "- si c'est une commande ou pas,\n"
        "- quels produits sont demandés et en quelle quantité,\n"
        "- pour quelle date de livraison.\n\n"
        f"Message du client : \"{user_message}\"\n\n"
        "Réponds clairement selon ces points en JSON avec les clefs : is_order (bool), "
        "order_details (liste d'objets {product, quantity}), delivery_date (date en ISO ou null).\n"
    )
    return prompt

@router.post("/messages/process")
async def process_message(payload: MessageProcessPayload, request: Request, session: AsyncSession = Depends(get_async_session)):
    phone = payload.phone_number.strip()
    msg = payload.message.strip()

    try:
        query_client = await session.execute(
            select(Client)
            .where(Client.phone_number == phone)
            .options(selectinload(Client.products))
        )
        client: Client = query_client.scalars().first()
        if not client:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Client non trouvé")
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur base de données: {e}")

    products = client.products if client.products else []

    prompt = build_prompt(products, msg)

    try:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": msg}
            ],
            max_tokens=400,
            temperature=0.2,
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur GPT: {e}")

    try:
        response_json = json.loads(answer)
    except Exception:
        m = re.search(r"(\{.*\})", answer, re.DOTALL)
        if not m:
            response_json = {"is_order": False}
        else:
            try:
                response_json = json.loads(m.group(1))
            except Exception:
                response_json = {"is_order": False}

    is_order = response_json.get("is_order", False)
    order_details = response_json.get("order_details", [])
    delivery_date = response_json.get("delivery_date", None)

    if is_order:
        try:
            new_order = ProcessedOrder(
                client_id=client.id,
                products_ordered=json.dumps(order_details, ensure_ascii=False),
                delivery_date=delivery_date,
                original_message=msg,
            )
            session.add(new_order)
            await session.flush()  # pour récupérer l'ID

            pdf_path = generate_order_pdf(
                client_name=client.name,
                items=order_details,
                delivery_date=delivery_date or "",
                order_id=new_order.id
            )

            if not client.email:
                raise HTTPException(status_code=500, detail="Email du client non défini.")

            send_order_email(
                to_email=client.email,
                pdf_path=pdf_path,
                client_name=client.name,
                delivery_date=delivery_date or ""
            )

            new_log = MessageLog(
                client_id=client.id,
                phone_number=phone,
                message=msg,
                is_order=True,
                ai_response=answer,
                processed_order=new_order
            )
            session.add(new_log)
            await session.commit()

            return {"status": "commande enregistrée"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Erreur traitement commande : {e}")


    else:
        try:
            new_log = MessageLog(
                client_id=client.id,
                phone_number=phone,
                message=msg,
                is_order=False,
                ai_response=answer,
            )
            session.add(new_log)
            await session.commit()
        except Exception:
            await session.rollback()
        return {"status": "pas une commande"}
