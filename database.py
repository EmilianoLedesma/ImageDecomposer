### Modulo de base de datos - Operaciones con Supabase
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, validar_configuracion

### Cliente global de Supabase (singleton)
cliente = None


def iniciar_cliente():
    ### Inicializa y retorna el cliente de Supabase
    global cliente
    if cliente is None:
        validar_configuracion()
        cliente = create_client(SUPABASE_URL, SUPABASE_KEY)
    return cliente


def guardar_imagen(ancho, alto, datos_rgb):
    ### Guarda los datos de una imagen en Supabase, retorna el ID
    cliente_local = iniciar_cliente()

    datos = {
        "width": ancho,
        "height": alto,
        "rgb_data": datos_rgb
    }

    respuesta = cliente_local.table("images").insert(datos).execute()

    if respuesta.data:
        return respuesta.data[0]["id"]
    else:
        raise Exception("Error al guardar la imagen en la base de datos")


def obtener_imagen(id_imagen):
    ### Recupera los datos de una imagen por su ID
    cliente_local = iniciar_cliente()

    respuesta = cliente_local.table("images").select("*").eq("id", id_imagen).execute()

    if respuesta.data:
        return respuesta.data[0]
    else:
        raise Exception(f"No se encontro imagen con ID: {id_imagen}")
