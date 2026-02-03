### Configuracion del proyecto - Carga variables de entorno para Supabase
import os
from dotenv import load_dotenv

### Cargar variables de entorno desde .env
load_dotenv()

### Credenciales de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def validate_config():
    ### Verifica que las credenciales de Supabase esten configuradas
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL no esta configurado en el archivo .env")
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY no esta configurado en el archivo .env")
