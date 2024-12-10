"""Support for the XTTS speech service."""
import logging
import aiohttp
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    Provider,
)
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_LANG = "en"
DEFAULT_PORT = 8020
SUPPORT_LANGUAGES = ["en"]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORT_LANGUAGES),
    vol.Required("speaker_wav"): cv.string,
})

async def async_get_engine(hass, config, discovery_info=None):
    """Set up XTTS speech component."""
    return XTTSProvider(
        hass,
        config[CONF_HOST],
        config[CONF_PORT],
        config[CONF_LANG],
        config["speaker_wav"]
    )

class XTTSProvider(Provider):
    """The XTTS API provider."""

    def __init__(self, hass, host, port, lang, speaker_wav):
        """Initialize XTTS provider."""
        self.hass = hass
        self.host = host
        self.port = port
        self.lang = lang
        self.speaker_wav = speaker_wav
        self.name = "XTTS"

    @property
    def default_language(self):
        """Return the default language."""
        return self.lang

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from XTTS."""
        url = f"http://{self.host}:{self.port}/tts_stream"
        
        params = {
            "text": message,
            "speaker_wav": self.speaker_wav,
            "language": language
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        _LOGGER.error("Error %d on load URL %s", response.status, url)
                        return None, None

                    data = await response.read()
                    return "wav", data

        except aiohttp.ClientError as client_error:
            _LOGGER.error("Error on load URL: %s", client_error)
            return None, None