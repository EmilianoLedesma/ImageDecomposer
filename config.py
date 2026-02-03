"""
Configuración del proyecto - Carga variables de entorno para Supabase
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Credenciales de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validar que las credenciales estén configuradas
def validate_config():
    """Verifica que las credenciales de Supabase estén configuradas."""
    if not SUPABASE_URL or SUPABASE_URL == "tu_url_aqui":
        raise ValueError("SUPABASE_URL no está configurado en el archivo .env")
    if not SUPABASE_KEY or SUPABASE_KEY == "tu_anon_key_aqui":
        raise ValueError("SUPABASE_KEY no está configurado en el archivo .env")
    return True
