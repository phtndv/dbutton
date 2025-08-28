import json
from typing import Any, Dict, List, Optional, Union, Callable, Type
from .utils import apply_filters, paginate

# Type aliases
CallbackData = Dict[str, Any]
KeyboardMarkup = Any  # Will be framework-specific InlineKeyboardMarkup
Message = Any  # Will be framework-specific Message type
CallbackQuery = Any  # Will be framework-specific CallbackQuery type

class dbutton:
    """
    A framework-agnostic paginated button interface for Telegram bots.
    
    Args:
        data_source: Iterable of dictionaries containing the data to display
        fields: List of field names to display (max 10)
        page_size: Number of items per page (default: 20)
        filters: Optional initial filters to apply
        callback_data_serializer: Optional custom serializer for callback data
        callback_data_deserializer: Optional custom deserializer for callback data
    """
    def __init__(
        self,
        data_source: List[Dict[str, Any]],
        fields: List[str],
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        callback_data_serializer: Optional[Callable[[Dict[str, Any]], str]] = None,
        callback_data_deserializer: Optional[Callable[[str], Dict[str, Any]]] = None
    ):
        if len(fields) > 10:
            raise ValueError("Maximum 10 fields allowed")
            
        self.raw_data = list(data_source)
        self.fields = fields
        self.page_size = page_size
        self.filters = filters or {}
        self.current_page = 1
        self._serialize_callback = callback_data_serializer or json.dumps
        self._deserialize_callback = callback_data_deserializer or json.loads
        self._handlers = {}
        self._refresh()
        
        # Initialize framework-specific handlers
        self._init_framework_handlers()
    
    def _init_framework_handlers(self):
        """Initialize framework-specific handlers"""
        try:
            from telegram import InlineKeyboardButton as PTBInlineKeyboardButton
            from telegram import InlineKeyboardMarkup as PTBInlineKeyboardMarkup
            self._handlers['python-telegram-bot'] = {
                'button': PTBInlineKeyboardButton,
                'markup': PTBInlineKeyboardMarkup
            }
        except ImportError:
            pass
            
        try:
            from aiogram.types import InlineKeyboardButton as AioInlineKeyboardButton
            from aiogram.types import InlineKeyboardMarkup as AioInlineKeyboardMarkup
            self._handlers['aiogram'] = {
                'button': AioInlineKeyboardButton,
                'markup': AioInlineKeyboardMarkup
            }
        except ImportError:
            pass
            
        try:
            from pyrogram.types import InlineKeyboardButton as PyroInlineKeyboardButton
            from pyrogram.types import InlineKeyboardMarkup as PyroInlineKeyboardMarkup
            self._handlers['pyrogram'] = {
                'button': PyroInlineKeyboardButton,
                'markup': PyroInlineKeyboardMarkup
            }
        except ImportError:
            pass
    
    def _refresh(self) -> None:
        """Recalculate filtered data and current page"""
        self.filtered = apply_filters(self.raw_data, self.filters)
        self.page_data, self.total_pages = paginate(
            self.filtered, self.current_page, self.page_size
        )
    
    def set_filters(self, **kwargs) -> None:
        """
        Update filters and return to the first page.
        
        Args:
            **kwargs: Field-value pairs to filter by
        """
        self.filters = kwargs
        self.current_page = 1
        self._refresh()
    
    def next_page(self) -> bool:
        """Move to the next page if possible"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._refresh()
            return True
        return False
    
    def prev_page(self) -> bool:
        """Move to the previous page if possible"""
        if self.current_page > 1:
            self.current_page -= 1
            self._refresh()
            return True
        return False
    
    def build_message(self, framework: str = 'python-telegram-bot') -> tuple[str, Any]:
        """
        Build the message text and keyboard markup.
        
        Args:
            framework: The framework being used ('python-telegram-bot', 'aiogram', or 'pyrogram')
            
        Returns:
            A tuple of (text, keyboard_markup)
        """
        # Build message text
        lines = []
        for idx, record in enumerate(self.page_data, start=1):
            parts = [f"{idx}"]
            for field in self.fields:
                parts.append(str(record.get(field, "")))
            lines.append(" — ".join(parts))
        text = "\n".join(lines) or "No data available."
        
        # Get the appropriate button and markup classes
        handler = self._handlers.get(framework, self._handlers.get('python-telegram-bot'))
        if not handler:
            raise ValueError(f"No handler found for framework: {framework}")
            
        ButtonClass = handler['button']
        MarkupClass = handler['markup']
        
        # Create numbered buttons
        button_rows = []
        for i in range(1, len(self.page_data) + 1):
            callback_data = self._serialize_callback({
                "action": "detail",
                "index": i - 1,
                "page": self.current_page
            })
            button_rows.append([ButtonClass(str(i), callback_data=callback_data)])
        
        # Add navigation buttons
        nav_buttons = []
        if self.current_page > 1:
            nav_buttons.append(ButtonClass(
                "«", 
                callback_data=self._serialize_callback({"action": "prev"})
            ))
        if self.current_page < self.total_pages:
            nav_buttons.append(ButtonClass(
                "»", 
                callback_data=self._serialize_callback({"action": "next"})
            ))
        
        if nav_buttons:
            button_rows.append(nav_buttons)
        
        return text, MarkupClass(button_rows)
    
    def _handle_callback(self, callback_data: Union[str, Dict[str, Any]]) -> tuple[bool, str]:
        """
        Handle callback data and update state accordingly.
        
        Args:
            callback_data: The callback data from the button press
            
        Returns:
            A tuple of (handled, message) where handled is a boolean indicating
            if the callback was handled, and message is a status message.
        """
        if isinstance(callback_data, str):
            try:
                data = self._deserialize_callback(callback_data)
            except (json.JSONDecodeError, TypeError):
                return False, "Invalid callback data"
        else:
            data = callback_data
            
        action = data.get("action")
        
        if action == "next":
            if self.next_page():
                return True, "Next page"
            return False, "Already on last page"
            
        elif action == "prev":
            if self.prev_page():
                return True, "Previous page"
            return False, "Already on first page"
            
        elif action == "detail":
            index = data.get("index", 0)
            if 0 <= index < len(self.page_data):
                self.selected_item = self.page_data[index]
                return True, f"Selected item {index}"
            return False, "Invalid item index"
            
        return False, "Unknown action"
    
    # Backward compatibility
    def handle_callback(self, update, context=None):
        """
        Legacy method for python-telegram-bot compatibility.
        
        Args:
            update: The update object from python-telegram-bot
            context: The context object from python-telegram-bot
            
        Returns:
            True if the callback was handled, False otherwise
        """
        if hasattr(update, 'callback_query') and update.callback_query:
            query = update.callback_query
            try:
                data = self._deserialize_callback(query.data)
            except (json.JSONDecodeError, TypeError):
                return False
                
            handled, _ = self._handle_callback(data)
            
            if handled:
                text, keyboard = self.build_message('python-telegram-bot')
                query.edit_message_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            
            return handled
        return False