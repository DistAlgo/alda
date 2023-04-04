repos_list_file = './data_prepare/numpy-python-most-stars-repos.txt'
output_bat_file = './run-candidate-loop-multiple-repos.bat'
repo_names = []

with open(repos_list_file, 'r') as input_repos, open(output_bat_file, 'w') as output_bat:
	# download repos from github
	output_bat.write('cd data_prepare\nFOR %%A IN (')
	for i, line in enumerate(input_repos):
		if 'github' in line:
			repo_parts = line.strip().split('/')
			repo_names.append(repo_parts[-1])
			if i == 0:
				output_bat.write(line.strip())
			else:
				output_bat.write(',' + line.strip())
	output_bat.write(') DO (\ngit clone %%A\n)\n')


	# generate data for anlyzing
	output_bat.write('FOR %%A IN (')
	for i, repo_name in enumerate(repo_names):
		if i == 0:
			output_bat.write(repo_name)
		else:
			output_bat.write(',' + repo_name)
	output_bat.write(') DO (\npython pyast_views.py %%A\n)\n')


	# analyzing
	output_bat.write('cd ..\nFOR %%A IN (')
	for i, repo_name in enumerate(repo_names):
		if i == 0:
			output_bat.write(repo_name)
		else:
			output_bat.write(',' + repo_name)
	output_bat.write(') DO (\npython -m da --rules -r launcher.da LoopToQuery %%A candidate rule\n)')

