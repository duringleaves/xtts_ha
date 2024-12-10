First attempt at creating an xtts-api-server integration for Home Assistant.  No warranties expressed or implied.

INSTRUCTIONS:
- in your ./config/custom_components/ directory, extract the contents to ./xtts_tts
- edit ./config/configuration.yaml:
  tts:
  - platform: xtts_tts
    host: "192.168.1.xx"
    port: 8020
    speaker_wav: "speaker_reference.wav"
    language: "en"
- restart home assistant
- under Developer Tools / Actions, try this:
  action: tts.xtts_tts_say
    target:
      entity_id: media_player.shield # use one of your own media_player entities
    data:
      message: "I think this is working now!"
      entity_id: media_player.shield
