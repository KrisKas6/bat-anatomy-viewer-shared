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

## Select recording channels

Open **NP trajectory → Recording channels → Select channels**. Import a
SpikeGLX AP `.meta`, Trodes `.trodesconf`, Kilosort `chanMap.json` or
ProbeInterface `probegroup.json`, or use the NP2014 physical-site template.
Enter channel IDs/ranges, click or drag across the map, or select a depth
interval in µm from the tip or entry. Assign sites to named color groups.
Choose the correct numbering convention and shank; hardware IDs and saved
indices can differ. Maps without a physical tip offset need confirmation
under **Tip calibration & map conventions** before atlas placement.

Selected sites follow probe rotation and appear in the nearest coronal
section. Save the map and selections with the plan JSON, or export selected
channels as CSV. **Include probe trajectories** in video export includes the
enabled recording-site colors and group legend. Channel maps are read locally.

## Open it again

Open a new terminal and run `batbrain`. The installer adds the command to your
Windows user PATH or your shell startup files on macOS/Linux. Use `--no-path`
during installation to leave that configuration unchanged. You can also run
the installed launcher directly:

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

Automatic encoder setup supports Windows x86/x64 and Windows 11 ARM64
(using its x64 app support), macOS Intel/Apple Silicon, and Linux x64/ARM64.
Python and a current browser with WebGL are required;
Chrome or Edge is recommended for video recording. The complete workflow is
tested on Linux with Chrome. Windows and macOS have not been tested natively.
Browse uses the native Windows or macOS folder picker. Linux uses Zenity or
Python Tk; if neither is available, paste a folder path instead. Quoted paths
copied from Windows Explorer and folder names with spaces or non-English
characters are supported. The encoder download is standalone, so it does not
depend on relocating a system FFmpeg installation or its shared libraries.

The encoder is downloaded from the official, checksum-pinned
[imageio-ffmpeg 0.6.0 wheels](https://pypi.org/project/imageio-ffmpeg/0.6.0/).
Encoder notices are kept with the installation. No atlas data, videos, or
unlock key are uploaded by the app.

Download updates: https://github.com/KrisKas6/bat-anatomy-viewer-shared/releases/latest
