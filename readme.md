# Discord bot that can remember and chat with you

## Features

- Chatting: The bot will remember you, as well as the date you chatted with it.
- File conversion: The bot can use `ffmpeg` and `imagemagick` on behalf of you.
- Voice transcription: The bot can transcribe files with OpenAI Whisper.
- QR scanning: The bot can read QR codes.
- URL scanning: The bot can scan whether a URL is malicious with Cloudflare Radar.
- Download media: The bot can use `yt-dlp` on behalf of you to extract audio.

## Deploying

`git clone` the repo, then install dependancies.

- see `requirements.txt` for Python dependancies.
- install ffmpeg
- install imagemagick, as `magick mogrify` or `convert`
- `start.sh` should take care of the above steps on linux...
- You may have to troubleshoot the [Qreader dependancy](https://pypi.org/project/qreader/).