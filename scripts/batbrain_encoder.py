"""Install a verified FFmpeg executable without pip or administrator privileges."""
import hashlib
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
from urllib.request import urlopen
import zipfile

# Official imageio-ffmpeg 0.6.0 wheels from PyPI, pinned by SHA-256.
# https://pypi.org/project/imageio-ffmpeg/0.6.0/
WHEELS = {
    ('Linux', 'x86_64'): ('a0/2d/43c8522a2038e9d0e7dbdf3a61195ecc31ca576fb1527a528c877e87d973', 'manylinux2014_x86_64', 'c7e46fcec401dd990405049d2e2f475e2b397779df2519b544b8aab515195282'),
    ('Linux', 'arm64'): ('33/e7/1925bfbc563c39c1d2e82501d8372734a5c725e53ac3b31b4c2d081e895b', 'manylinux2014_aarch64', '1d47bebd83d2c5fc770720d211855f208af8a596c82d17730aa51e815cdee6dc'),
    ('Darwin', 'x86_64'): ('da/58/87ef68ac83f4c7690961bce288fd8e382bc5f1513860fc7f90a9c1c1c6bf', 'macosx_10_9_intel.macosx_10_9_x86_64', '9d2baaf867088508d4a3458e61eeb30e945c4ad8016025545f66c4b5aaef0a61'),
    ('Darwin', 'arm64'): ('40/5c/f3d8a657d362cc93b81aab8feda487317da5b5d31c0e1fdfd5e986e55d17', 'macosx_11_0_arm64', 'b1ae3173414b5fc5f538a726c4e48ea97edc0d2cdc11f103afee655c463fa742'),
    ('Windows', 'x86_64'): ('2c/c6/fa760e12a2483469e2bf5058c5faff664acf66cadb4df2ad6205b016a73d', 'win_amd64', '02fa47c83703c37df6bfe4896aab339013f62bf02c5ebf2dce6da56af04ffc0a'),
    ('Windows', 'x86'): ('a0/13/59da54728351883c3c1d9fca1710ab8eee82c7beba585df8f25ca925f08f', 'win32', '196faa79366b4a82f95c0f4053191d2013f4714a715780f0ad2a68ff37483cc2'),
}


def wheel_for(system, machine):
    arch = {'amd64': 'x86_64', 'aarch64': 'arm64', 'i386': 'x86', 'i686': 'x86'}.get(machine.lower(), machine.lower())
    # Windows 11 on ARM runs this pinned x64 executable through OS emulation.
    if system == 'Windows' and arch == 'arm64':
        arch = 'x86_64'
    try:
        path, tag, digest = WHEELS[system, arch]
    except KeyError:
        raise RuntimeError(f'Automatic encoder setup is unavailable for {system} {machine}. Use --ffmpeg /path/to/ffmpeg.')
    return f'https://files.pythonhosted.org/packages/{path}/imageio_ffmpeg-0.6.0-py3-none-{tag}.whl', digest


def supports_h264(binary):
    try:
        result = subprocess.run([str(binary), '-hide_banner', '-encoders'], capture_output=True, timeout=15)
        return result.returncode == 0 and b'libx264 ' in result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return False


def ensure_encoder(data_dir):
    data_dir = Path(data_dir)
    target = data_dir / 'bin' / ('ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')
    if supports_h264(target):
        return target
    # Do not relocate a system FFmpeg: its shared-library paths may depend on
    # the original install location. These wheels contain standalone binaries.
    url, expected = wheel_for(platform.system(), platform.machine())
    print('Installing the video encoder (one-time download)…', flush=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='batbrain-encoder-') as temporary:
        wheel = Path(temporary) / 'encoder.whl'
        digest = hashlib.sha256()
        with urlopen(url, timeout=60) as incoming, wheel.open('wb') as output:
            while chunk := incoming.read(1024 * 1024):
                digest.update(chunk); output.write(chunk)
        if digest.hexdigest() != expected:
            raise RuntimeError('The encoder download failed its checksum. Run the installer again.')
        with zipfile.ZipFile(wheel) as archive:
            names = [name for name in archive.namelist() if name.startswith('imageio_ffmpeg/binaries/ffmpeg-')]
            if len(names) != 1:
                raise RuntimeError('The encoder package did not contain the expected executable.')
            binary = Path(temporary) / target.name
            with archive.open(names[0]) as source, binary.open('wb') as output:
                shutil.copyfileobj(source, output)
            binary.chmod(0o755)
            if not supports_h264(binary):
                raise RuntimeError('The downloaded encoder cannot run on this computer. Use --ffmpeg /path/to/ffmpeg.')
            notices = ['FFmpeg supplied by imageio-ffmpeg 0.6.0', url,
                       'Upstream and source/build information: https://github.com/imageio/imageio-ffmpeg',
                       'FFmpeg source and license: https://ffmpeg.org/\n']
            for name in archive.namelist():
                if 'license' in name.lower() and not name.endswith('/'):
                    notices.append(name + '\n' + archive.read(name).decode('utf-8', errors='replace'))
            temporary_target = target.with_name(target.name + '.installing')
            shutil.copyfile(binary, temporary_target)
            temporary_target.chmod(0o755)
            temporary_target.replace(target)
            (target.parent / 'encoder-notices.txt').write_text('\n\n'.join(notices), encoding='utf-8')
    return target
