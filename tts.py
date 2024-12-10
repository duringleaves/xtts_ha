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
    _LOGGER.debug("Setting up XTTS provider with config: %s", config)
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
        _LOGGER.debug(
            "Initialized XTTS provider with host=%s, port=%s, lang=%s, speaker=%s",
            host, port, lang, speaker_wav
        )

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
        
        _LOGGER.debug("Attempting TTS request to %s with params: %s", url, params)
        
        try:
            async with aiohttp.ClientSession() as session:
                _LOGGER.debug("Making GET request to XTTS server")
                async with session.get(url, params=params) as response:
                    _LOGGER.debug("Got response with status: %s", response.status)
                    if response.status != 200:
                        _LOGGER.error("Error %d on load URL %s", response.status, url)
                        return None, None

                    data = await response.read()
                    _LOGGER.debug("Successfully read %d bytes of audio data", len(data))
                    return "wav", data

        except aiohttp.ClientError as client_error:
            _LOGGER.error("Error on load URL: %s", client_error)
            return None, None
        except Exception as e:
            _LOGGER.error("Unexpected error: %s", str(e))
            return None, None