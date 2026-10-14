"""Local reports for unexpected Python errors, without save data or messages.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import json
import os
from pathlib import Path
import sys
import traceback
from datetime import datetime, timezone
from version import VERSION


def report_directory():
    base=Path(os.environ.get('LOCALAPPDATA') or Path.home()/'AppData'/'Local')
    return base/'UniversalSaveEditor'


def write_error_report(error_type,error,tb,directory=None):
    # No exception text, source lines, locals, filenames of saves or account IDs.
    frames=[{'module':Path(frame.filename).name,'function':frame.name,'line':frame.lineno}
            for frame in traceback.extract_tb(tb,limit=24)]
    report={'application':'UniversalSaveEditor','version':VERSION,
            'time_utc':datetime.now(timezone.utc).isoformat(),
            'python':sys.version.split()[0],'portable':bool(getattr(sys,'frozen',False)),
            'error_type':error_type.__name__,'frames':frames,
            'privacy':'No exception messages, source lines, local values or save contents are included.'}
    directory=Path(directory) if directory is not None else report_directory()
    target=directory/'last-error.json'
    try:
        directory.mkdir(parents=True,exist_ok=True)
        temporary=directory/'last-error.json.tmp'
        temporary.write_text(json.dumps(report,indent=2,ensure_ascii=True),encoding='utf8')
        os.replace(temporary,target)
    except OSError:
        return None
    return target


def install_error_reporting(on_error=None):
    previous=sys.excepthook
    busy=False
    def hook(error_type,error,tb):
        nonlocal busy
        if busy:
            previous(error_type,error,tb);return
        busy=True
        try:
            report=write_error_report(error_type,error,tb)
            if on_error is not None:on_error(report)
            else:previous(error_type,error,tb)
        except Exception:
            previous(error_type,error,tb)
        finally:busy=False
    sys.excepthook=hook
    return previous
