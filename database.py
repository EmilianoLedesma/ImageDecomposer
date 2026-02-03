"""
Módulo de base de datos - Operaciones con Supabase
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, validate_config

# Cliente global de Supabase
_client: Client = None


def init_client() -> Client:
    """
    Inicializa y retorna el cliente de Supabase.
    Usa un singleton para evitar múltiples conexiones.
    """
    global _client
    if _client is None:
        validate_config()
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def save_image(width: int, height: int, rgb_data: str) -> int:
    """
    Guarda los datos de una imagen en Supabase.

    Args:
        width: Ancho de la imagen en píxeles
        height: Alto de la imagen en píxeles
        rgb_data: String con valores RGB separados por coma

    Returns:
        ID del registro creado
    """
    client = init_client()

    data = {
        "width": width,
        "height": height,
        "rgb_data": rgb_data
    }

    response = client.table("images").insert(data).execute()

    if response.data and len(response.data) > 0:
        return response.data[0]["id"]
    else:
        raise Exception("Error al guardar la imagen en la base de datos")


def get_image(image_id: int) -> dict:
    """
    Recupera los datos de una imagen por su ID.

    Args:
        image_id: ID de la imagen a recuperar

    Returns:
        Diccionario con width, height, rgb_data y created_at
    """
    client = init_client()

    response = client.table("images").select("*").eq("id", image_id).execute()

    if response.data and len(response.data) > 0:
        return response.data[0]
    else:
        raise Exception(f"No se encontró imagen con ID: {image_id}")
