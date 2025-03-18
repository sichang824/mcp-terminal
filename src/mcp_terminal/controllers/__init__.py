"""Terminal controllers package."""

from .base import BaseTerminalController
from .subprocess import SubprocessTerminalController

# Conditionally import platform-specific controllers
import platform

if platform.system() == "Darwin":  # macOS
    from .applescript import AppleScriptTerminalController
    
    # Try to import iTerm2 controller if the package is available
    try:
        import iterm2
        from .iterm import ITermController
        ITERM_AVAILABLE = True
    except ImportError:
        ITERM_AVAILABLE = False
else:
    ITERM_AVAILABLE = False


def get_controller(controller_type=None):
    """
    Factory function to get a terminal controller based on the specified type or platform.
    
    Args:
        controller_type: The type of controller to get ("iterm", "applescript", "subprocess")
                        or None to auto-detect
    
    Returns:
        A terminal controller instance
    """
    system = platform.system()
    
    # If controller type is specified, try to use it
    if controller_type:
        if controller_type == "iterm" and system == "Darwin":
            if ITERM_AVAILABLE:
                return ITermController()
            else:
                raise ImportError("iTerm2 API not available. Install with 'pip install iterm2'")
        elif controller_type == "applescript" and system == "Darwin":
            return AppleScriptTerminalController()
        elif controller_type == "subprocess":
            return SubprocessTerminalController()
        else:
            raise ValueError(f"Controller type '{controller_type}' not supported on {system}")
    
    # Auto-detect the best controller
    if system == "Darwin":
        if ITERM_AVAILABLE:
            try:
                # Check if iTerm2 is installed
                import subprocess
                result = subprocess.run(
                    ["osascript", "-e", 'tell application "System Events" to exists application process "iTerm2"'],
                    capture_output=True, text=True
                )
                if "true" in result.stdout.lower():
                    return ITermController()
            except Exception:
                pass
        
        # Fall back to AppleScript for macOS Terminal
        return AppleScriptTerminalController()
    
    # Default to subprocess controller for all other platforms
    return SubprocessTerminalController()
