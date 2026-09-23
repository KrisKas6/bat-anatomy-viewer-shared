# Bat anatomy explorer — offline, shared-key edition

**Current download: v1.4.0, with recording-channel selection, color groups and video overlays.**

Explore **presubiculum (PrS), parasubiculum (PaS), medial and lateral entorhinal
cortex (mEC/lEC), subiculum, and Hpc** in the Egyptian fruit bat atlas.

Use the **BatBrain app package** for anatomy, trajectory planning and saving
videos on your computer. No GitHub account or private repository access is
needed. The separate HTML download provides viewing and video previews.

**The access key is shared separately and is not in this repository.**

## Install BatBrain to save videos

Download **[batbrain_shared_app.zip](https://github.com/KrisKas6/bat-anatomy-viewer-shared/releases/latest/download/batbrain_shared_app.zip)**
and extract the entire ZIP. Install Python 3.9 or newer if needed, then open
a terminal in the extracted folder and run:

**Windows:**
```powershell
py -3 scripts/install_batbrain.py --open
```

**macOS or Linux:**
```bash
python3 scripts/install_batbrain.py --open
```

The installer includes the video save service and automatically sets up
FFmpeg. Initial encoder setup needs internet; the installed app works offline.
It uses your user account without administrator privileges. Enter your existing
shared key when the browser opens, choose **Generate video**, select MP4 or MOV,
and paste a folder path or click **Browse…**. Keep the tab visible while recording.

Open a new terminal and run `batbrain`. The installer registers the command
in your Windows user PATH or macOS/Linux shell startup files. Pass `--no-path`
to leave those unchanged. You can also launch directly:

| Operating system | Command |
| --- | --- |
| Windows PowerShell | `& "$env:USERPROFILE\.local\bin\batbrain.cmd"` |
| macOS or Linux | `python3 "$HOME/.local/bin/batbrain"` |

The launcher always prints a clickable/copyable browser link. If the browser
does not open automatically, open that link. Browse uses the native Windows or
macOS folder picker, and Zenity or Python Tk on Linux. You can always paste the
folder path, including quoted paths copied from Windows Explorer. An existing FFmpeg encoder can be supplied
with `--ffmpeg /path/to/ffmpeg` for offline installation.

Automatic encoder setup supports Windows x86/x64, Windows 11 ARM64 through
x64 app support, macOS Intel/Apple Silicon, and Linux x64/ARM64.
The complete installed workflow is tested in Chrome on Linux;
Windows and macOS have not been tested natively. Full package instructions:
[APP_README.md](APP_README.md).

## Viewer-only HTML download

For viewing without installation, download **bat_anatomy_viewer_locked.html** from the
[latest release](https://github.com/KrisKas6/bat-anatomy-viewer-shared/releases/latest)
and double-click it. Open it with a current Chrome, Edge, Firefox, or Safari.
Enter the shared key. After downloading, the viewer works with the network off.
This file alone supports video previews; install the app above to save videos.

Alternatively, with [Git](https://git-scm.com/downloads) installed, run:

```bash
git clone --depth 1 https://github.com/KrisKas6/bat-anatomy-viewer-shared.git
cd bat-anatomy-viewer-shared
```

To install from the clone, run the installation command above. For viewing only,
open the HTML using the command for your operating system:

| Operating system | Command |
| --- | --- |
| Linux desktop | `xdg-open bat_anatomy_viewer_locked.html` |
| macOS | `open bat_anatomy_viewer_locked.html` |
| Windows PowerShell | `Start-Process .\bat_anatomy_viewer_locked.html` |

If HTML files open in a text editor, right-click the file and choose **Open
with** your browser. Keep the file somewhere convenient and open the same
file next time. You will need the shared key each time you open it.

The download is approximately 52 MB and contains all atlas images, filled
region profiles, 3D meshes, and the renderer. A current browser with WebGL
enabled is required. The offline workflow was tested in Chrome on Linux;
Windows and macOS were not available for native testing.

## Use the viewer

- Drag to rotate, scroll to zoom, and right-drag or shift-drag to pan.
- Select PrS or PaS and adjust visibility or opacity to inspect adjacent regions.
- Move the coronal section slider to compare filled regions with the atlas.
- Open the original atlas image or enlarge the region boundary overlay.
- Export a surface as OBJ, region contours as JSON, or the current view as PNG.
- Click **NP trajectory** in the top toolbar after unlocking. Set entry and
  target coordinates, or pick them on an atlas section.
- Select **NPX 2.0 · 4 shanks** for ML/AP shank orientation, additional roll,
  and an optional green PCB probe body. **Fit whole probe** shows its full extent.
- Under **Recording channels**, click **Select channels** to import SpikeGLX AP
  `.meta`, Trodes `.trodesconf`, Kilosort `chanMap.json`, or ProbeInterface
  `probegroup.json`. A physical-site template is also available. Enter IDs or
  ranges, click/drag on the map, or select a depth interval from the tip or entry.
  Assign sites to named color groups; selections rotate with the probe and
  appear in videos when trajectories are included. Maps without a physical tip
  offset require confirmation under **Tip calibration & map conventions**.
- Save/load trajectory plans and channel selections as JSON. Export section
  crossings or selected channels, depths and coordinates as CSV.
- Expand **EC** to select **mEC** and **lEC** separately.
- Click **Lock viewer** to close the atlas and return to the key prompt.

Anatomy and trajectory planning work offline. **Generate video** includes
previews for regions, probes, the brain outline, and a coronal atlas page with
adjustable transparency. **Brain focus (crop PCB)** is the default video framing:
it keeps the selected anatomy and planned tracks in view while allowing the
upper green PCB to extend outside the frame. **Fit whole probe** shows the
entire body with a wider view. The public app installer supplies the local
save service and encoder needed for MP4/MOV folder saving. Open its local
browser link and unlock the viewer to export videos.

Links to the paper and publisher websites
require internet if you choose to open them.

These are **draft atlas-derived segmentations**, with interpreted boundaries
and interpolation between traced sections. They are not the paper authors'
original meshes. Review the evidence and methods inside the viewer before
using the reconstruction for quantitative work.

Scientific sources: [Jacobsen et al., 2023](https://doi.org/10.1002/hipo.23517)
and the [Egyptian fruit bat atlas](https://shop.elsevier.com/books/book-companion/9780128192979).
Source attribution and the bundled renderer's license are included in the viewer.

## Sharing and updates

Send this repository link to users and give them the key separately. The atlas
and viewer contents are encrypted; the key is needed to decrypt them locally.
Anyone with the key can unlock, export, and share the contents. A downloaded
offline copy cannot be remotely revoked.

For a clone, download updates while online with:

```bash
git pull --ff-only
```

For an installed app, extract the latest app ZIP and rerun the installer.
For a viewer-only download, replace your HTML file with the newer release file.
If a later release uses a new key, ask the person who shared it for that key.
`SHA256SUMS.txt` contains the download checksum.

## Updating with an assistant or coding agent

This public repository contains the **encrypted viewer and Python installation
utilities**. Searching the locked HTML for
planner source code will not find the decrypted application. Open the file
in a browser and unlock it to verify **NP trajectory** is present.

Pull this repository's `main` branch or download the v1.4.0 app ZIP, then run
`python3 scripts/install_batbrain.py --open` (Windows: `py -3` in place of
`python3`). The installer includes the local save service and automatically
installs FFmpeg. Your existing key still works. End users do not need the
private source repository for installation or video export.

## Platform verification

`python scripts/verify_platforms.py` checks a fresh installation, automatic
encoder download, offline reinstall, terminal PATH registration, concurrent
launches, local API access controls, and real MP4/MOV conversion. It includes
Unicode folder/filename tests and checks picker commands and cancellation.
Folder-picker UI responses are mocked; the installer, launcher, API and encoder
run on the actual operating system running the test. No unlock key is needed.

`platform-checks.yml` is a prepared GitHub Actions matrix for Windows, macOS
and Linux, each on x64 and ARM64. To enable it, place the file at
`.github/workflows/platform-checks.yml` using a GitHub login with `workflow`
permission. Native Windows/macOS test runs remain pending until that workflow
is enabled. Linux installation, browser export and all picker command paths
have been checked locally.
