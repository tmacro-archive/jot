
from os import walk

SEP1 = '#-----INCEPT'
SEP2 = '-----#\n'
SEP = SEP1 + SEP2 #Too prevent accidental detection

def package_notes():
	for p, ds, fs in walk('.notes'):
		for f in fs:
			with open(p+'/'+f) as file:
				print('Packing %s'%p+'/'+f)
				NOTES[p+'/'+f] = base64.b64encode(file.read().encode('utf-8'))
	return NOTES

bug = '''
%s
NOTES = %s
STATIC_ASSETS.update(NOTES)
%s'''%(SEP, str(package_notes()), SEP)

with open('jot.py') as f:
	jot = f.read()

pieces = jot.split(SEP)

if len(pieces) == 2:
	print('This is a fresh copy, installing implant')
	pieces.insert(1,bug)
elif len(pieces) == 3:
	print('File already infected, updating Info')
	pieces.pop(1)
	pieces.insert(1,bug)

with open('jot.py', 'w') as f:
	f.write(''.join(pieces))

print('Exiting...')
