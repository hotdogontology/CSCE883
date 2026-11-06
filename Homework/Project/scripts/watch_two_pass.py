"""Observe the existing job, keep Windows awake, and publish only aggregate reports."""
import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import subprocess
import time

from export_two_pass import ROOT, OUT, DEST, export

REPO=ROOT.parents[1]
GIT=Path('C:/Program Files/Git/cmd/git.exe')
REPORT_PREFIX='Homework/Project/reports/two-pass/'


def alive(pid):
    kernel=ctypes.windll.kernel32
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle:return False
    try:
        code=wintypes.DWORD()
        return bool(kernel.GetExitCodeProcess(handle,ctypes.byref(code))) and code.value==259
    finally:kernel.CloseHandle(handle)


def git(*args):
    return subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),*args],
        cwd=REPO,capture_output=True,text=True,encoding='utf-8',errors='replace')


def publish():
    staged=git('diff','--cached','--name-only')
    if staged.returncode or any(not p.startswith(REPORT_PREFIX) for p in staged.stdout.splitlines()):
        raise RuntimeError('Refusing automatic commit because unrelated files are staged')
    result=git('add','--',REPORT_PREFIX)
    if result.returncode:raise RuntimeError('Could not stage aggregate reports')
    if git('diff','--cached','--quiet').returncode==1:
        if git('commit','-m','Record two-pass experiment progress').returncode:
            raise RuntimeError('Could not commit aggregate reports')
    if git('push','origin','main').returncode:
        raise RuntimeError('Git push failed; reports remain saved locally. No credentials logged.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    pid=int((OUT/'job.pid').read_text().strip())
    # This affects this process only; normal sleep policy resumes when it exits.
    awake=ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    if not awake:raise RuntimeError('Unable to hold a Windows execution request')
    previous=None
    try:
        while True:
            state=export()
            job=state['job']
            identity=(job.get('status'),job.get('current_stage'))
            terminal=job.get('status') in ('complete','failed')
            running=alive(pid)
            if identity!=previous or not running:
                if not running and not terminal:
                    snapshot=DEST/'latest.json'
                    state['observer_note']='Driver exited without a terminal job status; inspect local logs.'
                    snapshot.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
                if args.publish:publish()
                print(json.dumps({'event':'snapshot','job':job,'driver_alive':running}),flush=True)
                previous=identity
            if terminal or not running:break
            time.sleep(30)
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__=='__main__':main()
