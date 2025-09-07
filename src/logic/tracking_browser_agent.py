import asyncio
from typing import Any, Optional, Callable
from collections.abc import Awaitable
from browser_use import Agent as BrowserAgent
from browser_use.browser.events import ClickElementEvent, TypeTextEvent
from browser_use.agent.views import AgentHistoryList
from src.logic.element_tracker import element_tracker
import streamlit as st
from pathlib import Path


class TrackingBrowserAgent(BrowserAgent):
    """Browser agent that tracks element interactions for script generation."""
    
    def __init__(self, *args, **kwargs):
        # Extract our custom parameters before passing to parent
        self.generate_gif = kwargs.pop('generate_gif', False)
        self.highlight_elements = kwargs.pop('highlight_elements', True)
        self.record_video_dir = kwargs.pop('record_video_dir', None)
        self.record_har_path = kwargs.pop('record_har_path', None)
        self.traces_dir = kwargs.pop('traces_dir', None)
        headless = kwargs.pop('headless', None)
        window_size = kwargs.pop('window_size', None)
        self.use_vision = kwargs.pop('use_vision', True)
        self.record_har_content = kwargs.pop('record_har_content', 'embed')
        self.record_har_mode = kwargs.pop('record_har_mode', 'full')
        self.vision_detail_level = kwargs.pop('vision_detail_level', 'auto')
        self.max_history_items = kwargs.pop('max_history_items', None)
        self.save_conversation_path = kwargs.pop('save_conversation_path', None)
        
        # Set up browser profile with enhanced features and recording parameters
        if 'browser' not in kwargs and 'browser_profile' not in kwargs:
            from browser_use import BrowserProfile
            browser_profile = BrowserProfile(
                headless=headless,
                window_size=window_size,
                record_video_dir=self.record_video_dir,
                record_har_path=self.record_har_path,
                traces_dir=self.traces_dir,
                record_har_content=self.record_har_content,
                record_har_mode=self.record_har_mode
            )
            kwargs['browser_profile'] = browser_profile
        
        # Pass the browser-use specific parameters directly to the Agent
        # Use a string path for generate_gif to control where browser-use creates the GIF
        # If we want to generate our own GIF in a specific location, we'll handle that separately
        if self.generate_gif and self.record_video_dir:
            kwargs['generate_gif'] = str(Path(self.record_video_dir) / "execution.gif")
        else:
            kwargs['generate_gif'] = self.generate_gif
        kwargs['highlight_elements'] = self.highlight_elements
        kwargs['use_vision'] = self.use_vision
        kwargs['vision_detail_level'] = self.vision_detail_level
        kwargs['max_history_items'] = self.max_history_items
        kwargs['save_conversation_path'] = self.save_conversation_path
        
        super().__init__(*args, **kwargs)
        self.on_step_end_callback = None
        self._interactions_cleared = False
        self._event_handlers_registered = False
    
    def set_on_step_end_callback(self, callback: Callable):
        """Set a callback function to be called at the end of each step."""
        self.on_step_end_callback = callback
    
    async def run(
        self,
        max_steps: int = 100,
        on_step_start: Callable[['BrowserAgent'], Awaitable[None]] | None = None,
        on_step_end: Callable[['BrowserAgent'], Awaitable[None]] | None = None,
    ) -> AgentHistoryList:
        """Run the agent and track interactions."""
        # Clear previous interactions only if this is a fresh run
        if not self._interactions_cleared:
            element_tracker.clear_interactions()
            self._interactions_cleared = True
        
        # Ensure event handlers are registered before running
        self._ensure_event_handlers_registered()
        
        # Override the on_step_end callback to add our tracking
        async def wrapped_on_step_end(agent):
            # Call the original on_step_end if it exists
            if on_step_end:
                await on_step_end(agent)
            
            # Call our custom callback if it exists
            if self.on_step_end_callback:
                if asyncio.iscoroutinefunction(self.on_step_end_callback):
                    await self.on_step_end_callback(agent)
                else:
                    self.on_step_end_callback(agent)
        
        # Run the parent agent with our wrapped callback
        try:
            result = await super().run(max_steps, on_step_start, wrapped_on_step_end)
            
            # After execution, ensure GIF path is stored in session state for UI display
            # The GIF should already be created by browser-use in the correct location
            if self.generate_gif and self.record_video_dir:
                try:
                    # The GIF should already exist in the specified location
                    gif_path = Path(self.record_video_dir) / "execution.gif"
                    print(f"Expected GIF location: {gif_path}")
                    
                    # Store GIF path in session state for UI display
                    if 'history' in st.session_state:
                        st.session_state.history['gif_path'] = str(gif_path)
                    else:
                        st.session_state.history = {'gif_path': str(gif_path)}
                except Exception as e:
                    print(f"Failed to set GIF path in session state: {e}")
            
            return result
        except Exception as e:
            # Re-raise the exception to be handled by the caller
            raise
    
    def _ensure_event_handlers_registered(self):
        """Ensure event handlers are registered when browser is available."""
        # Only register once and only if browser is available
        if self._event_handlers_registered:
            return
            
        if not hasattr(self, 'browser_session') or not self.browser_session:
            print("Warning: Browser session not available for event handler registration")
            return  # Browser not initialized yet, will try again later
            
        # Register click event handler
        self.browser_session.event_bus.on(ClickElementEvent, self._handle_click_event)
        
        # Register type text event handler
        self.browser_session.event_bus.on(TypeTextEvent, self._handle_type_text_event)
        
        self._event_handlers_registered = True
        print("Event handlers registered successfully")
    
    def _handle_click_event(self, event: ClickElementEvent):
        """Handle click events and track them."""
        try:
            print(f"Handling click event: {event}")  # Debug print
            element_tracker.track_click(event)
        except Exception as e:
            print(f"Error tracking click event: {e}")
    
    def _handle_type_text_event(self, event: TypeTextEvent):
        """Handle type text events and track them."""
        try:
            print(f"Handling type text event: {event}")  # Debug print
            element_tracker.track_type_text(event)
        except Exception as e:
            print(f"Error tracking type text event: {e}")
    
    def get_tracked_interactions(self):
        """Get all tracked element interactions."""
        # Ensure handlers are registered
        self._ensure_event_handlers_registered()
        return element_tracker.get_interactions_summary()