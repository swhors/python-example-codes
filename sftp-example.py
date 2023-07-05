import paramiko
import shutil
from functools import wraps
from paramiko.ssh_exception import AuthenticationException, ProxyCommandFailure, NoValidConnectionsError

host=[SFTP Server Address, String Type]
port=[SFTP Server Port, Int Type]
username=[SFTP Server Account, String Type]
password=[SFTP Server Password, String Type]


class MyException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def sftp_deco():
    def wrapper(func):
        @wraps(func)
        def _impl(self, *args, **kwargs):
            retval = None
            try:
                self._connect()
                retval = func(self, *args, **kwargs)
            except ConnectionError as e:
                print(f'ConnectionError : {e}')
                raise MyException(e)
            except AuthenticationException as e:
                print(f'AuthenticationException : {e}')
                raise MyException(e)
            except ProxyCommandFailure as e:
                print(f'ProxyCommandFailure : {e}')
                raise MyException(e)
            except NoValidConnectionsError as e:
                print(f'NoValidConnectionsError : {e}')
                raise MyException(e)
            except Exception as e:
                print(f'Exception : {e}')
                raise MyException(e)
            finally:
                self._close()
                return retval
        return _impl
    return wrapper

class SFTPStorage:
    def __init__(self):
        # create ssh client
        self._ssh_client = paramiko.SSHClient()
        self._base_path="./backend_test1"
        self._is_connected = False
        self._is_sessioned = False

    def _connect(self):
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh_client.connect(hostname=host,port=port,username=username,password=password)
        self._is_connected = True
        self._ftp=self._ssh_client.open_sftp()
        self._is_sessioned = True

    def _close(self):
        if self._is_sessioned:
            self._ftp.close()
            self._is_sessioned = False
        if self._is_connected:
            self._ssh_client.close()
            self._is_connected = False

    @sftp_deco()
    def _get_list(self, sub_path=None):
        if sub_path == None:
            files=self._ftp.listdir(self._base_path)
        else:
            target_path = self.base_path + "/" + sub_path
            files = self._ftp.listdir(target_path)
        return files

    @sftp_deco()
    def _is_file(self, file_name, sub_Path=None):
        file_names = self._get_list(sub_path)
        return True if file_name in file_names else False
    
    @sftp_deco()
    def _mkdir(self, path_name):
        self._ftp.mkdir(self._base_path + "/" + add_path)
        print(f'files1={files}')
    
    @sftp_deco()
    def _write(self, target_name, buffer):
        file_path = self._base_path + "/" + target_name
        with self._ftp.open(file_path, "w") as fp:
          fp._write(buffer)
          fp.close()

    @sftp_deco()
    def _read(self, target_name):
        file_path = self._base_path + "/" + target_name
        with self._ftp.open(file_path, "r") as fp:
          message1 = fp.read()
          fp.close()
          return message1

    @sftp_deco()
    def _remove(self, target_name):
        file_path = self._base_path + "/" + target_name
        self._ftp.remove(file_path)


if __name__=="__main__":
    or_msg = "there are no exception. you must go now."
    storage = SFTPStorage()
    files = storage._get_list()
    print(f'files0={files}')
    for file in ["3.txt", "2.txt", "1.txt"]:
        print(f'_is_file({file}) = {storage._is_file(file)}')
    storage._remove("3.txt")
    print(f'_is_file(3.txt) = {storage._is_file("3.txt")}')
    storage._write("3.txt", or_msg)
    msg = storage._read("3.txt")
    print(f'msg = {msg}')

"""
aip-0164@aip-MacBookPro sftp % python ftp4.py
files0=['2.txt', '3.txt']
_is_file(3.txt) = True
_is_file(2.txt) = True
_is_file(1.txt) = False
_is_file(3.txt) = False
or_msg = there are no exception. you must go now.
rd_msg = b'there are no exception. you must go now.'
aip-0164@aip-MacBookPro sftp %
"""
