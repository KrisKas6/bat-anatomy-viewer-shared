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
SpikeGLX `.imro` / AP `.meta`, Trodes `.trodesconf`, Kilosort `chanMap.json` or
ProbeInterface `probegroup.json`, or choose **Use NPX 2.0 routing**.
Enter channel IDs/ranges, click or drag across the map, or select a depth
interval in µm from the tip or entry. Assign sites to named color groups.
Choose the correct numbering convention and shank; hardware IDs and saved
indices can differ. Maps without a physical tip offset need confirmation
under **Tip calibration & map conventions** before atlas placement.

Selected sites follow probe rotation and appear in the nearest coronal
section. The editor stays open while you use the 3D view and atlas. Drag its
title to move it or its bottom corner to resize it. Map selections update live
while dragging. Enable **Live depth range** to replace the current group as
you adjust depth limits or the shank filter; disable it to combine ranges.
Save the map and selections with the plan JSON, or export selected
channels as CSV. **Include probe trajectories** in video export includes the
enabled recording-site colors and group legend. Channel maps are read locally.

NP2013/NP2014 (four shanks) and NP2003/NP2004 (one shank) use the routing rules
from [Bill Karsh's SpikeGLX](https://github.com/billkarsh/SpikeGLX/tree/efac8da3625724c703996cd3e409059968e9ac16/Src-imro).
Hardware mode prevents different sites sharing an AP channel, across all banks,
shanks and color groups. Dragging skips forbidden sites; conflicting ID/depth
selections are rejected. Unidentified maps and older spatial plans are labeled
unverified or not enforced.

**Hardware-compatible patterns** offers complete 384-channel configurations:
one shank, supported shank pairs, four shanks at the same depth, or diagonal
patterns. Only valid depths appear on the slider. **Move this preset live**
updates the views while moving it. Applying a preset replaces all color groups.
Export a complete configuration as `.imro` and load it in SpikeGLX to apply it.
Imported references are retained; new templates use external reference.
Single-shank combined-bank acquisition is not modeled. The SpikeGLX copyright
and redistribution notice is embedded in the viewer.

## Resize panels and zoom the atlas

Drag the dividers between the controls, 3D view, atlas and section timeline.
Panel sizes are remembered; **Reset panels** restores them. Double-click a
divider to reset it, or focus it and use arrow keys / Home. The histology
window's panels also have dividers. On phones, panels stack vertically.

Use **+ / − / Fit** or the wheel in the atlas panel to zoom, and drag to pan.
Drag the image viewport's bottom corner to change its height. Region boundaries
and channel markers remain aligned, and trajectory picking works at any zoom.

## Hover, zoom and undo channel selections

Hover an electrode in **Select channels** to see its cyan point on the atlas,
including electrodes not yet selected. The atlas follows the nearest section;
uncheck **Follow hovered electrode in atlas** to keep the current page. The
readout shows channel IDs, coordinates and the AP distance to that section.

Wheel or **+/−** zooms the shank map. **Individual electrodes** shows separate
contacts with electrode IDs; focus one shank under **Shanks in map** to see AP
channel labels too. Right-drag, Shift+wheel or arrow keys pan along the probe;
**Fit map** or **0** restores the overview.

Use **Undo/Redo**, **Ctrl+Z / Ctrl+Shift+Z** (Cmd on Mac), or **Ctrl+Y** to reverse
up to 40 channel edits. Each drag or live slider gesture is one edit. Undo
pauses live depth and preset movement. Text fields retain normal text undo;
use the buttons to undo a selection while typing. History lasts for this
session and covers channel edits, not trajectory movement.

## Align histology in a separate window

Click **Histology alignment ↗** and allow its window if your browser blocks
pop-ups. Import JPEG/PNG slides (use an exported image for CZI/TIFF), duplicate
entries or split a slide into a grid, and crop each section independently.
Enter an approximate **printed atlas-page range** and optional slice spacing.
The displayed page stays provisional until you explicitly confirm it.

Move, rotate, flip and scale the overlay. For partial sections, place paired
landmarks on the available tissue and fit them. Image-based refinement offers
a nearby candidate to preview and accept/discard; it does not determine the
exact atlas page. Save a project to retain working images, crops, ranges,
spacing, transforms and landmarks. PNG overlay and landmark CSV exports are
also available. The atlas covers the right hemisphere; crop the matching
hemisphere from a bilateral section.

Images are processed locally. Original scans remain unchanged. Save the
project before reloading or locking BatBrain; locking closes the alignment
window. Closing only the alignment window retains it in the current session.

### Bat projects, freehand crops and probe reconstruction

Enter the **Bat ID**, and a **Section ID** and **Area name** for each slice.
Use **Freehand crop** to outline tissue. **Outline dye region** draws a closed
region around dye (such as DiI); **Trace probe dye** draws an open track. Draw
on either image. Crops and markings remain attached to the slice through its
alignment, and Undo/Redo restores edits.

Use the same **Probe ID** on different slices for one track. Different probe
IDs remain separate. Once a slice is aligned, confirm its exact atlas page and
click **Register slice to this bat**. **Show registered slices in 3D** adds the
registered images to the main atlas and connects region centers (trace
midpoints) in AP order. Opacity and per-slice visibility controls are in the
main window. Connections interpolate between observations; duplicate markings
at one page interrupt a connection. Uncertain or unreviewed slices stay pending.

Named bat projects autosave in this browser when storage is available. Open
them from **Saved on this computer**. Download **Save bat project (JSON)** for
backup or another computer: it includes working images, freehand crops, dye
markings, bat/section identities and registrations. Browser storage can be
cleared and is specific to the browser/address. Check the save status; if local
saving is unavailable, download JSON. Export probe-center coordinates as CSV
to retain probe IDs, area names, pages and review flags alongside coordinates.

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
