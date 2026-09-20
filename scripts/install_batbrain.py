#!/usr/bin/env python3
"""Install BatBrain for the current user, without administrator privileges."""

from pathlib import Path
import argparse
import os
import shlex
import shutil
import subprocess
import sys


def configure_command_path(bin_dir):
    """Register this user's command directory for new terminal sessions."""
    directory = str(bin_dir)
    if os.name == 'nt':
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
            try:
                current, kind = winreg.QueryValueEx(key, 'Path')
            except FileNotFoundError:
                current, kind = '', winreg.REG_EXPAND_SZ
            entries = [os.path.normcase(os.path.expandvars(p.strip('"'))) for p in current.split(';')]
            if os.path.normcase(directory) not in entries:
                winreg.SetValueEx(key, 'Path', 0, kind, current.rstrip(';') + (';' if current else '') + directory)
        # Inform Explorer so new terminals inherit the updated user PATH.
        import ctypes
        from ctypes import wintypes
        result = ctypes.c_size_t()
        send = ctypes.windll.user32.SendMessageTimeoutW
        send.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPCWSTR,
                         wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t)]
        send.restype = ctypes.c_ssize_t
        send(0xffff, 0x1a, 0, 'Environment', 2, 1000, ctypes.byref(result))
    else:
        shell = Path(os.environ.get('SHELL', '')).name
        if shell == 'fish':
            files = [Path.home() / '.config/fish/conf.d/batbrain.fish']
            command = 'fish_add_path -- ' + shlex.quote(directory)
        else:
            files = ([Path.home()/'.zprofile', Path.home()/'.zshrc'] if shell == 'zsh' or sys.platform == 'darwin'
                     else [Path.home()/'.profile', Path.home()/'.bashrc'])
            command = 'export PATH=' + shlex.quote(directory) + ':"$PATH"'
        block = '\n# BatBrain command\n' + command + '\n'
        for file in files:
            previous = file.read_bytes() if file.exists() else b''
            if command.encode('utf-8') not in previous:
                file.parent.mkdir(parents=True, exist_ok=True)
                with file.open('ab') as output:
                    output.write(block.encode('utf-8'))
    if directory not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = directory + os.pathsep + os.environ.get('PATH', '')


def install(ffmpeg=None, with_ffmpeg=False, configure_path=True):
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
        # UTF-8 and disabled delayed expansion preserve non-ASCII paths and '!'.
        executable = sys.executable.replace('%', '%%')
        command = ('@echo off\nsetlocal DisableDelayedExpansion\nchcp 65001 >nul\n'
                   f'"{executable}" "%~dp0batbrain" %*\n')
        (bin_dir / 'batbrain.cmd').write_bytes(command.replace('\n', '\r\n').encode('utf-8'))
    if configure_path:
        configure_command_path(bin_dir)
    print(f"Installed command: {bin_dir / 'batbrain'}")
    print(f"Installed viewer: {data_dir / 'index.html'}")
    print("Run: batbrain (open a new terminal after first installation)")
    if str(bin_dir) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"Add {bin_dir} to your shell's PATH to run batbrain by name.")
    return bin_dir / 'batbrain'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', help='copy a standalone FFmpeg executable for offline MP4/MOV export')
    parser.add_argument('--with-ffmpeg', action='store_true', help='automatically install the video encoder (default for public packages)')
    parser.add_argument('--open', action='store_true', help='open BatBrain after installation')
    parser.add_argument('--no-path', action='store_true', help='leave shell profiles and the Windows user PATH unchanged')
    args = parser.parse_args()
    try:
        installed_launcher = install(args.ffmpeg, args.with_ffmpeg, configure_path=not args.no_path)
        if args.open:
            subprocess.run([sys.executable, str(installed_launcher)], check=True)
    except (OSError, RuntimeError) as error:
        parser.exit(1, f'BatBrain installation failed: {error}\n')
