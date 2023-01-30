import os
import sqlite3
import subprocess as sp
import sys

from pathlib import Path

db_path = Path(Path.home() / '.mypycheck.sqlite3')

def _create_files_table(con: sqlite3.Connection) -> None:
    con.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    timestamp DOUBLE NOT NULL
                );''')
    try:
        con.execute('''CREATE UNIQUE INDEX idx_files_name 
                        ON files (name);''')
    except:
        pass

def _check(file: str, stdout: int=-1, stderr: int=-1) -> None:
    path = Path(file).resolve(strict=True)
    try:
        connection = sqlite3.connect(db_path)
        _create_files_table(connection)
    except:
        if db_path.exists():
            os.remove(db_path)
        connection = sqlite3.connect(db_path)
        _create_files_table(connection)

    cursor = connection.execute("SELECT name,timestamp FROM files WHERE name = ?", (str(path), ))
    row = cursor.fetchone()
    mtime = path.stat().st_mtime
    if row is not None and row[1] >= mtime:
        return

    if stdout < 0:
        stdout = sys.stdout.fileno()
    if stderr < 0:
        stderr = sys.stderr.fileno()

    # Throws sp.CalledProcessError on failed check
    sp.check_call(['mypy', file, '--strict'], stdout=stdout, stderr=stderr)

    connection.execute("INSERT OR REPLACE INTO files (name, timestamp) VALUES (?, ?);", (str(path), mtime))
    connection.commit()
    connection.close()

def check(file: str) -> None:
    try:
        if '/site-packages/' in str(file):
            return
        _check(file)
    except sp.CalledProcessError as err:
        exit(1)

def clean() -> None:
    if db_path.exists():
        os.remove(db_path)

def check_main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('--clean', action='store_true')
    args = parser.parse_args()

    if args.clean:
        clean()

    check(args.target)

