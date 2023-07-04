import paramiko
import shutil
from functools import wraps
from paramiko.ssh_exception import AuthenticationException, ProxyCommandFailure, NoValidConnectionsError

host=[SFTP Server Address, String Type]
port=[SFTP Server Port, Int Type]
username=[SFTP Server Account, String Type]
password=[SFTP Server Password, String Type]

message="test message\r\n abdbdjaslkdjaslkdjals\r\n 123343545465645\r\n "\
        "1,2,3,3,4,,5,56,6"\
        "a,v,d,sd,c,d,d"


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
        print('connection established successfully')
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
    def _get_list(self):
        files=self._ftp.listdir(self._base_path)
        return files

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
    storage = SFTPStorage()
    files = storage._get_list()
    print(f'files0={files}')
    storage._remove("3.txt")
    storage._write("3.txt", "there are no exception. you must go now.")
    msg = storage._read("3.txt")
    print(f'msg = {msg}')

"""
aip-0164@aip-0164ui-MacBookPro sftp % ## Abnormal Case
aip-0164@aip-0164ui-MacBookPro sftp % python ftp4.py
Exception : [Errno 8] nodename nor servname provided, or not known
files0=None
Exception : [Errno 8] nodename nor servname provided, or not known
Exception : [Errno 8] nodename nor servname provided, or not known
Exception : [Errno 8] nodename nor servname provided, or not known
msg = None
aip-0164@aip-0164ui-MacBookPro sftp % ## Normal Case
aip-0164@aip-0164ui-MacBookPro sftp % python ftp4.py
connection established successfully
files0=['2.txt', '3.txt']
connection established successfully
connection established successfully
connection established successfully
msg = b'there are no exception. you must go now.'
"""
