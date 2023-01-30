#!/usr/bin/env python3
import os
import subprocess as sp
import unittest
import sys
import tempfile
import time

from pathlib import Path

test_dir = Path(__file__).resolve().parent
lib_dir = test_dir.parent / 'src'
test_src_dir = test_dir / 'checker_files'

sys.path.insert(0, str(lib_dir))
import mypycheck # type: ignore

class BasicTests(unittest.TestCase):
    def setUp(self) -> None:
        mypycheck.clean()

    def test_good(self):
        with tempfile.TemporaryFile(mode='w+b') as f:
            mypycheck._check(str(test_src_dir / 'good_func.py'), stdout=f.fileno(), stderr=f.fileno())

    def test_skip_after_check(self):
        with tempfile.TemporaryFile(mode='w+b') as f:
            mypycheck._check(str(test_src_dir / 'good_func.py'), stdout=f.fileno(), stderr=f.fileno())
            assert f.seek(0, os.SEEK_END) > 0
            f.truncate(0)
            #should not output anything on a second call
            mypycheck._check(str(test_src_dir / 'good_func.py'), stdout=f.fileno(), stderr=f.fileno())
            assert f.seek(0, os.SEEK_END) == 0

    def test_rescan_after_update(self):
        with tempfile.TemporaryFile(mode='w+b') as f:
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.py') as src_f:
                with (test_src_dir / 'good_func.py').open('rb') as src_rd:
                    src_f.write(src_rd.read())
                src_f.flush()
                mypycheck._check(src_f.name, stdout=f.fileno(), stderr=f.fileno())
                assert f.seek(0, os.SEEK_END) > 0
                f.truncate(0)
                #should not output anything on a second call
                mypycheck._check(src_f.name, stdout=f.fileno(), stderr=f.fileno())
                assert f.seek(0, os.SEEK_END) == 0
                #give timestamp a little time to be different
                time.sleep(0.1)
                src_f.write(b'\n')
                src_f.flush()
                mypycheck._check(src_f.name, stdout=f.fileno(), stderr=f.fileno())
                assert f.seek(0, os.SEEK_END) > 0

    def test_bad_no_func_ret(self):
        with tempfile.TemporaryFile(mode='w+b') as f:
            with self.assertRaises(sp.CalledProcessError):
                mypycheck._check(str(test_src_dir / 'bad_no_func_ret.py'), stdout=f.fileno(), stderr=f.fileno())
            assert f.seek(0, os.SEEK_END) > 0

    def test_bad_missing_func_arg(self):
        with tempfile.TemporaryFile(mode='w+b') as f:
            with self.assertRaises(sp.CalledProcessError):
                mypycheck._check(str(test_src_dir / 'bad_missing_func_arg.py'), stdout=f.fileno(), stderr=f.fileno())
            assert f.seek(0, os.SEEK_END) > 0

    def test_bad_no_func_args(self):
        with tempfile.TemporaryFile(mode='w+b') as f:
            with self.assertRaises(sp.CalledProcessError):
                mypycheck._check(str(test_src_dir / 'bad_no_func_args.py'), stdout=f.fileno(), stderr=f.fileno())
            assert f.seek(0, os.SEEK_END) > 0

if __name__ == '__main__':
    unittest.main()