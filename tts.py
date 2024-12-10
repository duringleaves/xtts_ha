import logging
import aiohttp
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
    DOMAIN as TTS_DOMAIN,
)
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_LANG = "en"
DEFAULT_PORT = 8020
SUPPORT_LANGUAGES = ["en"]

CONF_SPEAKER_WAV = "speaker_wav"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORT_LANGUAGES),
    vol.Required(CONF_SPEAKER_WAV): cv.string,
})

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the XTTS speech platform."""
    _LOGGER.debug("Setting up XTTS TTS platform")
    
    tts_service = XTTSProvider(
        hass,
        config[CONF_HOST],
        config[CONF_PORT],
        config[CONF_LANG],
        config[CONF_SPEAKER_WAV]
    )

    async_add_devices([XTTSTTSEntity(tts_service)])

def get_engine(hass, config, discovery_info=None):
    """Set up XTTS speech component."""
    _LOGGER.debug("Setting up XTTS provider with config: %s", config)
    return XTTSProvider(
        hass,
        config[CONF_HOST],
        config[CONF_PORT],
        config.get(CONF_LANG, DEFAULT_LANG),
        config[CONF_SPEAKER_WAV]
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
        url = f"http://{self.host}:{self.port}/tts_to_audio"
        
        json_data = {
            "text": message,
            "speaker_wav": self.speaker_wav,
            "language": language
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        _LOGGER.debug("Attempting TTS POST request to %s with data: %s", url, json_data)
        
        try:
            async with aiohttp.ClientSession() as session:
                _LOGGER.debug("Making POST request to XTTS server")
                async with session.post(
                    url, 
                    json=json_data,
                    headers=headers,
                    allow_redirects=True,
                    timeout=30
                ) as response:
                    _LOGGER.debug("Got response with status: %s", response.status)
                    _LOGGER.debug("Response headers: %s", response.headers)
                    
                    if response.status != 200:
                        _LOGGER.error("Error %d on load URL %s", response.status, url)
                        response_text = await response.text()
                        _LOGGER.error("Response content: %s", response_text)
                        return None, None

                    data = await response.read()
                    _LOGGER.debug("Successfully read %d bytes of audio data", len(data))
                    
                    # Verify we got actual WAV data
                    if len(data) > 0:
                        _LOGGER.debug("First 4 bytes: %s", data[:4].hex())
                        
                    return "wav", data

        except aiohttp.ClientError as client_error:
            _LOGGER.error("Error on load URL: %s", client_error)
            return None, None
        except Exception as e:
            _LOGGER.error("Unexpected error: %s", str(e))
            _LOGGER.exception("Full exception:")
            return None, None

class XTTSTTSEntity(TextToSpeechEntity):
    """The XTTS TTS API entity."""
    
    def __init__(self, tts_service):
        """Initialize XTTS TTS entity."""
        self._tts_service = tts_service

    @property
    def name(self):
        """Return name of entity."""
        return "XTTS TTS"

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return self._tts_service.supported_languages

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS audio."""
        return await self._tts_service.async_get_tts_audio(message, language, options)
