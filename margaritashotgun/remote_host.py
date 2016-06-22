import logging
#from margaritashotgun.remote_shell import RemoteShell
#from margaritashotgun.auth import Auth
from margaritashotgun.auth import Auth
from margaritashotgun.remote_shell import RemoteShell, Commands
from margaritashotgun.repository import Repository

logger = logging.getLogger(__name__)


def capture_memory(host):
    print("todo capture")

class RemoteHost():
    """
    """

    def __init__(self):
        self.memory = None
        self.tunnel = None
        self.shell = None
        self.log_wrapper = None
        self.repo = Repository()
        self.shell = RemoteShell()
        self.commands = Commands
        print("init")

    def mem_size(self):
        result = self.shell.execute(self.commands.mem_size.value)
        print(result['stdout'])

    def kernel_version(self):
        result = self.shell.execute(self.commands.kernel_version.value)
        print(result['stdout'])

    def wait_for_lime(self):
        # TODO: requires async execution :/
        print('todo')

#    def wait_for_lime(self, port=4000):
#        tries = 0
#        lime_listener = "0.0.0.0:{}".format(port)
#        command = "netstat -lnt | grep {}".format(port)
#        lime_loaded = False
#        while tries < 60 and lime_loaded is False:
#            stdin, stdout, stderr = self.ssh.exec_command(command)
#            output = stdout.read().decode('utf-8').strip("\n")
#            if lime_listener in output:
#                lime_loaded = True
#            tries = tries + 1
#            time.sleep(1)
#        return lime_loaded


    def test(self):
        # meant to fail
        #auth = Auth()
        # should pass (user + pass auth)
        auth = Auth(username='user', password='hunter2', key=None)
        print(auth.method)
        print(auth.password)
        # should pass (user + key)
        auth = Auth(username='user', password=None, key='key')
        print(auth.method)
        print(type(auth.key))
        # should pass (user + encryptedkey)
        auth = Auth(username='user', password='hunter2', key='encrypted_key')
        print(auth.method)
        print(type(auth.key))
        print("meep")

if __name__=='__main__':
    rh = RemoteHost()
    rh.test()
