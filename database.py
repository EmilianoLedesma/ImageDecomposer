### Modulo de base de datos - Operaciones con Supabase
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, validate_config

### Cliente global de Supabase (singleton)
cliente = None


def init_client():
    ### Inicializa y retorna el cliente de Supabase
    global cliente
    if cliente is None:
        validate_config()
        cliente = create_client(SUPABASE_URL, SUPABASE_KEY)
    return cliente


def save_image(width, height, rgb_data):
    ### Guarda los datos de una imagen en Supabase, retorna el ID
    client = init_client()

    data = {
        "width": width,
        "height": height,
        "rgb_data": rgb_data
    }

    response = client.table("images").insert(data).execute()

    if response.data:
        return response.data[0]["id"]
    else:
        raise Exception("Error al guardar la imagen en la base de datos")


def get_image(image_id):
    ### Recupera los datos de una imagen por su ID
    client = init_client()

    response = client.table("images").select("*").eq("id", image_id).execute()

    if response.data:
        return response.data[0]
    else:
        raise Exception(f"No se encontro imagen con ID: {image_id}")
