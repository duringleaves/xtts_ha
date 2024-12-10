import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
DOMAIN = "xtts_tts"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the XTTS TTS component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up XTTS TTS from a config entry."""
    return True