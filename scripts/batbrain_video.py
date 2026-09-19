"""Local folder selection and H.264 MP4/MOV export for the BatBrain server."""
import json
import importlib.util
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time


class VideoService:
    MAX_UPLOAD = 128 * 1024 * 1024

    def __init__(self, data_dir, cache_dir):
        self.data_dir, self.cache_dir = Path(data_dir), Path(cache_dir)
        self.token = secrets.token_urlsafe(32)
        self.jobs = {}
        self.lock = threading.Lock()
        self.browse_lock = threading.Lock()
        self.encoder_lock = threading.Lock()

    def ffmpeg(self):
        candidates = [self.data_dir / ('bin/ffmpeg.exe' if os.name == 'nt' else 'bin/ffmpeg'), os.environ.get('BATBRAIN_FFMPEG'), shutil.which('ffmpeg')]
        return next((str(p) for p in candidates if p and Path(p).is_file() and os.access(p, os.X_OK)), None)

    def default_folder(self):
        try:
            saved = json.loads((self.cache_dir / 'video-preferences.json').read_text())['folder']
            if Path(saved).is_dir():
                return saved
        except (OSError, ValueError, KeyError, TypeError):
            pass
        return str(next((p for p in [Path.home() / 'Videos', Path.home() / 'Downloads'] if p.is_dir()), Path.home()))

    def config(self):
        return {'version': 1, 'token': self.token, 'folder': self.default_folder(),
                'ready': bool(self.ffmpeg()), 'browse': bool(shutil.which('zenity') or importlib.util.find_spec('tkinter')),
                'formats': ['mp4', 'mov']}

    @staticmethod
    def folder(raw):
        if not isinstance(raw, str) or not raw.strip() or '\x00' in raw:
            raise ValueError('Enter a save-folder path.')
        path = Path(raw.strip()).expanduser()
        if not path.is_absolute():
            raise ValueError('Enter an absolute folder path, or a path starting with ~/.')
        path = path.resolve()
        if not path.is_dir():
            raise ValueError('That folder does not exist. Choose an existing folder.')
        return path

    def browse(self, raw):
        chooser = shutil.which('zenity')
        try:
            initial = self.folder(raw or self.default_folder())
        except ValueError:
            initial = self.folder(self.default_folder())
        if not self.browse_lock.acquire(blocking=False):
            raise ValueError('A folder browser is already open.')
        try:
            if chooser:
                command = [chooser, '--file-selection', '--directory',
                           '--title=Choose a folder for the BatBrain video', '--filename=' + str(initial) + '/']
            else:
                # Run Tk in its own main thread/process, including on Windows/macOS.
                command = [sys.executable, '-c',
                           'import sys, tkinter as tk; from tkinter import filedialog; '
                           'root=tk.Tk(); root.withdraw(); '
                           'print(filedialog.askdirectory(title="Choose a folder for the BatBrain video", initialdir=sys.argv[1])); root.destroy()', str(initial)]
            result = subprocess.run(command,
                                    stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=180)
            if (chooser and result.returncode == 1) or (result.returncode == 0 and not result.stdout.strip()):
                return {'cancelled': True}
            if result.returncode != 0:
                raise ValueError('The folder browser could not open. Paste the folder path instead.')
            return {'folder': str(self.folder(result.stdout.strip()))}
        finally:
            self.browse_lock.release()

    def prepare(self, data):
        if not self.ffmpeg():
            raise ValueError('Video encoding is unavailable. Install FFmpeg or reinstall BatBrain with --ffmpeg /path/to/ffmpeg.')
        folder = self.folder(data.get('folder'))
        format_ = data.get('format')
        if format_ not in ('mp4', 'mov'):
            raise ValueError('Choose MP4 or MOV.')
        name = data.get('name', '')
        if not isinstance(name, str):
            raise ValueError('Enter a video filename.')
        name = name.strip()
        if name.lower().endswith(('.mp4', '.mov')):
            name = name[:-4]
        if not name or name in ('.', '..') or len(name) > 120 or any(c in '/\\' or ord(c) < 32 for c in name):
            raise ValueError('Use a filename of 1–120 characters without slashes.')
        # Fail before recording starts if the requested destination is not writable.
        with tempfile.TemporaryFile(dir=folder):
            pass
        now, job_id = time.monotonic(), secrets.token_urlsafe(24)
        with self.lock:
            self.jobs = {k: v for k, v in self.jobs.items() if v['busy'] or now - v['created'] < 1800}
            if len(self.jobs) >= 16:
                raise ValueError('Too many pending video exports. Finish or cancel an existing export.')
            self.jobs[job_id] = {'folder': folder, 'name': name, 'format': format_, 'created': now, 'busy': False}
        return {'job': job_id, 'folder': str(folder), 'filename': name + '.' + format_}

    def discard(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            if job and not job['busy']:
                del self.jobs[job_id]
        return {'cancelled': True}

    def save(self, job_id, stream, length, content_type):
        if not 0 < length <= self.MAX_UPLOAD:
            raise ValueError('Video upload must be smaller than 128 MB and cannot be empty.')
        if content_type.split(';')[0] not in ('video/webm', 'video/mp4'):
            raise ValueError('Unsupported recording format.')
        with self.lock:
            job = self.jobs.get(job_id)
            if not job or job['busy'] or time.monotonic() - job['created'] >= 1800:
                raise ValueError('This export expired or was already used. Generate the video again.')
            job['busy'] = True
        try:
            with tempfile.TemporaryDirectory(prefix='video-', dir=self.cache_dir) as work:
                incoming, encoded = Path(work) / 'recording', Path(work) / ('encoded.' + job['format'])
                with incoming.open('wb') as output:
                    remaining = length
                    while remaining:
                        chunk = stream.read(min(1024 * 1024, remaining))
                        if not chunk:
                            raise ValueError('The video upload was interrupted. Generate it again.')
                        output.write(chunk)
                        remaining -= len(chunk)
                with incoming.open('rb') as source:
                    header = source.read(12)
                if header.startswith(b'\x1a\x45\xdf\xa3'):
                    demuxer = 'matroska'
                elif len(header) >= 8 and header[4:8] == b'ftyp':
                    demuxer = 'mov'
                else:
                    raise ValueError('The browser returned an invalid video recording.')
                command = [self.ffmpeg(), '-nostdin', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                           '-f', demuxer, '-i', str(incoming), '-map', '0:v:0', '-an',
                           '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '18',
                           '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart',
                           '-f', job['format'], str(encoded)]
                with self.encoder_lock:
                    result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, timeout=180)
                if result.returncode or not encoded.is_file() or not encoded.stat().st_size:
                    (self.cache_dir / 'video-encoder.log').write_bytes(result.stderr[-16000:])
                    raise ValueError('Video conversion failed. The encoder details are in the BatBrain video-encoder.log file.')
                # Exclusive creation avoids overwriting a previous export, including on lab network drives.
                suffix = 1
                while True:
                    stem = job['name'] + (f'_{suffix}' if suffix > 1 else '')
                    destination = job['folder'] / (stem + '.' + job['format'])
                    try:
                        output = destination.open('xb')
                        break
                    except FileExistsError:
                        suffix += 1
                try:
                    with output, encoded.open('rb') as source:
                        shutil.copyfileobj(source, output)
                except BaseException:
                    destination.unlink(missing_ok=True)
                    raise
                preferences = self.cache_dir / 'video-preferences.json'
                try:
                    preferences.write_text(json.dumps({'folder': str(job['folder'])}))
                except OSError:
                    pass  # The video was saved even if a preference could not be stored.
                return {'saved': True, 'path': str(destination), 'filename': destination.name,
                        'bytes': destination.stat().st_size, 'format': job['format']}
        finally:
            with self.lock:
                self.jobs.pop(job_id, None)


def handle_video_request(handler, service):
    """Return True for an API route. Writes require same-origin access plus a per-server token."""
    if not handler.path.startswith('/api/video/'):
        return False

    def reply(status, data):
        body = json.dumps(data).encode()
        handler.send_response(status)
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Content-Length', str(len(body)))
        handler.send_header('Cache-Control', 'no-store')
        handler.send_header('X-Content-Type-Options', 'nosniff')
        handler.end_headers()
        handler.wfile.write(body)

    host = handler.headers.get('Host', '')
    port = handler.server.server_port
    origin = handler.headers.get('Origin')
    if (host not in (f'127.0.0.1:{port}', f'localhost:{port}') or
            (origin and origin != 'http://' + host) or handler.headers.get('Sec-Fetch-Site') == 'cross-site'):
        reply(403, {'error': 'Open BatBrain directly on this computer to export a video.'})
        return True
    try:
        if handler.command == 'GET' and handler.path == '/api/video/config':
            reply(200, service.config())
            return True
        if handler.command != 'POST' or not secrets.compare_digest(handler.headers.get('X-BatBrain-Token', ''), service.token):
            reply(403, {'error': 'Reload BatBrain before exporting a video.'})
            return True
        length = int(handler.headers.get('Content-Length', '0'))
        handler.connection.settimeout(45)
        if handler.path.startswith('/api/video/save/'):
            result = service.save(handler.path.rsplit('/', 1)[-1], handler.rfile, length, handler.headers.get('Content-Type', ''))
        else:
            if not 0 < length <= 8192:
                raise ValueError('Invalid video export request.')
            data = json.loads(handler.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Invalid video export settings.')
            if handler.path == '/api/video/browse':
                result = service.browse(data.get('folder'))
            elif handler.path == '/api/video/prepare':
                result = service.prepare(data)
            elif handler.path.startswith('/api/video/cancel/'):
                result = service.discard(handler.path.rsplit('/', 1)[-1])
            else:
                reply(404, {'error': 'Unknown video export action.'})
                return True
        reply(200, result)
    except subprocess.TimeoutExpired:
        reply(408, {'error': 'The operation timed out. Please try again.'})
    except (ValueError, OSError) as error:
        reply(400, {'error': str(error)})
    return True
