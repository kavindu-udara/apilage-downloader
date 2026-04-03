# අපිලගෙ ඩවුන්ලෝඩරය

Apilage Downloader is a small desktop app for fetching YouTube video details and downloading a video at a selected quality. The project currently includes a Tkinter GUI, a simple CLI downloader module, and a GitHub Actions workflow that builds release executables for Windows, macOS, and Linux.

## Features

- Fetch video metadata before downloading
- Fetch playlist metadata before downloading
- Select from available quality presets based on the video formats returned by `yt-dlp`
- Choose the output directory before starting the download
- Download either a single video or an entire playlist from the GUI
- Desktop GUI built with Tkinter
- Cross-platform executable builds through GitHub Actions

## Project Structure

```text
.
├── main.py
├── gui.py
├── cli/
│   └── downloader.py
├── controllers/
│   └── video_controller.py
├── models/
├── assets/
└── .github/workflows/build-release.yml
```

## Requirements

- Python 3.12 or newer for local development
- `uv` recommended for environment and dependency management
- Internet access for `yt-dlp` to fetch video information and download media

## Local Setup

Install dependencies with `uv`:

```bash
uv venv
source .venv/bin/activate
uv sync
```

If you prefer `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install yt-dlp
```

## Run the App

Start the GUI application:

```bash
python main.py
```

## How to Use

1. Open the app.
2. Paste a YouTube video or playlist URL.
3. Enable the `Playlist` checkbox if the URL is a playlist.
4. Click `Fetch video`.
5. Review the fetched metadata.
6. Select a quality.
7. Choose a save folder.
8. Click `Download` or `Download Playlist`.

## Build an Executable Locally

Install PyInstaller:

```bash
uv pip install pyinstaller
```

Build for your current platform:

```bash
uv run pyinstaller --onefile --windowed --name "Apilage Downloader" main.py
```

Platform-specific icons used by the release workflow:

- Windows: `assets/icon.ico`
- macOS: `assets/icon.icns`
- Linux: no native executable icon is applied in the current workflow

The built files are written to `dist/`.

## GitHub Releases

You can download the release assets from the repository Releases page.

## Notes

- The downloader depends on `yt-dlp`, so download behavior can change if YouTube changes its platform behavior.
- The repository also contains an older CLI-oriented downloader implementation in `cli/downloader.py`.

