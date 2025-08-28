# dbutton v1.0.1

[![Versión de Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Una biblioteca ligera e independiente del framework para crear visualizaciones de datos interactivas y paginadas con capacidades avanzadas de filtrado para bots de Telegram. dbutton simplifica el proceso de visualización y navegación a través de grandes conjuntos de datos de manera amigable, con soporte nativo para todos los frameworks principales de bots de Python para Telegram.

## ✨ Características

- **Soporte para Múltiples Frameworks**: Funciona perfectamente con:
  - python-telegram-bot (v20+)
  - Aiogram (v3+)
  - Pyrogram (v2+)
- **Paginación Inteligente**: Navega fácilmente a través de grandes conjuntos de datos
- **Filtrado Avanzado**: Aplica y combina múltiples filtros al instante
- **Interfaz Interactiva**: Generación automática de botones con manejo de devoluciones de llamada
- **Altamente Personalizable**: Controla los campos mostrados, tamaño de página y diseño de botones
- **Tipado Estático**: Tipos completos para mejor soporte del IDE y confiabilidad del código
- **Asíncrono**: Construido con patrones modernos async/await para un rendimiento óptimo
- **Fuentes de Datos Flexibles**: Funciona con cualquier estructura de datos iterable
- **Serialización Personalizada**: Control total sobre el manejo de datos de devolución de llamada

## 🚀 Instalación

DButton está disponible en PyPI y se puede instalar mediante pip:

```bash
pip install git+https://github.com/phtndv/dbutton.git
```

### 📦 Dependencias

- **Python**: 3.8 o superior
- **Requerido**:
  - `typing-extensions`
- **Dependencias de Frameworks** (instalar según sea necesario):
  - `python-telegram-bot>=20.0` para soporte de python-telegram-bot
  - `aiogram>=3.0` para soporte de Aiogram
  - `pyrogram>=2.0` para soporte de Pyrogram

## 🚀 Inicio Rápido

### Importación

Puedes importar la clase `dbutton` de dos maneras:

```python
# Opción 1: Importar directamente la clase
try:
    from dbutton import dbutton
except ImportError:
    # Si falla, intentar importar desde el módulo
    from dbutton.dbutton import dbutton

# Opción 2: Importar el módulo y acceder a la clase
import dbutton
# Luego usar dbutton.dbutton()

# El resto de las importaciones del framework
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Sample data - can be any iterable of dictionaries
data = [
    {"id": 1, "name": "Alice", "role": "Admin", "status": "active"},
    {"id": 2, "name": "Bob", "role": "User", "status": "inactive"},
    # ... more items ...
]

# Inicializar dbutton con tus datos
# Si usaste 'from dbutton import dbutton'
button = dbutton(
    data_source=data,          # Tu fuente de datos
    fields=["name", "role"],   # Campos a mostrar en la lista
    page_size=5,               # Items por página
    framework="python-telegram-bot",  # Especifica el framework
    filters={"status": "active"}  # Filtros iniciales opcionales

# O si usaste 'import dbutton', entonces:
# button = dbutton.dbutton(
#     data_source=data,
#     fields=["name", "role"],
#     page_size=5,
#     framework="python-telegram-bot"
# )
)

# Command handler for /start
async def start(update: Update, context):
    # Generate message text and keyboard
    text, keyboard = button.build_message()
    await update.message.reply_text(
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown'  # Optional: for better formatting
    )

# Handle button callbacks
async def callback_handler(update: Update, context):
    await button.handle_callback(update, context)

# Set up and start the bot
def main():
    app = Application.builder()\
        .token("YOUR_BOT_TOKEN")\
        .build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()
```

### Aiogram (v2 o superior)

```python
from aiogram import Bot, Dispatcher, types
import dbutton

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher()

# Sample data
data = [
    {"id": 1, "name": "Alice", "role": "Admin"},
    {"id": 2, "name": "Bob", "role": "User"},
]

# Initialize with your data
button = dbutton(data_source=data, fields=["name", "role"], page_size=5)
handler = dbutton.AiogramHandler(button, bot)

@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await handler.send_message(message)

@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    await handler.handle_callback(callback_query)

if __name__ == "__main__":
    dp.run_polling(bot)
```

### Pyrogram

```python
from pyrogram import Client, filters
import dbutton

app = Client("my_bot", bot_token="YOUR_BOT_TOKEN")

# Sample data
data = [
    {"id": 1, "name": "Alice", "role": "Admin"},
    {"id": 2, "name": "Bob", "role": "User"},
]

# Initialize with your data
button = dbutton(data_source=data, fields=["name", "role"], page_size=5)
handler = dbutton.PyrogramHandler(button, app)

@app.on_message(filters.command("start"))
async def start(client, message):
    await handler.send_message(message)

@app.on_callback_query()
async def callback(client, callback_query):
    await handler.handle_callback(callback_query)

app.run()
```

## 📚 Referencia de la API (dbutton)

### Clase `dbutton.dbutton`

La clase principal para crear interfaces de botones interactivas y paginadas.

### Inicialización

```python
dbutton(
    data_source: Iterable[Dict[str, Any]],
    fields: List[str],
    page_size: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    callback_data_serializer: Optional[Callable] = None,
    callback_data_deserializer: Optional[Callable] = None,
    **kwargs
)
```

#### Parámetros

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `data_source` | `Iterable[Dict[str, Any]]` | Tus datos a paginar (lista de diccionarios) |
| `fields` | `List[str]` | Nombres de campos a mostrar (máx. 10) |
| `page_size` | `int` | Número de elementos por página (predeterminado: 20) |
| `filters` | `Dict[str, Any]` | Filtros iniciales a aplicar (opcional) |
| `callback_data_serializer` | `Callable` | Serializador personalizado para datos de devolución de llamada (opcional) |
| `callback_data_deserializer` | `Callable` | Deserializador personalizado para datos de devolución de llamada (opcional) |

### Métodos Principales

#### `build_message(framework: str = 'python-telegram-bot') -> Tuple[str, Any]`

Genera el texto del mensaje y el marcado del teclado para la página actual.

**Parámetros:**

- `framework`: El framework a utilizar (`'python-telegram-bot'`, `'aiogram'`, o `'pyrogram'`)

**Retorna:**

- `Tuple[str, Any]`: Una tupla que contiene el texto del mensaje y el marcado del teclado

#### `set_filters(**filters) -> None`

Actualiza los filtros activos y reinicia a la primera página.

**Parámetros:**

- `**filters`: Pares clave-valor de nombres de campo y valores por los que filtrar

#### `next_page() -> bool`

Avanza a la siguiente página si está disponible.

**Retorna:**

- `bool`: `True` si la página cambió, `False` si ya estaba en la última página

#### `prev_page() -> bool`

Retrocede a la página anterior si está disponible.

**Retorna:**

- `bool`: `True` si la página cambió, `False` si ya estaba en la primera página

#### `handle_callback(update: Any, context: Any = None) -> bool`

Handle callback queries from Telegram buttons.

**Parámetros:**

- `update`: El objeto de actualización del framework
- `context`: El objeto de contexto (si se usa python-telegram-bot)

**Retorna:**

- `bool`: `True` si la devolución de llamada fue manejada, `False` en caso contrario

## Ejemplos

### Filtros de Datos

```python
# Aplicar múltiples filtros
button.set_filters(role="Admin", status="active")

# Limpiar filtros
button.set_filters()
```

### Personalización de la Visualización

```python
# Mostrar campos específicos con tamaño de página personalizado
button = dbutton(
    data_source=data,
    fields=["username", "email", "status"],
    page_size=10,
    framework="python-telegram-bot"  # Asegúrate de especificar el framework
)
```

### Personalización de Texto de Botones

```python
# Personalizar el texto mostrado en los botones
button = dbutton(
    data_source=data,
    fields=["name", "role"],
    framework="python-telegram-bot",  # No olvides el framework
    button_text=lambda item: f"{item['name']} ({item['role']})"
)
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contribuciones

¡Las contribuciones son bienvenidas! Siéntete libre de enviar un Pull Request.

1. Haz un fork del repositorio
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Añadir una característica asombrosa'`)
4. Sube los cambios a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Registro de Cambios

### [1.0.1] - 2025-08-28

#### Añadido

- Diseño independiente del framework con API consistente de dbutton
- Soporte nativo para python-telegram-bot, Aiogram y Pyrogram
- Serialización y deserialización personalizadas de datos de devolución de llamada
- Tipos completos y documentación
- Pruebas unitarias para todos los frameworks

### [1.0.0] - 2025-08-27

- Lanzamiento inicial
