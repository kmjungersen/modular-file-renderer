# -*- coding: utf-8 -*-
import os
import sys
import shutil

from invoke import task, run

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')


HERE = os.path.abspath(os.path.dirname(__file__))

@task
def init_player():
    src = os.path.join(HERE, 'player', 'mfr_config_local.py.example')
    dest = os.path.join(HERE, 'player', 'mfr_config_local.py')
    if not os.path.exists(dest):
        print('Copying {src} to {dest}'.format(**locals()))
        shutil.copy(src, dest)

@task
def clean_player():
    """Remove mfr assets from the player's static folder."""
    player_static_dir = os.path.join(HERE, 'player', 'static', 'mfr')
    print('Removing player static directory')
    shutil.rmtree(player_static_dir)

@task
def player(clean=False):
    """Run the player app."""
    init_player()
    if clean:
        clean_player()
    from player import create_app
    app = create_app()
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))


@task
def test():
    run('python setup.py test', pty=True)

@task
def clean():
    run("rm -rf build")
    run("rm -rf dist")
    run("rm -rf mfr.egg-info")
    clean_docs()
    print("Cleaned up.")

@task
def clean_docs():
    run("rm -rf %s" % build_dir)

@task
def browse_docs():
    platform = str(sys.platform).lower()
    command = {'darwin': 'open ',
               'linux': 'idle ',
               'win32': '',
               }
    if command.get(platform):
        run("{0}{1}".format(command[platform],
                            os.path.join(build_dir, 'index.html')))
    else:
        print "Unsure how to open the built file on this operating system."
        sys.exit(1)

@task
def docs(clean=False, browse=False):
    if clean:
        clean_docs()
    run("sphinx-build %s %s" % (docs_dir, build_dir), pty=True)
    if browse:
        browse_docs()

@task
def readme(browse=False):
    run('rst2html.py README.rst > README.html')

@task
def publish(test=False):
    """Publish to the cheeseshop."""
    try:
        __import__('wheel')
    except ImportError:
        print("wheel required. Run `pip install wheel`.")
        sys.exit(1)
    if test:
        run('python setup.py register -r test sdist bdist_wheel upload -r test')
    else:
        run("python setup.py register sdist bdist_wheel upload")