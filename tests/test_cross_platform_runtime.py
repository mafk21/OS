"""Native-host smoke checks and mocked platform command contracts (no GUI required)."""
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
from types import SimpleNamespace

import pytest
import install_jarvis as installer
from core import os_control as osc
from actions import shell_agent as shell
from actions import computer_control as control
from actions import computer_settings as settings


def test_all_native_launchers_and_unicode_space_paths(tmp_path):
    folder=tmp_path/'Jarvis apps é';folder.mkdir()
    files=installer.write_native_launchers(folder)
    assert {Path(f).name for f in files}=={'Start_JARVIS.bat','Start_JARVIS.command','Start_JARVIS.sh'}
    for name in ('Start_JARVIS.command','Start_JARVIS.sh'):
        path=folder/name
        assert 'cd "$(dirname "$0")"' in path.read_text()
        if os.name!='nt':assert os.access(path,os.X_OK)


@pytest.mark.parametrize('system,relative',[('Windows','Scripts/python.exe'),('Darwin','bin/python3'),('Linux','bin/python3')])
def test_virtualenv_layout_per_os(monkeypatch,tmp_path,system,relative):
    monkeypatch.setattr(installer.platform,'system',lambda:system)
    assert installer.venv_python(tmp_path)==tmp_path/relative


def test_launcher_reuses_existing_venv(monkeypatch,tmp_path):
    exe=tmp_path/'python';exe.touch();calls=[]
    monkeypatch.setattr(installer,'venv_python',lambda:exe)
    monkeypatch.setattr(installer.subprocess,'call',lambda argv,**kw:calls.append(argv) or 0)
    assert installer.main(['--launch'])==0
    assert calls[0][0]==str(exe)


def test_mac_terminal_quotes_shell_metacharacters_and_never_fakes_success(monkeypatch,tmp_path):
    # Keep shell metacharacters on every host; double quotes are illegal in
    # Windows filenames, so use an apostrophe there to retain quote coverage.
    name = "a $(touch SHOULD_NOT_EXIST) 'name'" if os.name == 'nt' else 'a $(touch SHOULD_NOT_EXIST) "name"'
    folder=tmp_path/name;folder.mkdir()
    calls=[]
    monkeypatch.setattr(osc,'_SYSTEM','Darwin')
    monkeypatch.setattr(osc,'_fast_pid_set',lambda:set())
    monkeypatch.setattr(osc,'list_visible_windows',lambda:[])
    monkeypatch.setattr(osc,'verify_launch',lambda *a,**k:{'verified':False,'pid':None,'window_title':None})
    monkeypatch.setattr(osc.subprocess,'run',lambda argv,**kw:calls.append(argv) or SimpleNamespace(returncode=0,stderr=''))
    result=osc.open_interactive_terminal(cwd=str(folder))
    expected=('cd -- '+shlex.quote(str(folder.resolve()))).replace('\\','\\\\').replace('"','\\"')
    assert expected in calls[0][-1]
    assert result['ok'] is False
    assert result['verified_window'] is None


@pytest.mark.parametrize('terminal,flag',[('gnome-terminal','--'),('xfce4-terminal','--command'),('konsole','-e')])
def test_linux_terminal_argument_contract(monkeypatch,terminal,flag):
    calls=[]
    monkeypatch.setattr(osc,'_SYSTEM','Linux');monkeypatch.setenv('DISPLAY',':99')
    monkeypatch.setattr(osc,'_fast_pid_set',lambda:set());monkeypatch.setattr(osc,'list_visible_windows',lambda:[])
    monkeypatch.setattr(osc.shutil,'which',lambda s:s if s==terminal else None)
    monkeypatch.setattr(osc,'unpatched_popen',lambda argv,**kw:calls.append(argv) or SimpleNamespace(pid=1234,poll=lambda:None))
    monkeypatch.setattr(osc,'verify_launch',lambda *a,**k:{'verified':True,'pid':1234,'window_title':'Terminal'})
    assert osc.open_interactive_terminal(command='echo "one two"')['ok']
    assert calls[0][1]==flag
    if terminal=='xfce4-terminal':assert shlex.split(calls[0][2])==['bash','-lc','echo "one two"\nexec bash']
    else:assert calls[0][2:4]==['bash','-lc']


def test_headless_linux_terminal_reports_limitation(monkeypatch):
    monkeypatch.setattr(osc,'_SYSTEM','Linux')
    monkeypatch.delenv('DISPLAY',raising=False);monkeypatch.delenv('WAYLAND_DISPLAY',raising=False)
    monkeypatch.setattr(osc,'_fast_pid_set',lambda:set());monkeypatch.setattr(osc,'list_visible_windows',lambda:[])
    assert not osc.open_interactive_terminal()['ok']


def test_explicit_powershell_uses_pwsh_on_unix(monkeypatch,tmp_path):
    calls=[];monkeypatch.setattr(shell,'_SYSTEM','Darwin')
    monkeypatch.setattr(shell.shutil,'which',lambda name:'/usr/bin/pwsh' if name=='pwsh' else None)
    monkeypatch.setattr(shell.subprocess,'run',lambda argv,**kw:calls.append(argv) or SimpleNamespace(stdout='done',stderr='',returncode=0))
    assert shell._run_once('Get-Location',cwd=str(tmp_path),shell_pref='powershell')=='done'
    assert calls[0][0]=='/usr/bin/pwsh'


@pytest.mark.skipif(os.name=='nt',reason='Actual POSIX shell test; Windows routing tested separately')
def test_actual_bash_selection_supports_bash_not_sh_syntax(tmp_path):
    assert shell._run_once('a=(one two); printf "%s" "${a[1]}"',cwd=str(tmp_path),shell_pref='bash')=='two'


def test_mac_copy_uses_command_not_control(monkeypatch):
    calls=[];monkeypatch.setattr(control,'_PYPERCLIP',False)
    monkeypatch.setattr(control,'_get_os',lambda:'mac')
    monkeypatch.setattr(control,'_hotkey',lambda *args:calls.append(args))
    monkeypatch.setattr(control.time,'sleep',lambda _:None)
    control._clipboard_get();assert calls==[('command','c')]


@pytest.mark.parametrize('value,expected',[('+10%','10%+'),('-10%','10%-'),('42%','42%')])
def test_pipewire_volume_arguments(monkeypatch,value,expected):
    calls=[];monkeypatch.setattr(settings.shutil,'which',lambda s:s if s=='wpctl' else None)
    monkeypatch.setattr(settings.subprocess,'run',lambda argv,**kw:calls.append(argv) or SimpleNamespace(returncode=0,stderr=''))
    settings._linux_volume('volume',value)
    assert calls==[['wpctl','set-volume','@DEFAULT_AUDIO_SINK@',expected,'--limit','1.0']]


def test_audio_backend_failure_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(settings.shutil,'which',lambda s:s if s=='wpctl' else None)
    monkeypatch.setattr(settings.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=1,stderr='No audio server'))
    with pytest.raises(RuntimeError,match='No audio server'):settings._linux_volume('mute','toggle')


def test_missing_display_does_not_prevent_desktop_tool_import():
    script='''
import sys, importlib.abc
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname == 'pyautogui': raise KeyError('DISPLAY')
sys.meta_path.insert(0, Block())
from actions import computer_control, computer_settings
assert not computer_control._PYAUTOGUI
assert not computer_settings._PYAUTOGUI
'''
    subprocess.run([sys.executable,'-c',script],check=True,capture_output=True,text=True)


@pytest.mark.parametrize('system,expected',[('Windows','windows'),('Darwin','mac'),('Linux','linux')])
def test_local_input_uses_host_not_stale_copied_windows_profile(monkeypatch,system,expected):
    from actions import send_message
    monkeypatch.setattr(platform,'system',lambda:system)
    monkeypatch.setattr(control,'_load_config',lambda:{'os_system':'windows'})
    assert control._get_os()==expected
    assert send_message._get_os()==expected


@pytest.mark.skipif(os.name=='nt',reason='POSIX process-group cancellation; Windows uses taskkill /T')
def test_streaming_stop_terminates_spawned_descendants(tmp_path):
    import psutil
    import threading
    import time
    from core.dev_workspace import DevTerminalManager
    mgr=DevTerminalManager();ready=threading.Event();child=[]
    def receive(evt):
        text=str(evt)
        import re
        match=re.search(r'CHILD=(\d+)',text)
        if match:child.append(int(match.group(1)));ready.set()
    mgr.add_listener(receive)
    code="import subprocess,sys,time; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(90)']); print('CHILD='+str(p.pid),flush=True); time.sleep(90)"
    sess=mgr.start_command(shlex.join([sys.executable,'-u','-c',code]),cwd=str(tmp_path))
    try:
        assert ready.wait(5)
        assert mgr.stop_command(sess['id'])
        end=time.monotonic()+3
        alive=True
        while time.monotonic()<end:
            try:alive=psutil.Process(child[0]).status()!=psutil.STATUS_ZOMBIE
            except psutil.NoSuchProcess:alive=False
            if not alive:break
            time.sleep(.02)
        assert not alive,'Stop must not leave shell descendants running'
    finally:
        mgr.stop_command(sess['id'])
        for pid in child:
            try:psutil.Process(pid).kill()
            except psutil.NoSuchProcess:pass
