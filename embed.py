
NOTES = {}

#-----INCEPT-----#

from io import StringIO
from os.path import isfile

def get_embedded_file(path):
	encoded = STATIC_ASSETS.get(path, None)
	if encoded:
		return base64.b64decode(encoded).decode('utf-8')
	return None

class JFile:
	def __init__(self, path, mode = 'r'):
		self.path = path
		self.mode = mode
		if mode == 'r' and not self.external and  not self.embeded:
			raise FileNotFoundError("No such file or directory: '%s'"%path)
	
	def __enter__(self):
		return self
	
	def __exit__(self, *args):
		pass
		
	@property
	def embeded(self):
		return self.path in STATIC_ASSETS.keys()

	@property
	def external(self):
		return isfile(self.path)
	
	def _readDisk(self, path):
		if self.external:
			with open(path) as f:
				return f.read()
		return None
	
	def _readEmbed(self, path):
		return get_embedded_file(path)

	def read(self):
		if self.external:
			return self._readDisk(self.path)
		elif self.embeded:
			return self._readEmbed(self.path)

	def write(self, data):
		if self.mode == 'w':
			with open(self.path, 'w') as f:
				return f.write(data)
		raise FileNotFoundError("No such file or directory: '%s'"%path)

def jopen(*args, **kwargs):
	print('opening!')
	return JFile(*args, **kwargs)
	
@app.route('/')
def server_home():
	f = get_embedded_file('/index.html')
	if f:
		return f
	raise Exception('No bundled index.html')

# Serve static files under /static/
@app.route('/static/<path>')
def get_static(path):
	f = get_embedded_file('/static/' + path)
	if f:
		return f
	raise Exception('No bundled file:%s'%path)


@app.route('/favicon.ico')
def fav():
	# with open("favicon.png", 'rb') as f:
	# 	return f.read()
	return '200'