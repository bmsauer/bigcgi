from unittest.mock import MagicMock, patch
import os
import tempfile

from util.test import NamedTemporaryFileMock

os.mkdir = MagicMock()
os.system = MagicMock()
tempfile.NamedTemporaryFile = NamedTemporaryFileMock

import util.filesys

def test_check_user_directories():
    os.mkdir = MagicMock(side_effect=FileNotFoundError)
    assert util.filesys.check_user_directories("testuser") == False
    os.mkdir = MagicMock()
    assert util.filesys.check_user_directories("testuser") == True

def test_move_file_contents():
    with patch("util.filesys.move_file", MagicMock(return_value=False)):
        result = util.filesys.move_file_contents("filename", "testuser", "file", b"123")
        assert result == False
    
    with patch("util.filesys.move_file",MagicMock(return_value=True)):
        result = util.filesys.move_file_contents("filename", "testuser", "file", b"123")
        util.filesys.move_file.assert_called_with("testuser", "file1", "/home/testuser/files/filename", "400")
        assert result == True

        result = util.filesys.move_file_contents("filename", "testuser", "app", b"123")
        util.filesys.move_file.assert_called_with("testuser", "file1", "/home/testuser/public_html/filename", "500")
        assert result == True

def test_move_file():
    os.system = MagicMock(return_value=1)
    assert util.filesys.move_file("testuser", "tmpfilename", "path", "400") == False
    os.system = MagicMock(return_value=0)
    assert util.filesys.move_file("testuser", "tmpfilename", "path", "400") == True
