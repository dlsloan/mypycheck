import os
import subprocess as sp

from pathlib import Path

def check(file: str):
    path = Path(file).resolve(strict=True)
    #mypy_path = sp.check_output('_pyinclude', encoding='utf-8')
    env = dict(os.environ)
    try:
        sp.check_call(['mypy', file, '--strict'])#, env=env.update({'MYPYPATH': mypy_path}))
    except sp.CalledProcessError as err:
        exit(1)
