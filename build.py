#!/usr/bin/python3
import click
from os.path import abspath
import subprocess
import shlex
from os import chdir, getcwd, walk, system
import base64

class Config:
	verbose = False
	debug = False
	vendor = 'vendor/'
	jot_store = 'https://github.com/tmacro/jot-store-reference.git'
	jot_editor = 'https://github.com/tmacro/jot-editor.git'

def run(command, env = {}, verbose = True):
	args = shlex.split(command)
	proc = subprocess.Popen(args, env = env, stderr = subprocess.STDOUT,
						stdout = subprocess.PIPE, universal_newlines = True)
	if verbose:
		for line in proc.stdout:
			click.echo(line.strip('\n'))
	proc.wait()
	return proc.returncode

def git_clone(repo, path):
	cmd = 'git clone %s %s'%(repo, path)
	return run(cmd) == 0

def git_pull(path):
	cwd = getcwd()
	chdir(path)
	ret = run('git pull')
	chdir(cwd)
	return ret == 0

def read(path):
	with open(path) as f:
		return f.read()
	
def package_assets(path):
	assets = dict()
	cwd = getcwd()
	chdir(path)
	for p, ds, fs in walk('.'):
		for f in fs:
			with open(p+'/'+f) as file:
				assets[p[1:]+'/'+f] = base64.b64encode(file.read().encode('utf-8'))
	chdir(cwd)
	return assets

def package_file(path):
	with open(path) as f:
		return { path: base64.b64encode(f.read().encode('utf-8'))}

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.version_option('0.1.0')
@click.pass_context
@click.option('--verbose', '-v', 
	is_flag=True,
	help='Enables verbose logging.')
@click.option('--vendor', 
	default = Config.vendor,
	metavar='PATH', 
	help='Changes the vendor directory.')
@click.option('--store', 
	default = Config.jot_store,
	metavar='GIT_REPO', 
	help='Changes the git repo used for jot_store.')
@click.option('--editor', 
	default = Config.jot_editor,
	metavar='GIT_REPO', 
	help='Changes the git repo used for jot_editor.')
def cli(ctx, vendor, store, editor, verbose):
	ctx.obj = Config()
	ctx.obj.ctx = ctx
	ctx.obj.verbose = verbose
	ctx.obj.jot_editor = editor
	ctx.obj.jot_store = store
	ctx.obj.vendor = abspath(vendor)

@cli.command()
@pass_config
def bundle(config):
	click.echo('Bundling vendor...')
	cwd = getcwd()
	chdir('vendor/editor')
	system('npm run build')
	chdir(cwd)
	assets = package_assets(config.vendor + '/editor/dist')
	click.echo('Bundling Jot...')
	stringed = '\nSTATIC_ASSETS = %s'%str(assets)
	embed = read('embed.py')
	bundle = stringed + '\n' + embed 
	with open('build/bundle.py', 'w') as f:
		f.write(bundle)
	
@cli.command()
@pass_config
def build(config):
	config.ctx.invoke(bundle)
	click.echo('Building Jot...')
	with open('build/bundle.py') as f:
		app_bundle = f.read()
	with open(config.vendor + '/store/jot.py') as file:
		jot = file.read()
	jot = jot.split('#---Insert---\n')
	jot.insert(1, app_bundle)
	_exit = read('exit.py')
	jot.append(_exit)	
	with open('build/jot.py', 'w') as f:
		f.write(''.join(jot))

@cli.command()
@pass_config
def install(config):
	click.echo('Installing Dependencies...')
	run('mkdir -p %s'%config.vendor)
	git_clone(config.jot_editor, config.vendor + '/editor')
	git_clone(config.jot_store, config.vendor + '/store')
	chdir(config.vendor+'/editor')
	run('npm install')

@cli.command()
@pass_config
def update(config):
	click.echo('Updateing Dependencies...')
	git_pull(config.vendor + '/editor')
	git_pull(config.vendor + '/store')
	chdir(config.vendor+'/editor')
	run('npm install')

if __name__ == '__main__': cli()