# Benchmarking experiments for using rules in Alda

This directory contains the source code and data for performance benchmarking. Each subdirectory is a benchmark with its set of  experiements. The timing of compiling each program will be in a subdirectory `timing` of where `python -m da` is run.

#### trans

This benchmark is on computing the transitive closure of a graph. Example input data are in subdirectory `input`.

1. to obtain all the statistics for a set of runs, run `./test_trans.sh`
2. to measure a single run, run
 `python -m da --rules --message-buffer-size=409600 launcher.da --nume=NUMEDGE --mode=MODE`, where

- `NUMEDGE` is the number of edges in the input; to use an example data file in `input`, use a number after `e` in a file name
- `MODE` specifies the method used to compute the transitive closure, and can be one of:
    - `'rule'`: using the rules, in file `trans_rules.da`
    - `'rev_rule'`: using the same rules as for mode `'rule'` but reversing the two conditions in the second rule, in file `trans_rev_rules.da`
    - `'distalgo'`: using DistAlgo high-level queries, in file `trans_set.da`
    - `'python'`: using Python comprehensions, in file `trans_py.da`

3. to generate your own input data, run
 `python -m da gen_graph.da` in directory `gen_input`; you can update the argument of `gen_graph` on the last line to be any list of numbers, where each number is the number edges of a graph generated, with half the number of vertices. Each generated graph is in a file named as `v` followed by number of vertices followed by `e` followed by number of edges.

#### hrbac

This benchmark is on Hierachical Role-Based Access Control (HRBAC). Example input data are in subdirectory `input`.

1. to obtain all the statistics for a set of runs, run `./test_hrbac.sh`
2. to measure a single run, run
 `python -m da --rules --message-buffer-size=409600 launcher.da --numr=NUMROLE --numq=NUMOP --q=NUMQUERY --mode=MODE`, where

- `NUMROLE` is the number of roles,
- `NUMOP` is the number of operations for
    - adding/deleting a user (each `NUMOP` times)
    - adding/deleting a role (each `NUMOP/10'` times)
    - adding/deleting a UR pair (each `NUMOP*1.1` times)
    - adding/deleting a RH pair (each `NUMOP/10` times)
- `NUMQUERY` is the number of `AuthorizedUsers` queries, and  
- `MODE` specifies the method used to query authorized users, and can be one of:
    - `'rule'`: using rules with only local predicates, in file `hrbac_trans_rules.da`
    - `'rolerule'`: in addition to the rules for `'rule'`, add a rule that uses a local `role` set, in file `hrab_trans_with_role_rules.da`
    <!-- - `'ROLErule'`: using rules with both local and non-local predicates -->
    - `'transRH'`: using rules with only non-local predicates, in file `hrbac_transRH_rs.da`
    - `'auth_rules'`: using rules for non-recursive set queries `AuthorizedUsers`, in file `hrbac_auth_rules.da`
    - `'authUR'`: introducing set `authorizedUR` as a field so the rule for `'auth_rules'` can be automatically triggered to update `authorizedUR`, in file `hrbac_authorizedUR_rs.da`
    - `'distalgo'`: using DistAlgo high-level queries. in file `hrbac_set.da`
    - `'python'`: using Python comprehensions, in file `hrbac_py.da`

3. to generate your own input data, run the scripts in directory `gen_input` as follows:

    - run `python gen_rbacDB.py` to generate a dataset of user-role (UR) relation and role-hierach (RH) relation of 500 roles.
    - run `python -m da gen_queries.da` to generate a workload of sequence of hrbac queries

#### allrbac

This benchamrk is on the full core and hierarchical RBAC, the description of which can be found [here](https://www3.cs.stonybrook.edu/~stoller/papers/rbac-spec.pdf).

1. to measure the allrbac program, run
 `python -m da --rules --message-buffer-size=409600 launcher.da --numr=NUMROLE --nump=NUMPERM --ac=NUMQUERY`, where

    - `NUMROLE` is the number of roles,
    - `NUMPERM` is the number of permissions, and
    - `NUMQUERY` is the number of `CheckAccess` queries

2. the data provided in directory `input` is for reproducing the experiments in the [PEPM 06 RBAC paper](https://www3.cs.stonybrook.edu/~liu/papers/ImplCRBAC-PEPM06.pdf) with a larger number of roles and permissions,
    1. Exp.1. fix the number of permissions to 1000 and the number of `CheckAccess` queries to 1000, the number of roles varies from 100 to 1000 with a step of 100.
    2. Exp.2. fix the number of roles to 500 and the number of `CheckAccess` queries to 1000, the number of permissions varies from 1000 to 3000 with a step of 100.
    3. Exp.3. fix the number of roles to 500 and permissions to 3000, the number of `CheckAccess` queries varies from 100 to 1000 with a step of 100.

3. to generate your own input data, run the scripts in directory `gen_input` as follows:

    - run `python gen_allrbacDB.py` to generate a dataset of UR, RH, and permission-role (PR) relation
    - run `python -m da --rules --message-buffer-size=409600 gen_allrbacQueries.da`

#### pyAnalysis

This benchmark is on analyzing and transformig Python programs.

- to generate input data, run in directory `data_prepare`
 `python pyast_views.py INPUT`, where input can be a Python module or package.
 The generated data will be in directory `data`.

<!-- 1. to measure all analyses, run `./test_pyanalysis.sh`.   -->
- to measure an analysis or transformation, run
 `python -m da launcher.da ANALYZER DATASET QUERY MODE`, where
    - `ANALYZER` is the analysis or transformation to invokde, and can be one of:
        - `'LoopAnalyzer'`: supporting only one `MODE`: `'rule'`, and `QUERY:`
            - `'loopdepth'`: computing the nesting depth of loops
        - `'LoopToQuery'`: supporting only one `MODE`: `'rule'`, and `QUERY`:
            - `'candidate'`: finding candidate for-loops that can be transformed to comprehensions and printing the potential transformation
            - `'forToCompSimple`: transforming simple for-loops, which is a subset of the candidates, to comprehensions and writing the transformed program to directory `output`
        - `'NumpyAnalyzer'`: supporting only one `MODE`: `'rule'`, and `QUERY`:
            - `'numpy'`: finding for-loops that can be transformed to numpy function calls and printing the potiencal transformation
        - `'ClassAnalyzer'`: supporting all four `MODE`s, and `QUERY`:
            - `'subclass'`: finding and printing class inheritance relation
    - `DATASET` is the name of the package to analyze
    - `MODE` specifies the methods used for the analysis, and can be one of:
        - `'rule'`: using rules
        - `'python'`: using Python nested for-loops and tests
        - `'distalgo'`: using DistAlgo queries
        - `'combine'`: using a combination of rules and DistAlgo queries

#### OpenRuleBench

This benchmark contains Alda and XSB versions of the DBLP, TC (transitive closure), and Wine benchmarks in OpenRuleBench.

- Before running DBLP, uncompress `data_raw/dblp.gz`.

- `data_raw` contains raw data files.  `dblp` and `wine` are copied from OpenRuleBench.  The raw data files for TC are generated as in OpenRuleBench using the programs in `data_prepare`.

- `run.sh` runs the benchmarks and saves the output to files.  The variables `daPgms` and `xsbPgms` control which versions of the benchmarks to run.  `run.sh` calls `ORBtimer.da` to run and time the Alda benchmarks.

- The `TCraw`, `DBLPraw`, and `Wineraw` entries in `daPgms` cause `run.sh` to call `ORBtimer.da` with the option `--mode=raw`.  In this mode, `ORBtimer.da` reads raw data files in `data_raw` and writes the data in pickled form to files in `data_pickle`.  The other Alda programs read the pickled data.
 
- `TCrev` uses the same rules as TC but reversing the two conditions in the recursive rule.

- `Wine_break.da` is an optimized version of `Wine`, optimized using subsumptive transformations, as mentioned in the [arXiv paper about Alda](https://arxiv.org/abs/2205.15204).

- `run.sh` saves output files in the `out` directory.  Names of output files have the form `BENCHMARK_DATASET_ITERATION_TYPE.txt`, where
   - `BENCHMARK` is the version of a benchmark, e.g., `TCrev`.
   - `DATASET` is always `wine` for Wine, is always `dblp` for DBLP, and indicates the graph size and whether the graph has cycles for TC (e.g., `tc_d100_par200_xsb_cyc` indicates a graph with 100 nodes, 200 edges, and cycles).
   - `ITERATION` is the iteration number (`run.sh` runs each benchmark a specified number of times). 
   - `TYPE` is `out` for the program's output and `err` for the program's output to stderr.  Running times are recorded in the `out` files.
-  In addition, query results are saved in files named `BENCHMARK_DATASET_answers.txt`.  The iteration number is omitted, because answers are saved for the first iteration only.

#### PA

This benchmark is for analysis of class hierarchy of Python programs.

- to download the github repos used as datasets for this benchmark, run `python download.py` in the `data_prep` directory.  delete `blender\extern\mantaflow\preprocessed\python\defines.py` (it doesn't contain Python).

- to prepare the data, run `run_pyast_views.sh` in the `data_prep` directory.  This generates data files in directory `data`.

- the versions of the benchmark (PA, PAopt, PAXSB, PAoptXSB, and PAXSBopt) are described in the [arXiv paper about Alda](https://arxiv.org/abs/2205.15204).

- `run.sh` runs the benchmark and saves the output to files.  The variable `pgms` controls which versions of the benchmark to run. `run.sh` calls `PAtimer.da` to run and time the Alda benchmarks.  

- `run.sh` saves output files in the `out` directory.  Names of output files have the same form as for OpenRuleBench, except that `DATASET` identifies a repo (e.g., `numpy`), and results appear in `out` files there are no `answers` files.

- to count the numbers of facts in `astFacts` and `text-rep` in the prepared data, run `../count_facts.sh` in the `data` directory.  the counts are recorded in `line_counts.txt`.

- `io_time.py` measures the time to read facts from `.P` files, pickle them, and write them to files.  after running the benchmark, `__pycache__` contains a `.P` file containing facts for each dataset.  To measure the times for those files, run `python ../io_time.py` in `__pycache__`, then delete all `.pickle` files.  The times are recorded in `io_time.csv`.

#### RBAC

This benchmark is for hierarchical RBAC.  It compares different ways of computing the transitive role hierarchy, as described in the [arXiv paper about Alda](https://arxiv.org/abs/2205.15204) and summarized there in Table 2.

- The programs in `gen_input` are used to generate input files stored in files in `input`. 

- An input file with `np` (mnemonic for "no print") in its name (e.g., `workload_randomnp_50`) contains the same workload as the corresponding input file without `np` (e.g., `workload_random_50`) except print statements have been removed.

- `RBACtimer.da` always reads workload files without `np` in the name.  To use the workloads with `np` in the name, modify the line in `RBACtimer.da` that opens the workload file, or rename the `np` files to remove `np` from the name.

- `run.sh` runs the benchmark on the random workloads and saves the output to files.  The variable `pgms` controls which versions of the benchmark to run. `run.sh` calls `RBACtimer.da` to run and time the Alda benchmarks.  

- `run.sh` saves output files in the `out` directory.  Names of output files have the same form as for PA, except `DATASET` is the size of the workload, specifically, the number of authorized user queries.

#### Extract running times from output files

- to extract running times from a collection of output files generated by running benchmarks in OpenRuleBench, RBAC, or PA, and saves the running times in a single `csv` file, cd to  `OpenRuleBench`, `PA` or `RBAC` and run `python extract_times.py BENCHMARK PROGRAMS DATASETS NUMITER`, where
   - `BENCHMARK` is `"OpenRuleBench"`, `"PA"`, or `"RBAC"` (this should match the directory in which you run the program)
   - `PROGRAMS` is a space-separated list of programs, identified using the same names as in `run.sh`
   - `DATASETS` is a space-separated list of datasets, identified using the same names as in `run.sh`
   - `NUMITER` is the number of iterations
   - The `out` directory should contain output files produced by running each program in `PROGRAMS` `NUMITER` times on each dataset in `DATASETS`.
   - For RBAC or PA, the generated csv file is named `timing_BENCHMARK.csv`.  For OpenRuleBench, it is named `timing_BENCHMARK_PROGRAM.csv`, where `PROGRAM` is `DBLP`, `TC`, `Wine` (they have different datasets, so `extract_times.py` needs to be run separately for each of them, as done in `run_extract.sh`).
   - If `NUMITER` is greater than 1, the mean and standard deviation of the running times of the iterations, not the individual running times, are included in the `csv` file.

- to extract running times from output files for all three of those benchmarks, run `./run_extract.sh`.  That script also provides examples of how to call `extract_times.py`.

#### Check that different versions of a benchmark produce the same results

- to check that different versions of a benchmark produce the same results, run `python check_consistency.py BENCHMARK` in this folder, where `BENCHMARK` is `"OpenRuleBench"`, `"PA"`, or `"RBAC"`.  
- This program looks in `BENCHMARK/out` for files containing saved query results, and checks that for each dataset, the saved query results for different versions of the benchmark are equal.  Note that query results are in `_answers.txt` files for OpenRuleBench and in `_out.txt` files for RBAC and PA.
- For example, `OpenRuleBench/out/DBLP_dblp_answers.txt` and `OpenRuleBench/out/DBLPWxsb_dblp_answers.txt` are compared to check that `DBLP.da` and `DBLPW.P` produce the same results.
- For RBAC and PA, the results in output files from only the first iteration are compared.
- The comparison results are saved in `consistency_BENCHMARK.csv'.