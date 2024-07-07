# Discord bot that can remember and chat with you

For webpage-based documentation, see [here](https://hackclub.jclink.link/documentations/discord-bots/memory-discord-bot)

## Features

- Chatting: The bot will remember you, as well as the date you chatted with it.
- File conversion: The bot can use `ffmpeg` and `imagemagick` on behalf of you.
- Voice transcription: The bot can transcribe files with OpenAI Whisper.
- QR scanning: The bot can read QR codes.
- URL scanning: The bot can scan whether a URL is malicious with Cloudflare Radar.
- Download media: The bot can use `yt-dlp` on behalf of you to extract audio.

## Deploying

`git clone` the repo, then install dependancies.

**If installing on a resource-constrained environment, for example an e2-micro VM, run `pip install torch --no-cache-dir` first**
Then, run `pip install -r requirements.txt`.
After that, you may want to install ffmpeg and imagemagick, with the package manager of your choice on Linux or with an installer on Windows.
On linux, run: `sudo apt install libzbar0` (Else, see below for QReader repo instructions)

- see `requirements.txt` for Python dependancies.
- install ffmpeg
- install imagemagick, as `magick mogrify` or `convert`
- You may have to troubleshoot the [Qreader dependancy](https://pypi.org/project/qreader/).
- make a directory named ltmemories and stmemories

## Known issues

The QR code read function will run slowly if your server is slow.
- The dependancy relies on a machine learning model to detect the presence and location of the QR code.