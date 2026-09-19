# Bat anatomy explorer — offline, shared-key edition

**Current download: v1.1.1 (September 18, 2026), with larger brain framing in probe videos.**

Explore **presubiculum (PrS), parasubiculum (PaS), medial and lateral entorhinal
cortex (mEC/lEC), subiculum, and Hpc** in the Egyptian fruit bat atlas.

Works on **Linux, Windows, and macOS** in a current desktop browser. Download
once, open the HTML file, and enter the access key supplied by the person who
shared this viewer. No account, Python, installation, or local server is
needed to run it. Internet is only needed for the initial download or updates.

**The access key is shared separately and is not in this repository.**

## Download and open

The easiest option is to download **bat_anatomy_viewer_locked.html** from the
[latest release](https://github.com/KrisKas6/bat-anatomy-viewer-shared/releases/latest)
and double-click it. Open it with a current Chrome, Edge, Firefox, or Safari.
Enter the shared key. After downloading, the viewer works with the network off.

Alternatively, with [Git](https://git-scm.com/downloads) installed, run:

```bash
git clone --depth 1 https://github.com/KrisKas6/bat-anatomy-viewer-shared.git
cd bat-anatomy-viewer-shared
```

Then open it using the command for your operating system:

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
- Save/load trajectory plans as JSON and export section crossings as CSV.
- Expand **EC** to select **mEC** and **lEC** separately.
- Click **Lock viewer** to close the atlas and return to the key prompt.

Anatomy and trajectory planning work offline. **Generate video** includes
previews for regions, probes, the brain outline, and a coronal atlas page with
adjustable transparency. **Brain focus (crop PCB)** is the default video framing:
it keeps the selected anatomy and planned tracks in view while allowing the
upper green PCB to extend outside the frame. **Fit whole probe** shows the
entire body with a wider view. Saving MP4/MOV files to a folder requires the local
BatBrain app and FFmpeg; this encrypted HTML download does not install that
save service. Repository owners can install it from the private source/release
using their authorized GitHub account.

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

For a release download, replace your HTML file with the newer release file.
If a later release uses a new key, ask the person who shared it for that key.
`SHA256SUMS.txt` contains the download checksum.

## Updating with an assistant or coding agent

This public repository contains the **encrypted download**, not separate
JavaScript source files or a Python installer. Searching the locked HTML for
planner source code will not find the decrypted application. Open the file
in a browser and unlock it to verify **NP trajectory** is present.

Pull this repository's `main` branch or download the v1.1.1 release, replace
any older local copy, and reopen it in the browser. Your existing shared key
still works. The separate `KrisKas6/bat-anatomy-viewer` source repository is
private and requires GitHub authentication with access to that repository.
