In order to run the experiments here:
 
 * Under data_prep, edit the pyast_views.py file to include the repos you want in the repos list.
 * Run "python pyast_views.py" with the latest version of python in the data_prep directory.
 * If you want a single repo out of all repos listed, you can run: "python pyast_views.py reponame".
 * After the data is generated, run the following in the root directory for your repo:
python -m da --message-buffer-size=409600000 --rule PA.da repo_name

You may need to play with the buffer size.