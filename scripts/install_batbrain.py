#!/usr/bin/python3
"""Install BatBrain for the current user, without administrator privileges."""

from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys


def install(ffmpeg=None, with_ffmpeg=False):
    binary = Path(ffmpeg).expanduser().resolve() if ffmpeg else None
    if binary and (not binary.is_file() or not os.access(binary, os.X_OK)):
        raise SystemExit(f"FFmpeg executable not found: {binary}")
    source = Path(__file__).resolve().parent
    viewer = source.parent / "bat_anatomy_viewer.html"
    shared_viewer = source.parent / 'bat_anatomy_viewer_locked.html'
    shared = shared_viewer.is_file() and not (source.parent / 'data/region_atlas.js').is_file()
    if shared:
        viewer = shared_viewer
    launcher = source / "batbrain"
    backend = source / "batbrain_video.py"
    # A Git checkout has the full atlas sources; its ignored HTML may be absent
    # or left over from before git pull. Release ZIPs instead carry a ready bundle.
    if (source.parent / 'data/region_atlas.js').is_file():
        print('Building BatBrain from the current source…', flush=True)
        subprocess.run([sys.executable, str(source / 'build_standalone.py'), '--html-only'], check=True)
    if not viewer.is_file() or not launcher.is_file() or not backend.is_file():
        raise SystemExit("Use a complete Git checkout or extract the portable release ZIP before installing BatBrain.")
    data_dir = Path.home() / ".local/share/batbrain"
    bin_dir = Path.home() / ".local/bin"
    for directory in (data_dir, bin_dir):
        directory.mkdir(parents=True, exist_ok=True)
    if (with_ffmpeg or shared) and not binary:
        # The public edition includes video setup by default. No private repo access.
        import importlib.util
        spec = importlib.util.spec_from_file_location('batbrain_encoder', source / 'batbrain_encoder.py')
        encoder = importlib.util.module_from_spec(spec); spec.loader.exec_module(encoder)
        binary = encoder.ensure_encoder(data_dir)
    for source_file, target, mode in (
        (viewer, data_dir / "index.html", 0o644),
        (launcher, bin_dir / "batbrain", 0o755),
        (backend, data_dir / "batbrain_video.py", 0o644),
    ):
        temporary = target.with_name(target.name + ".installing")
        shutil.copyfile(source_file, temporary)
        temporary.chmod(mode)
        temporary.replace(target)
    if binary:
        encoder_dir = data_dir / 'bin'
        encoder_dir.mkdir(exist_ok=True)
        target_encoder = encoder_dir / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
        if binary.resolve() != target_encoder.resolve():
            temporary = target_encoder.with_name(target_encoder.name + '.installing')
            shutil.copyfile(binary, temporary)
            temporary.chmod(0o755)
            temporary.replace(target_encoder)
        print(f"Installed video encoder: {target_encoder}")
    if os.name == 'nt':
        (bin_dir / 'batbrain.cmd').write_text(f'@echo off\n"{sys.executable}" "{bin_dir / "batbrain"}" %*\n')
    print(f"Installed command: {bin_dir / 'batbrain'}")
    print(f"Installed viewer: {data_dir / 'index.html'}")
    print("Run: batbrain")
    if str(bin_dir) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"Add {bin_dir} to your shell's PATH to run batbrain by name.")
    return bin_dir / 'batbrain'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', help='copy a standalone FFmpeg executable for offline MP4/MOV export')
    parser.add_argument('--with-ffmpeg', action='store_true', help='automatically install the video encoder (default for public packages)')
    parser.add_argument('--open', action='store_true', help='open BatBrain after installation')
    args = parser.parse_args()
    try:
        installed_launcher = install(args.ffmpeg, args.with_ffmpeg)
        if args.open:
            subprocess.run([sys.executable, str(installed_launcher)], check=True)
    except (OSError, RuntimeError) as error:
        parser.exit(1, f'BatBrain installation failed: {error}\n')
