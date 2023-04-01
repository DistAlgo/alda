# Benchmarking experiments for using rules in Alda

This directory contains the source code and data for performance benchmarking. Each subdirectory is a benchmark with its set of  experiements. The timing of compiling each program will be in a subdirectory `timing` of where `python -m da` is run.

#### trans

This benchmark is on computing the transitive closure of a graph. Example input data are in subdirectory `input`.

1. to obtain all the statistics for a set of runs, run `./test_trans.sh`
2. to measure a single run, run
 `python -m da --rule --message-buffer-size=409600 launcher.da --nume=NUMEDGE --mode=MODE`, where

- `NUMEDGE` is the number of edges in the input; to use an example data file in `input`, use a number after `e` in a file name
- `MODE` specifies the method used to compute the transitive closure, and can be one of:
- `'rule'`: using the rules, in file `trans_rules.da`
- `'rev_rule'`: using the same rules as for mode `'rule'` but reversing the two conditions in the second rule, in file `trans_rev_rules.da`
- `'distalgo'`: using DistAlgo high-level queries, in file `trans_set.da`
- `'python'`: using Python comprehensions, in file `trans_py.da`

3. to generate your own input data, run
 `python -m da gen_graph.da` in directory `gen_input; you can update the arugment of `gen_graph` on the last line to be any list of numbers, where each number is the number edges of a graph generated, with half the number of vertices. Each generated graph is in a file named as `v` followed by number of vertices followed by `e` followed by number of edges.

#### hrbac

This benchmark is on Hierachical Role-Based Access Control (HRBAC). Example input data are in subdirectory `input`.

1. to obtain all the statistics for a set of runs, run `./test_hrbac.sh`
2. to measure a single run, run
 `python -m da --rule --message-buffer-size=409600 launcher.da --numr=NUMROLE --numq=NUMOP --q=NUMQUERY --mode=MODE`, where

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
 `python -m da --rule --message-buffer-size=409600 launcher.da --numr=NUMROLE --nump=NUMPERM --ac=NUMQUERY`, where

- `NUMROLE` is the number of roles,
- `NUMPERM` is the number of permissions, and
- `NUMQUERY` is the number of `CheckAccess` queries

2. the data provided in directory `input` is for reproducing the experiments in the [PEPM 06 RBAC paper](https://www3.cs.stonybrook.edu/~liu/papers/ImplCRBAC-PEPM06.pdf) with a larger number of roles and permissions,
1. Exp.1. fix the number of permissions to 1000 and the number of `CheckAccess` queries to 1000, the number of roles varies from 100 to 1000 with a step of 100.
2. Exp.2. fix the number of roles to 500 and the number of `CheckAccess` queries to 1000, the number of permissions varies from 1000 to 3000 with a step of 100.
3. Exp.3. fix the number of roles to 500 and permissions to 3000, the number of `CheckAccess` queries varies from 100 to 1000 with a step of 100.

3. to generate your own input data, run the scripts in directory `gen_input` as follows:
- run `python gen_allrbacDB.py` to generate a dataset of UR, RH, and permission-role (PR) relation
- run `python -m da --rule --message-buffer-size=409600 gen_allrbacQueries.da`

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
