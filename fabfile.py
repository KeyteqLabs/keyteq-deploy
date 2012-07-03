from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import exists
from xml.dom.minidom import parse
import sys

#Configure static environment
env.user = 'apache'
env.roledefs = {
    'stage': ['stage-web1'],
    'production': ['c01web01.keyteq.no', 'c01web02.keyteq.no']
}

#Configure dynamic environment
dom = parse('extension.xml')
deploy = dom.getElementsByTagName('deploy')
if (not deploy):
	print "Must set deploy target in extension.xml"
	print "See http://github.com/keyteqlabs/keyteq-deploy"
	sys.exit(1)

deploy = deploy[0]
site = deploy.getElementsByTagName('site')[0].childNodes[0].data
extension = deploy.getElementsByTagName('extension')[0].childNodes[0].data

site_dir = '/srv/sites/{0}/{1}'.format(site[0], site)

def _extensions():
    extensions = dom.getElementsByTagName('dependencies')[0].getElementsByTagName('extension')
    exts = []
    for ext in extensions:
        data = {}
        for (name, value) in ext.attributes.items():
            data[name] = value
        exts.append(data)
    return exts

def ext_dir(extension):
    return '{0}/www/extension/{1}/'.format(site_dir, extension)

def pull(extension):
    with(cd(ext_dir(extension))):
        run('git pull')

def cache():
    with(cd("{0}/www".format(site_dir))):
        run('ezcache')

@roles('production')
def deploy():
    pull(extension)
    execute(extensions)
    execute(cache)

@roles('stage')
def stage():
    pull(extension)
    execute(cache)

def extensions():
    related = _extensions()
    for e in related:
        _dir = ext_dir(e['name'])
        if (not exists(_dir) and 'repo' in e):
            run('git clone {0} {1}'.format(e['repo'], _dir))

        if (exists(_dir)):
            with(cd(_dir)):
                if ('branch' in e):
                    run('git checkout {0}'.format(e['branch']))
                run('git pull')
