#!/home/davis/Documents/netautgui/flask/bin/python2.7
import os
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
sys.path.insert(0,'/usr/lib/python2.7/dist-packages')
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor



class AnsiblePlaybook:

  def __init__(self,playbook_path,host_list,stdoutfile):
      self.playbook_path='/home/davis/Documents/Network-automation/'+str(playbook_path).strip()

      self.host_list='/home/davis/Documents/Network-automation/'+str(host_list).strip()

      self.stdoutfile = stdoutfile

  def runPlaybook(self):
    sys.stdout = open(self.stdoutfile,'w')
    variable_manager = VariableManager()
    loader = DataLoader()
     
    inventory = Inventory(loader=loader, variable_manager=variable_manager,  host_list=self.host_list)
    #self.playbook_path
#    self.playbook_path = '/home/davis/Documents/Network-automation/cisco_xe.yml'

    if not os.path.exists(self.playbook_path):
        print '[INFO] The playbook does not exist'
        sys.exit()

    Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user='slotlocker', private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method=None, become_user='root', verbosity=None, check=False)

    #variable_manager.extra_vars = {'hosts': 'mywebserver'} # This can accomodate various other command line arguments.`

    passwords = {}

    pbex = PlaybookExecutor(playbooks=[self.playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, options=options, passwords=passwords)

    results = pbex.run()

    print "Output ::-",results
    return results
