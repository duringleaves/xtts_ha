import logging
import voluptuous as vol
from homeassistant.setup import async_setup_component

_LOGGER = logging.getLogger(__name__)
DOMAIN = "xtts_tts"

async def async_setup(hass, config):
    """Set up the XTTS TTS component."""
    _LOGGER.debug("Initializing XTTS TTS platform")
    if DOMAIN not in config:
        return True

    return True

async def async_setup_entry(hass, config_entry):
    """Set up XTTS TTS from a config entry."""
    return True
