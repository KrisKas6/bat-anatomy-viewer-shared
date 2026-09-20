"""Native public-app install, launch and MP4/MOV API checks; no atlas key needed."""
import concurrent.futures
import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    loader = SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    result = importlib.util.module_from_spec(spec); loader.exec_module(result)
    return result


def main():
    report = {'system':platform.system(),'machine':platform.machine(),'python':platform.python_version()}
    with tempfile.TemporaryDirectory(prefix='batbrain-platform-') as temporary:
        scratch=Path(temporary); package=scratch/'public package'; home=scratch/'User José λ!'
        scripts=package/'scripts'; scripts.mkdir(parents=True)
        for name in ['batbrain','batbrain_video.py','batbrain_encoder.py','install_batbrain.py']:
            shutil.copyfile(ROOT/'scripts'/name,scripts/name)
        source=ROOT/'bat_anatomy_viewer_locked.html'
        if not source.exists(): source=ROOT/'sharing/dist/bat_anatomy_viewer_locked.html'
        shutil.copyfile(source,package/'bat_anatomy_viewer_locked.html')
        installer=module('platform_installer',scripts/'install_batbrain.py')
        original_path=os.environ.get('PATH','')
        # Only the scratch home is modified. Test registration twice for idempotency.
        registry_before=None
        if os.name=='nt':
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,'Environment') as key:
                try: registry_before=winreg.QueryValueEx(key,'Path')
                except FileNotFoundError: pass
        try:
            with patch.object(Path,'home',return_value=home):
                launcher=installer.install()
                encoder_path=home/'.local/share/batbrain/bin'/('ffmpeg.exe' if os.name=='nt' else 'ffmpeg')
                digest=hashlib.sha256(encoder_path.read_bytes()).hexdigest()
                with patch('urllib.request.urlopen',side_effect=AssertionError('Offline reinstall requested a download')):
                    installer.install()
                assert digest==hashlib.sha256(encoder_path.read_bytes()).hexdigest()
            bin_dir=home/'.local/bin'
            if os.name=='nt':
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment') as key:
                    entries=winreg.QueryValueEx(key,'Path')[0].split(';')
                    assert entries.count(str(bin_dir))==1, entries
            else:
                profiles=list(home.glob('.*rc'))+list(home.glob('.*profile'))+list(home.glob('.config/fish/conf.d/*.fish'))
                assert profiles
                for profile in profiles: assert profile.read_text(encoding='utf-8').count('# BatBrain command')==1
            report['fresh_install_encoder_and_offline_update']='passed'
            report['terminal_path_registration']='passed'
            data=home/'.local/share/batbrain';cache=home/'cache'
            env=dict(os.environ,XDG_CACHE_HOME=str(cache),PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
            def launch():
                if os.name=='nt':
                    # Resolve the installed command through PATH like cmd/PowerShell.
                    command=[os.environ.get('COMSPEC','cmd.exe'),'/d','/c','batbrain','--no-open']
                else:
                    command=['batbrain','--no-open']
                result=subprocess.run(command,env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
                assert result.returncode==0, (result.stdout,result.stderr)
                match=re.search(r'http://127\.0\.0\.1:\d+/',result.stdout)
                assert match,result.stdout
                return match[0]
            pid=None
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                    urls=list(pool.map(lambda _:launch(),range(3)))
                assert len(set(urls))==1,urls
                url=urls[0]
                state=json.loads((cache/'batbrain/server.json').read_text())
                pid=state['pid']
                http=build_opener(ProxyHandler({}))
                def api(path,body=None,token=None,content_type='application/json',origin=None):
                    headers={'Origin':origin or url.rstrip('/')}
                    if token:headers['X-BatBrain-Token']=token
                    if body is not None:
                        headers['Content-Type']=content_type
                        if not isinstance(body,bytes):body=json.dumps(body).encode()
                    with http.open(Request(url+path,body,headers),timeout=90) as response:
                        return json.load(response)
                config=api('api/video/config')
                assert config['ready'] and config['formats']==['mp4','mov']
                with http.open(url,timeout=10) as response:
                    assert hashlib.sha256(response.read()).hexdigest()==hashlib.sha256(source.read_bytes()).hexdigest()
                assert api('__batbrain_health')['server_version']==4
                report['concurrent_terminal_launch_and_local_service']='passed'
                destination=home/'Vidéos λ with spaces';destination.mkdir()
                sample=scratch/'sample.webm'
                subprocess.run([str(encoder_path),'-nostdin','-v','error','-f','lavfi','-i','testsrc2=size=320x240:rate=30',
                                '-t','1','-c:v','libvpx','-threads','2',str(sample)],check=True,timeout=30)
                token=config['token']
                for origin,auth in [('https://example.invalid',token),(url.rstrip('/'),None)]:
                    try:
                        api('api/video/prepare',{'folder':str(destination),'name':'blocked','format':'mp4'},token=auth,origin=origin)
                        raise AssertionError('Write protection was bypassed')
                    except HTTPError as error:assert error.code==403
                for format_ in ['mp4','mov']:
                    existing=destination/('rotation λ.'+format_);existing.write_bytes(b'preserve previous video')
                    prepared=api('api/video/prepare',{'folder':'"'+str(destination)+'"','name':'rotation λ','format':format_},token)
                    saved=api('api/video/save/'+prepared['job'],sample.read_bytes(),token,'video/webm')
                    output=Path(saved['path'])
                    assert output.name=='rotation λ_2.'+format_ and output.parent==destination and saved['bytes']>1000
                    assert existing.read_bytes()==b'preserve previous video'
                    decoded=subprocess.run([str(encoder_path),'-i',str(output),'-f','null','-'],capture_output=True,timeout=30)
                    assert decoded.returncode==0 and b'Video: h264' in decoded.stderr
                    assert (output.read_bytes()[8:12]==b'qt  ')==(format_=='mov')
                    report[format_]={'h264_decode':'passed','unicode_folder_and_filename':'passed','no_overwrite':'passed'}
                pending=api('api/video/prepare',{'folder':str(destination),'name':'cancelled','format':'mp4'},token)
                assert api('api/video/cancel/'+pending['job'],{},token)['cancelled']
                assert not (destination/'cancelled.mp4').exists()
                report['origin_token_checks_and_cancel']='passed'
                backend=module('platform_backend',data/'batbrain_video.py')
                service=backend.VideoService(data,cache)
                picker=service.picker()
                if sys.platform in ('win32','darwin'):assert picker==('windows' if sys.platform=='win32' else 'mac')
                # Verify native command arguments and Unicode output; no modal UI in CI.
                if picker:
                    with patch.object(backend.subprocess,'run') as run:
                        run.return_value=subprocess.CompletedProcess([],0,stdout=str(destination)+'\n',stderr='')
                        assert service.browse(str(destination))['folder']==str(destination)
                        args=run.call_args.args[0]
                        assert run.call_args.kwargs['encoding']=='utf-8'
                        if picker=='windows':
                            assert '-STA' in args and 'FolderBrowserDialog' in args[-1]
                            assert run.call_args.kwargs['env']['BATBRAIN_INITIAL_FOLDER']==str(destination)
                        if picker=='mac':assert args[-1]==str(destination) and 'choose folder' in args[-2]
                        run.return_value=subprocess.CompletedProcess([],0,stdout='\n',stderr='')
                        assert service.browse(str(destination))=={'cancelled':True}
                report['folder_picker_command']=picker or 'paste path available'
                # Cover all picker integrations even when only one OS is available.
                for target,kind,executable in [('win32','windows','powershell.exe'),('darwin','mac','osascript'),('linux','zenity','zenity')]:
                    with patch.object(backend,'sys',SimpleNamespace(platform=target,executable=sys.executable)), \
                         patch.object(backend.shutil,'which',side_effect=lambda name:executable if name==executable else None), \
                         patch.object(backend.subprocess,'run') as run:
                        assert service.picker()==kind
                        run.return_value=subprocess.CompletedProcess([],0,stdout=str(destination)+'\n',stderr='')
                        assert service.browse(str(destination))['folder']==str(destination)
                        assert run.call_args.kwargs['env']['BATBRAIN_INITIAL_FOLDER']==str(destination)
                        run.return_value=subprocess.CompletedProcess([],0,stdout='\n',stderr='')
                        assert service.browse(str(destination))=={'cancelled':True}
                report['windows_macos_linux_picker_integrations']='passed with mocked dialogs'
                if os.name=='nt':
                    for name in ['CON','NUL.txt','bad:name','trailing.','bad?name']:
                        try:service.prepare({'folder':str(destination),'name':name,'format':'mp4'})
                        except ValueError:pass
                        else:raise AssertionError(name)
                    report['windows_reserved_names']='passed'
            finally:
                if pid is None and (cache/'batbrain/server.json').exists():
                    pid=json.loads((cache/'batbrain/server.json').read_text())['pid']
                if pid:
                    try:os.kill(pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                    time.sleep(.5)
        finally:
            os.environ['PATH']=original_path
            if os.name=='nt':
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER,'Environment') as key:
                    if registry_before:winreg.SetValueEx(key,'Path',0,registry_before[1],registry_before[0])
                    else:
                        try:winreg.DeleteValue(key,'Path')
                        except FileNotFoundError:pass
    output=ROOT/'platform-test-report.json';output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
