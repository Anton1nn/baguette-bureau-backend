import httpx

VENOM_BOT_URL = "http://localhost:3000"
WHATSAPP_API_URL = "http://localhost:3002"


class VenomBotServiceError(Exception):
    """Exception personnalisée pour les erreurs du service Venom Bot."""
    pass


# ------------------- SESSION INIT -------------------

async def create_venom_session(client_id: str):
    """Crée une session Venom Bot pour le client donné."""
    url = f"{VENOM_BOT_URL}/session/create/{client_id}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur création session Venom ({client_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau : {str(e)}")


async def create_whatsapp_session(user_id: int) -> None:
    """Crée une session WhatsApp via l’API secondaire (port 3002)."""
    url = f"{WHATSAPP_API_URL}/start"
    payload = {"session": str(user_id)}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur création session WhatsApp ({user_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau WhatsApp : {str(e)}")


# ------------------- QR CODE -------------------

async def get_qr_code(client_id: str) -> str:
    """Récupère le QR Code (base64) pour une session Venom (port 3000)."""
    url = f"{VENOM_BOT_URL}/session/qrcode/{client_id}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            if "qr" not in data:
                raise VenomBotServiceError(f"QR code absent : {data}")
            return data["qr"]
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur récupération QR Venom ({client_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau QR Venom : {str(e)}")


async def get_qr_code_from_secondary(session_id: int) -> str:
    """Récupère le QR Code pour une session via l’API secondaire (port 3002)."""
    url = f"{WHATSAPP_API_URL}/qrcode/{session_id}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            return data["qr"]
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur QR secondaire ({session_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau QR secondaire : {str(e)}")


# ------------------- SESSION STATUS -------------------

async def check_session_status(client_id: str) -> str:
    """Vérifie si la session est authentifiée via Venom (port 3000)."""
    url = f"{VENOM_BOT_URL}/session/status/{client_id}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            if "status" not in data:
                raise VenomBotServiceError(f"Statut absent : {data}")
            return data["status"]
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur statut Venom ({client_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau statut Venom : {str(e)}")


async def get_whatsapp_status(session_id: int) -> str:
    """Récupère le statut de la session WhatsApp via API secondaire (3002)."""
    url = f"{WHATSAPP_API_URL}/status/{session_id}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            return data["status"]
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur statut WhatsApp ({session_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau statut WhatsApp : {str(e)}")


# ------------------- MESSAGE -------------------

async def send_message(client_id: str, phone_number: str, message: str):
    """Envoie un message à un numéro donné via la session Venom."""
    url = f"{VENOM_BOT_URL}/session/send/{client_id}"
    payload = {
        "to": phone_number,
        "message": message
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise VenomBotServiceError(f"Erreur envoi message Venom ({client_id}) : {e.response.text}")
        except Exception as e:
            raise VenomBotServiceError(f"Erreur réseau message Venom : {str(e)}")
