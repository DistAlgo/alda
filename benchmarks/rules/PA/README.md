To run experiments, do these two steps:

1. Generate a database of facts from a Python module or package, by running

      `python ../../pyAnalysis/data_prepare/pyast_views.py <SOURCE>`

   in the `data_prepare` directory (under directory `PA`, not `pyAnalysis`),
   where `<SOURCE>` is (a path ends with) a file or directory containing
   Python or DistAlgo modules or packages.

   This will generate a database, named with the file or directory in
   `<SOURCE>`, in a directory under `data` in directory `PA`.

2. Analyze the generated database using queries in file `PA.da`, by running

      `python -m da --message-buffer-size=409600000 --rule launcher.da --data data/<DATABASE> --module PA`

   in the `PA` directory, where `<DATABASE>` is the directory under `data` 
   that contains the generated facts.

   This will output two groups of timings, for running the two sets of
   rules in file `PA.da`.

   The first group is followed by two lines of query results:

   1. number of defined classes,
      number of class inheritance pairs, and 
      set of root classes, 
      i.e., classes having children classes but not parent classes, and

   2. maximum height of the class inheritance hierarchy, and 
      root classes with the maximum height.

   The second group is followed by one line of query results:

   *   maximum number of descendants any class has, and
      root classes with the maximum number of descendants.

   The running time of the compiler is also added in to a corresponding
   file under directory 'timing'.


Example:

1. under `PA/data_prepare`, run

      `python ../../pyAnalysis/data_prepare/pyast_views.py ../../../distalgo/da/tools`

2. under `PA`, run

      `python -m da --message-buffer-size=409600000 --rule PA.da data/tools`


If you want to analyze a Python or DistAlgo module or package in a git repo, and you
have `git` installed, you could also do the following:

 * Under data_prep, edit the pyast_views.py file to include the repos you want in the repos list.
 * Run "python pyast_views.py" in the data_prep directory.
 * If you want a single repo out of all repos listed, you can run: "python pyast_views.py reponame".
 * After the data is generated, run the following in the 'PA' directory:
python -m da --message-buffer-size=409600000 --rule launcher.da --data data/repo_name --module PA

You may need to play with the buffer size.

In order to use the optimized version, use --module PA_opt instead.