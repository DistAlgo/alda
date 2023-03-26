from pathlib import Path, PurePath
csp_path = PurePath('__pycache__')
if not Path(csp_path).exists():
	Path(csp_path).mkdir()

def write_file(filename, string):
	file = open(PurePath.joinpath(csp_path,filename),'w')
	file.write(string)
	file.close()

def read_answer(filename):
	return open(PurePath.joinpath(csp_path,"{}.answers".format(filename)),"r").read()

def clear_cache(filename):
	for x in Path(csp_path).iterdir():
		if x.is_file() and PurePath(x).name.startswith(filename+'.CSP'):
			x.unlink()