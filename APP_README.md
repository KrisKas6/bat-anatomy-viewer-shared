# BatBrain — shared app with video saving

This package includes the encrypted viewer, the BatBrain launcher, and MP4/MOV
folder saving. It does not require access to a private GitHub repository.
Your existing shared key unlocks the viewer. The key is supplied separately.

## Install BatBrain to save videos

1. Install Python 3.9 or newer if it is not already installed.
2. Extract the entire ZIP into a folder on your computer.
3. Open a terminal in that folder and run:

   **Windows:**
   ```powershell
   py -3 scripts/install_batbrain.py --open
   ```

   **macOS or Linux:**
   ```bash
   python3 scripts/install_batbrain.py --open
   ```

The installer automatically installs a compatible FFmpeg encoder. Initial
encoder setup needs internet; subsequent use works offline. It installs in
your user account without administrator privileges. If an encoder is already
installed, it is reused. For a fully offline installation, pass
`--ffmpeg /path/to/ffmpeg` (or the Windows `ffmpeg.exe` path).

The installer opens the app and prints its local browser link. Enter your
shared key, choose **Generate video**, select the regions and optional probe,
choose MP4 or MOV, and paste a save-folder path or click **Browse…**.
The selected folder must already exist. Keep the tab visible while recording.

## Open it again

Run `batbrain` if your user's `.local/bin` directory is on PATH. Otherwise:

**Windows:**
```powershell
& "$env:USERPROFILE\.local\bin\batbrain.cmd"
```

**macOS or Linux:**
```bash
python3 "$HOME/.local/bin/batbrain"
```

If the browser does not open automatically, click or copy the printed link.
Opening `bat_anatomy_viewer_locked.html` directly provides the offline viewer
and video preview. Use the installed app's local link for video saving.

## Updates and platform support

Download the latest app ZIP, extract it and rerun the installer. This updates
the encrypted viewer and launcher without changing your shared key.

Automatic encoder setup supports Windows x86/x64, macOS Intel/Apple Silicon,
and Linux x64/ARM64. Python and a current browser with WebGL are required;
Chrome or Edge is recommended for video recording. The complete workflow is
tested on Linux with Chrome. Windows and macOS have not been tested natively.
Browse uses Zenity on Linux or Python's Tk folder picker; if neither is
available, paste a folder path instead.

The encoder is downloaded from the official, checksum-pinned
[imageio-ffmpeg 0.6.0 wheels](https://pypi.org/project/imageio-ffmpeg/0.6.0/).
Encoder notices are kept with the installation. No atlas data, videos, or
unlock key are uploaded by the app.

Download updates: https://github.com/KrisKas6/bat-anatomy-viewer-shared/releases/latest
