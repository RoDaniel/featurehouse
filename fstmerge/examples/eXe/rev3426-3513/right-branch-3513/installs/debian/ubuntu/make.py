import sys
import os
import getopt
import shutil
import time
import subprocess
import re
import tempfile
SRCDIR = os.path.abspath('../../..')
WDIR = os.getcwd()
changelog = 'debian/changelog'
REVISION_FILE = os.path.join(SRCDIR, 'exe/engine/version_svn.py')
os.chdir(SRCDIR)
try:
    psvn = subprocess.Popen('svnversion', stdout=subprocess.PIPE)
    psvn.wait()
    revision = psvn.stdout.read().strip()
    open(REVISION_FILE, 'wt').write('revision = "%s"\n' % revision)
except OSError:
    print "*** Warning: 'svnversion' tool not available to update revision number"
sys.path.insert(0, SRCDIR)
from exe.engine import version
os.chdir(WDIR)
cl = open(changelog, 'wt')
news = open(os.path.join(SRCDIR, 'NEWS'))
need_version = True
timestamp = time.localtime()
while True:
    nl = news.readline()
    if nl.startswith("Version 0.23"):
        break
    elif nl.startswith("Version"):
        need_version = False
        tl = re.match(r'Version\s+(?P<version>\d\.\d+)\s+\(r(?P<revision>\d+)\)\s+(?P<date>\d+-\d+-\d+)', nl)
        if not tl:
            print "badly formed version header in NEWS: ", nl
            sys.exit(1)
        versionstring = tl.group('version') + '.0.' + tl.group('revision')
        timestamp = time.strptime(tl.group('date'), '%Y-%m-%d')
        cl.write("python-exe (%s-ubuntu1) unstable; urgency=low\n" % versionstring)
    elif nl.strip() == "":
        cl.write("\n")
        cl.write(" -- eXe Project <exe@exelearning.org>  %s\n" %
                time.strftime("%a, %d %b %Y %H:%M:%S +1200", timestamp))
        cl.write("\n")
    else:
        if need_version:
            need_version = False
            cl.write("python-exe (%s-ubuntu1) unstable; urgency=low\n" % version.version)
        cl.write('    ' + nl)
news.close()
cl.write(open(changelog+".in", 'rt').read())
cl.close()
newDir = os.path.join(SRCDIR, 'debian')
if os.path.islink(newDir):
    os.remove(newDir)
elif os.path.exists(newDir):
    raise Exception('exe/debian directory/file already exists, aborting...')
src = os.path.abspath('debian')
os.chdir(SRCDIR)
os.symlink(src, 'debian')
subprocess.check_call('fakeroot debian/rules binary', shell = True)
