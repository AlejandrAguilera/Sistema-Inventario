## 🛠 Herramientas Utilizadas
- **IDE**: Visual Studio Code
- **Lenguaje de programación**: Python 3.11+
- **Framework Web**: Flask
- **Base de Datos (DBMS)**: MySQL 8.0 (usando MySQL Workbench para administración)
- **Frontend**: Bootstrap 5 para diseño responsivo
- **Servidor de desarrollo**: Ejecutado en un **servidor local** usando `localhost`

## ▶️ Pasos para Ejecutar la Aplicación
1. **Clonar o descargar el repositorio** del proyecto en tu máquina local.
2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate     # En Linux/Mac
   venv\Scripts\activate        # En Windows
3. **Instalar las dependencias del proyecto**:
   pip install -r requirements.txt
4. **Configurar la conexión a la base de datos**: Crea un archivo config.py con el siguiente contenido:
  MYSQL_HOST = 'localhost'
  MYSQL_USER = 'root'
  MYSQL_PASSWORD = 'tu_contraseña'
  MYSQL_DB = 'inventario'
  SECRET_KEY = 'clave_secreta_segura'
5. **Ejecutar la aplicación en modo desarrollo**:
   flask run
6. **Acceder a la app desde el navegador**:
   http://localhost:5000





