from typing import Any, Dict, Optional, Union, Type, Tuple
from .button import dbutton as DButton

class BaseHandler:
    """Base handler for framework-specific implementations"""
    
    def __init__(self, button_instance: 'DButton', bot_instance: Any = None):
        """
        Initialize with a dbutton instance and optional bot instance
        
        Args:
            button_instance: An instance of dbutton
            bot_instance: Optional bot/client instance for the framework
        """
        if not isinstance(button_instance, DButton):
            raise TypeError("button_instance must be an instance of dbutton")
            
        self.button = button_instance
        self.bot = bot_instance
    
    async def handle_callback(self, *args, **kwargs) -> bool:
        """Handle callback from the framework"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def send_message(self, *args, **kwargs) -> Any:
        """Send a message using the framework"""
        raise NotImplementedError("Subclasses must implement this method")


class PythonTelegramBotHandler(BaseHandler):
    """Handler for python-telegram-bot framework"""
    
    async def handle_callback(self, update, context) -> bool:
        """
        Handle callback from python-telegram-bot
        
        Args:
            update: Update object from python-telegram-bot
            context: Context object from python-telegram-bot
            
        Returns:
            bool: True if callback was handled successfully
        """
        from telegram import Update
        
        if not isinstance(update, Update):
            raise TypeError("update must be an instance of telegram.Update")
            
        query = update.callback_query
        if not query:
            return False
            
        await query.answer()
        
        # Use DButton's built-in handler
        handled = await self.button.handle_callback(update, context)
        
        if handled:
            # Get updated message content
            text, keyboard = self.button.build_message()
            
            # Update the message
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        return handled
    
    async def send_message(self, update, context=None, *args, **kwargs) -> Any:
        """
        Send a message using python-telegram-bot
        
        Args:
            update: Update object from python-telegram-bot
            context: Optional context object
            
        Returns:
            The sent message
        """
        if not hasattr(update, 'message') or not update.message:
            raise ValueError("Invalid update object - missing 'message' attribute")
            
        text, keyboard = self.button.build_message()
        return await update.message.reply_text(
            text=text,
            reply_markup=keyboard,
            *args,
            **kwargs
        )


class AiogramHandler(BaseHandler):
    """Handler for Aiogram framework"""
    
    def __init__(self, button_instance: 'dbutton', bot: Any = None):
        """
        Initialize with dbutton and optional Aiogram bot instance
        
        Args:
            button_instance: Instance of dbutton
            bot: Optional Aiogram bot instance (will be used if provided)
        """
        super().__init__(button_instance, bot)
        self._check_aiogram_import()
    
    def _check_aiogram_import(self):
        """Verify Aiogram is installed"""
        try:
            from aiogram import Bot, Dispatcher, types
        except ImportError:
            raise ImportError(
                "Aiogram is required but not installed. "
                "Install with: pip install pycypher[aiogram]"
            )
    
    async def handle_callback(self, callback_query, *args, **kwargs) -> bool:
        """
        Handle callback from Aiogram
        
        Args:
            callback_query: CallbackQuery object from Aiogram
            
        Returns:
            bool: True if callback was handled successfully
        """
        from aiogram import types
        
        if not isinstance(callback_query, types.CallbackQuery):
            raise TypeError("callback_query must be an instance of aiogram.types.CallbackQuery")
        
        # Use DButton's built-in handler with a mock update
        class MockUpdate:
            def __init__(self, query):
                self.callback_query = query
                
        mock_update = MockUpdate(callback_query)
        handled = await self.button.handle_callback(mock_update, None)
        
        if handled:
            # Get updated message content
            text, keyboard = self.button.build_message()
            
            # Update the message
            bot = self.bot or callback_query.bot
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=text,
                reply_markup=keyboard
            )
            
        return handled
    
    async def send_message(self, message, *args, **kwargs) -> Any:
        """
        Send a message using Aiogram
        
        Args:
            message: Message object or chat_id
            
        Returns:
            The sent message
        """
        from aiogram import types
        
        text, keyboard = self.button.build_message()
        
        if isinstance(message, types.Message):
            return await message.answer(
                text=text,
                reply_markup=keyboard,
                *args,
                **kwargs
            )
        elif isinstance(message, (int, str)):
            if not self.bot:
                raise ValueError("Bot instance is required when passing chat_id directly")
            return await self.bot.send_message(
                chat_id=message,
                text=text,
                reply_markup=keyboard,
                *args,
                **kwargs
            )
        else:
            raise TypeError("message must be an aiogram.types.Message or chat_id (int/str)")


class PyrogramHandler(BaseHandler):
    """Handler for Pyrogram framework"""
    
    def __init__(self, button_instance: 'DButton', client: Any = None):
        """
        Initialize with dbutton and optional Pyrogram client
        
        Args:
            button_instance: Instance of dbutton
            client: Optional Pyrogram Client instance
        """
        super().__init__(button_instance, client)
        self._check_pyrogram_import()
    
    def _check_pyrogram_import(self):
        """Verify Pyrogram is installed"""
        try:
            from pyrogram import Client, filters
        except ImportError:
            raise ImportError(
                "Pyrogram is required but not installed. "
                "Install with: pip install pycypher[pyrogram]"
            )
    
    async def handle_callback(self, client, callback_query) -> bool:
        """
        Handle callback from Pyrogram
        
        Args:
            client: Pyrogram Client that received the callback
            callback_query: CallbackQuery object from Pyrogram
            
        Returns:
            bool: True if callback was handled successfully
        """
        from pyrogram.types import CallbackQuery
        
        if not isinstance(callback_query, CallbackQuery):
            raise TypeError("callback_query must be an instance of pyrogram.types.CallbackQuery")
        
        # Use DButton's built-in handler with a mock update
        class MockUpdate:
            def __init__(self, query):
                self.callback_query = query
                
        mock_update = MockUpdate(callback_query)
        handled = await self.button.handle_callback(mock_update, None)
        
        if handled:
            # Get updated message content
            text, keyboard = self.button.build_message()
            
            # Update the message
            await callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard
            )
            
        return handled
    
    async def send_message(self, message, *args, **kwargs) -> Any:
        """
        Send a message using Pyrogram
        
        Args:
            message: Message object or chat_id
            
        Returns:
            The sent message
        """
        from pyrogram.types import Message
        
        text, keyboard = self.button.build_message()
        
        if isinstance(message, Message):
            return await message.reply_text(
                text=text,
                reply_markup=keyboard,
                *args,
                **kwargs
            )
        elif isinstance(message, (int, str)):
            if not self.bot:
                raise ValueError("Client instance is required when passing chat_id directly")
            return await self.bot.send_message(
                chat_id=message,
                text=text,
                reply_markup=keyboard,
                *args,
                **kwargs
            )
        else:
            raise TypeError("message must be a pyrogram.types.Message or chat_id (int/str)")
