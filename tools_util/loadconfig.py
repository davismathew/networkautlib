import os
import ConfigParser

def readconf():
    config = ConfigParser.ConfigParser()
    config.read('/etc/ansibengine.conf')
    return config


def project_path(type):
    config = readconf()
    if type == 'project':
        path = config.get('paths', 'project_path')
    elif type == 'play':
        path = config.get('paths', 'project_path')
    elif type == 'resultout':
        path = config.get('paths', 'result_path')
    return os.listdir(path)

def get_vars(type):
    config = readconf()
    if type == 'project':
        vars = config.get(ENVIRONMENT, 'project_path')
    elif type == 'play':
        vars = config.get(ENVIRONMENT, 'project_path')
    elif type == 'resultout':
        vars = config.get(ENVIRONMENT, 'result_path')
    elif type == 'baseurl':
        vars = config.get(ENVIRONMENT, 'baseurl')
    elif type == 'ansibengineemc':
        vars = config.get(ENVIRONMENT, 'ansibengineemc')
    elif type == 'ansibenginemtn':
        vars = config.get(ENVIRONMENT, 'ansibenginemtn')
    return vars
