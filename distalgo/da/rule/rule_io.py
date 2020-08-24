from pathlib import Path, PurePath

# rule_path = PurePath.joinpath(PurePath(__file__).parent,'rules')
rule_path = PurePath('__pycache__')
if not Path(rule_path).exists():
    Path(rule_path).mkdir()

def write_file(filename, string):
    file = open(PurePath.joinpath(rule_path,filename),'w')
    file.write(string)
    file.close()

def read_answer(filename):
    return open(PurePath.joinpath(rule_path,"{}.answers".format(filename)),"r").read()

def clear_cache(filename):
	for x in Path(rule_path).iterdir():
		if x.is_file() and PurePath(x).name.startswith(filename+'.RuleSet'):
			x.unlink()
		