"""
Tests for fade transition functionality.
"""

import pytest
import customtkinter as ctk
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.transition_utils import TransitionManager, create_fade_dialog, show_fade_popup, show_fade_confirmation_dialog


class TestTransitionManager:
    """Test cases for TransitionManager class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.root = ctk.CTk()
        self.dialog = ctk.CTkToplevel(self.root)
        self.transition_manager = TransitionManager(self.dialog, 300)
    
    def teardown_method(self):
        """Cleanup test environment."""
        try:
            self.dialog.destroy()
            self.root.destroy()
        except:
            pass
    
    def test_initialization(self):
        """Test TransitionManager initialization."""
        assert self.transition_manager.dialog == self.dialog
        assert self.transition_manager.duration_ms == 300
        assert not self.transition_manager.fade_in_progress
        assert not self.transition_manager.fade_out_progress
    
    @patch.object(ctk.CTkToplevel, 'attributes')
    def test_fade_in(self, mock_attributes):
        """Test fade in animation."""
        mock_attributes.return_value = 0.0
        
        # Mock the after method to capture the animation
        original_after = self.dialog.after
        animation_calls = []
        
        def mock_after(delay, callback):
            animation_calls.append((delay, callback))
            return original_after(delay, callback)
        
        self.dialog.after = mock_after
        
        # Start fade in
        self.transition_manager.fade_in()
        
        # Verify animation was started
        assert self.transition_manager.fade_in_progress
        assert len(animation_calls) > 0
    
    @patch.object(ctk.CTkToplevel, 'attributes')
    def test_fade_out(self, mock_attributes):
        """Test fade out animation."""
        mock_attributes.return_value = 1.0
        
        # Mock the after method to capture the animation
        original_after = self.dialog.after
        animation_calls = []
        
        def mock_after(delay, callback):
            animation_calls.append((delay, callback))
            return original_after(delay, callback)
        
        self.dialog.after = mock_after
        
        # Start fade out
        self.transition_manager.fade_out()
        
        # Verify animation was started
        assert self.transition_manager.fade_out_progress
        assert len(animation_calls) > 0
    
    def test_fallback_without_attributes(self):
        """Test fallback behavior when attributes are not available."""
        # Create a mock dialog without attributes
        mock_dialog = Mock()
        mock_dialog.winfo_exists.return_value = True
        mock_dialog.after = Mock()
        
        transition_manager = TransitionManager(mock_dialog, 300)
        
        # Test fade in with fallback
        callback_called = False
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        transition_manager.fade_in(test_callback)
        
        # Verify callback was called immediately due to fallback
        assert callback_called


class TestFadeDialogFunctions:
    """Test cases for fade dialog utility functions."""
    
    def setup_method(self):
        """Setup test environment."""
        self.root = ctk.CTk()
    
    def teardown_method(self):
        """Cleanup test environment."""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_create_fade_dialog(self):
        """Test create_fade_dialog function."""
        dialog, transition_manager = create_fade_dialog(
            self.root, "Test Dialog", "400x300", 300
        )
        
        assert isinstance(dialog, ctk.CTkToplevel)
        assert isinstance(transition_manager, TransitionManager)
        assert dialog.title() == "Test Dialog"
        assert dialog.geometry().startswith("400x300")
        
        # Cleanup
        dialog.destroy()
    
    def test_show_fade_popup(self):
        """Test show_fade_popup function."""
        with patch('utils.transition_utils.create_fade_dialog') as mock_create:
            mock_dialog = Mock()
            mock_transition = Mock()
            mock_create.return_value = (mock_dialog, mock_transition)
            
            show_fade_popup(self.root, "Test", "Message", "green")
            
            # Verify dialog was created
            mock_create.assert_called_once()
    
    def test_show_fade_confirmation_dialog(self):
        """Test show_fade_confirmation_dialog function."""
        with patch('utils.transition_utils.create_fade_dialog') as mock_create:
            mock_dialog = Mock()
            mock_transition = Mock()
            mock_create.return_value = (mock_dialog, mock_transition)
            
            def test_callback():
                pass
            
            show_fade_confirmation_dialog(
                self.root, "Test", "Message", test_callback
            )
            
            # Verify dialog was created
            mock_create.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 