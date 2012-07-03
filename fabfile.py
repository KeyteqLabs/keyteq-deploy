# vim: ts=4 sw=4: expandtab
from __future__ import with_statement
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import exists
from xml.dom.minidom import parse
import sys

#Configure static environment
env.roledefs = {
    'localhost': ['localhost'],
    'dev': ['apache@dev-web1'],
    'stage': ['apache@stage-web1'],
    'production': ['apache@c01web01.keyteq.no', 'apache@c01web02.keyteq.no']
}

#Configure dynamic environment
dom = parse('extension.xml')
deploy = dom.getElementsByTagName('deploy')
if (not deploy):
	print red("Must set deploy target in extension.xml")
	print "See http://github.com/keyteqlabs/keyteq-deploy"
	sys.exit(1)

deploy = deploy[0]
site = deploy.getElementsByTagName('site')[0].childNodes[0].data
extension = deploy.getElementsByTagName('extension')[0].childNodes[0].data

path_conf = {
    'default': '/srv/sites',
    'dev': '/var/www/sites'
}

#site_dir = '/srv/sites/{0}/{1}'.format(site[0], site)

@task
@roles('dev')
def join():
    extension_dir = ext_dir(extension, 'dev')
    _site_dir = site_dir('dev')
    with cd(extension_dir):
        run('git pull')
    with cd(_site_dir):
        run('ezcache');
    print green('Shared dev area updated')

@task
@roles('production')
def deploy():
    pull(ext_dir(extension))
    execute(extensions)
    execute(cache)

@task
@roles('stage')
def stage():
    pull(ext_dir(extension))
    execute(cache)

def extensions():
    related = _extensions()
    for e in related:
        _dir = ext_dir(e['name'])
        if (not exists(_dir) and 'repo' in e):
            run('git clone {0} {1}'.format(e['repo'], _dir))

        if (exists(_dir)):
            with cd(_dir):
                if ('branch' in e):
                    run('git checkout {0}'.format(e['branch']))
                run('git pull')

def site_dir(where):
    return "{0}/{1}/{2}/www".format(path_conf[where], site[0], site)

def _extensions():
    extensions = dom.getElementsByTagName('dependencies')[0].getElementsByTagName('extension')
    exts = []
    for ext in extensions:
        data = {}
        for (name, value) in ext.attributes.items():
            data[name] = value
        exts.append(data)
    return exts

def ext_dir(extension, where='default'):
    return '{0}/extension/{1}/'.format(site_dir(where), extension)

def pull(path):
    with cd(path):
        run('git pull')

def cache(where='default'):
    with cd("{0}".format(site_dir(where))):
        run('ezcache')
