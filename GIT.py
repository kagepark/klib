# Kage Park
from klib.MODULE import MODULE
MODULE().Import('from klib.Type import Type')

def git_ver(git_dir=None):
    if git_dir is not None and os.path.isdir('{0}/.git'.format(git_dir)):
        gver=rshell('''cd {0} && git describe --tags'''.format(git_dir))
        if gver[0] == 0:
            return gver[1]
