# DButton v1.0.1

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, framework-agnostic Python library for creating interactive, paginated data displays with advanced filtering capabilities for Telegram bots. DButton simplifies the process of displaying and navigating through large datasets in a user-friendly way, with native support for all major Python Telegram bot frameworks.

## ✨ Features

- **Multi-Framework Support**: Seamlessly works with:
  - python-telegram-bot (v20+)
  - Aiogram (v3+)
  - Pyrogram (v2+)
- **Smart Pagination**: Effortlessly navigate through large datasets
- **Advanced Filtering**: Apply and combine multiple filters on the fly
- **Interactive Interface**: Automatic button generation with callback handling
- **Highly Customizable**: Control display fields, page size, and button layouts
- **Type Safety**: Full type hints for better IDE support and code reliability
- **Asynchronous**: Built with modern async/await patterns for optimal performance
- **Flexible Data Sources**: Works with any iterable data structure
- **Custom Serialization**: Full control over callback data handling

## 🚀 Installation

DButton is available on PyPI and can be installed via pip:

```bash
# Install from PyPI (recommended)
pip install dbutton

# Or install directly from GitHub
pip install git+https://github.com/phtndv/dbutton.git
```

### 📦 Dependencies

- **Python**: 3.8 or higher
- **Required**: 
  - `typing-extensions`
- **Framework Dependencies** (install as needed):
  - `python-telegram-bot>=20.0` for python-telegram-bot support
  - `aiogram>=3.0` for Aiogram support
  - `pyrogram>=2.0` for Pyrogram support

## 🚀 Quick Start

### Basic Usage with python-telegram-bot

```python
import dbutton
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Sample data - can be any iterable of dictionaries
data = [
    {"id": 1, "name": "Alice", "role": "Admin", "status": "active"},
    {"id": 2, "name": "Bob", "role": "User", "status": "inactive"},
    # ... more items ...
]

# Initialize the DButton with your data
button = dbutton.DButton(
    data_source=data,          # Your data source
    fields=["name", "role"],   # Fields to display in the list
    page_size=5,               # Items per page
    filters={"status": "active"}  # Optional initial filters
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

### Aiogram (v2+)

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
button = dbutton.DButton(data_source=data, fields=["name", "role"], page_size=5)
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
button = dbutton.DButton(data_source=data, fields=["name", "role"], page_size=5)
handler = dbutton.PyrogramHandler(button, app)

@app.on_message(filters.command("start"))
async def start(client, message):
    await handler.send_message(message)

@app.on_callback_query()
async def callback(client, callback_query):
    await handler.handle_callback(callback_query)

app.run()
```

## 📚 API Reference (dbutton)

### `dbutton.DButton` Class

The main class for creating interactive, paginated button interfaces.

### Initialization

```python
dbutton.DButton(
    data_source: Iterable[Dict[str, Any]],
    fields: List[str],
    page_size: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    callback_data_serializer: Optional[Callable] = None,
    callback_data_deserializer: Optional[Callable] = None,
    **kwargs
)
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `data_source` | `Iterable[Dict[str, Any]]` | Your data to paginate (list of dictionaries) |
| `fields` | `List[str]` | Field names to display (max 10) |
| `page_size` | `int` | Number of items per page (default: 20) |
| `filters` | `Dict[str, Any]` | Initial filters to apply (optional) |
| `callback_data_serializer` | `Callable` | Custom callback data serializer (optional) |
| `callback_data_deserializer` | `Callable` | Custom callback data deserializer (optional) |

### Core Methods

#### `build_message(framework: str = 'python-telegram-bot') -> Tuple[str, Any]`

Generate the message text and keyboard markup for the current page.

**Parameters:**

- `framework`: The framework to use (`'python-telegram-bot'`, `'aiogram'`, or `'pyrogram'`)

**Returns:**

- `Tuple[str, Any]`: A tuple containing the message text and keyboard markup

#### `set_filters(**filters) -> None`

Update the active filters and reset to the first page.

**Parameters:**

- `**filters`: Key-value pairs to filter the data by

#### `next_page() -> bool`

Move to the next page if available.

**Returns:**

- `bool`: `True` if the page changed, `False` if already on the last page

#### `prev_page() -> bool`

Move to the previous page if available.

**Returns:**
- `bool`: `True` if the page changed, `False` if already on the first page

#### `handle_callback(update: Any, context: Any = None) -> bool`

Handle callback queries from Telegram buttons.

**Parameters:**

- `update`: The update object from the framework
- `context`: The context object (if using python-telegram-bot)

**Returns:**

- `bool`: `True` if the callback was handled, `False` otherwise

## Examples

### Filtering Data

```python
# Apply filters
button.set_filters(role="Admin")

# Clear filters
button.set_filters()
```

### Customizing Display

```python
# Show specific fields with custom page size
button = DButton(
    data_source=users,
    fields=["username", "email", "status"],
    page_size=10
)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog

### [1.0.1] - 2025-08-28

#### Added

- Framework-agnostic design with consistent DButton API
- Native support for python-telegram-bot, Aiogram, and Pyrogram
- Custom callback serialization/deserialization
- Comprehensive type hints and documentation
- Unit tests for all frameworks

### [1.0.0] - 2025-08-27

- Initial release
