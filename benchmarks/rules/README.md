# Experiments

In this directory, locate the source code for performance experiments

#### trans

This example is for computing the transitive closure of a graph as discussed in section 2. The input data used in the paper is included in the repository.

1. to obtain all the statistics in section 7.3 Transitive closure, run `./test_trans.sh`
2. to measure a single round of transitive closure, run
 `python -m da --rule --message-buffer-size=409600 launcher.da --nume=NUMEDGE --mode=MODE`, where

- `NUMEDGE` is the number of edges in the input, and  
- `MODE` specifies the methods used for computing the transitive closure, and can be one of:
- `'rule'`: using the rules in section 4.2
- `'rev_rule'`: using the same rule as the program for `'rule'` but reversing the two conditions in the recursive rule
- `'distalgo'`: using DistAlgo high-level queries as introduced in section 7.2
- `'python'`: using Python comprehensions as introduced in section 7.2

3. the data provided in the `input` folder is those used when generating the graphs in the paper
4. to generate your own input data,
 run `gen_graph.da` in the `gen_input` folder with command `python -m da gen_graph.da`
5. the timing of compiling each program will be in the `timing` folder

#### hrbac

This example is for Hierachical Role-Based Access Control (HRBAC) discussed in section 2.
The input data used in the paper is included in the repository.

1. to obtain all the statistics in section 7.4 Hierarchical RBAC, run `./test_hrbac.sh`
2. to measure a single round of HRBAC, run
 `python -m da --rule --message-buffer-size=409600 launcher.da --numr=NUMROLE --numq=NUMOP --q=NUMQUERY --mode=MODE`, where

- `NUMROLE` is the number of roles,
- `NUMOP` is the number of operations for
- adding/deleting a user (each `NUMOP` times)
- adding/deleting a role (each `NUMOP/10'` times)
- adding/deleting a UR pair (each `NUMOP*1.1` times)
- adding/deleting a RH pair (each `NUMOP/10` times)
- `NUMQUERY` is the number of `AuthorizedUsers` queries, and  
- `MODE` specifies the method used for quering authorized users, and can be one of:
- `'rule'`: using rules with only local predicates as introduced in section 4.2
- `'rolerule'`: in addition to the previous rules in the program for `'rule'`, add a rule that uses a local `role` set as introduced in section 4.2
  <!-- - `'ROLErule'`: using rules with both local and non-local predicates as introduced in section 4.3 -->
- `'transRH'`: using rules with only non-local predicates as introduced in section 4.1
  <!-- - `'auth_rules'`: using rules for non-recursive set queries `AuthorizedUsers` as introduced in section 4.4 -->
- `'authUR'`: introducing set `authorizedUR` as a field so the previous rule in the program for `'auth_rules'` can be automatically triggered to update `authorizedUR` as introduced in section 4.4
- `'python'`: using Python comprehensions as introduced in section 7.2
- `'distalgo'`: using DistAlgo high-level queries as introduced in section 7.2

3. the data provided in the `input` folder is those used when generating the graphs in the paper
4. to generate your own input data, run the scripts in the `gen_input` folder as follows:

- run `gen_rbacDB.py` to generate a dataset of user-role (UR) relation and role-hierach (RH) relation of 500 roles.
- run `python -m da gen_queries.da` to generate a workload of sequence of hrbac queries

5. the timing of compiling each program will be in the `timing` folder

#### allrbac

This example is on the full core and hierarchical RBAC, the description of which can be found [here](https://www3.cs.stonybrook.edu/~stoller/papers/rbac-spec.pdf).

1. to measure the allrbac program, run
 `python -m da --rule --message-buffer-size=409600 launcher.da --numr=NUMROLE --nump=NUMPERM --ac=NUMQUERY`, where

- `NUMROLE` is the number of roles,
- `NUMPERM` is the number of permissions, and
- `NUMQUERY` is the number of `CheckAccess` queries

2. the data provided in the `input` folder is for reproducing the experiments in the [PEPM 06 RBAC paper](https://www3.cs.stonybrook.edu/~liu/papers/ImplCRBAC-PEPM06.pdf) with a larger number of roles and permissions,
1. Exp.1. fix the number of perissions to 1000 and the number of `CheckAccess` queries to 1000, the number of roles varies from 100 to 1000 with a step of 100.
2. Exp.2. fix the number of roles to 500 and the number of `CheckAccess` queries to 1000, the number of permissions varies from 1000 to 3000 with a step of 100.
3. Exp.3. fix the number of roles to 500 and permissions to 3000, the number of `CheckAccess` queries varies from 100 to 1000 with a step of 100.
3. to generate your own input data, run the scripts in `gen_input` folder as follows:

- run `gen_allrbacDB.py` to generate a dataset of UR, RH, and permission-role (PR) relation
- run `python -m da --rule --message-buffer-size=409600 gen_allrbacQueries.da`

#### pyAnalysis

This folder contains the examples for analyzing Python programs as discussed in section 7.5 and 7.6.

- to generate input data, run in the `data_prepare` folder
 `python pyast_views.py INPUT`, where input can be a Python module or a Python package
 the generated data will be in `data` folder.

<!-- ##### Program analysis -->
<!-- This example computes the inheritance information of Python programs as discussed in section 7.5. -->
<!-- 1. to obtain all the statistics in section 7.5 Program analysis, run `./test_pyanalysis.sh`.   -->
- to measure the analysis for getting the inheritance information, run
 `python -m da launcher.da ANALYZER DATASET QUERY MODE`, where
    - `ANALYZER` is the analyzer to invokde, and can be one of:
        - `'LoopAnalyzer'`: supporting only one `MODE`: `'rule'`, and `QUERY:`
            - `'loopdepth'`: computing the depth of loops and
        - `'LoopToQuery'`: supporting only one `MODE`: `'rule'`, and `QUERY`:
            - `'candidate'`: finding candidate for-loops that can be transformed to comprehensions and printing the potential transformation
            - `'forToCompSimple`: transforming simple for-loops, which is a subset of the candidates, to comprehensions and writing the converted files to the `output` folder
        - `'NumpyAnalyzer'`: supporting only one `MODE`: `'rule'`, and `QUERY`:
            - `'numpy'`: finding for-loops that can be transformed to numpy function calls and printing the potiencal transformation
        - `'ClassAnalyzer'`: supporting all four `MODE`s, and `QUERY`:
            - `'subclass'`: finding and printing the class inheritance relation
    - `DATASET` is the name of the package to analyasis,  
    - `MODE` specifies the methods used for computing basic inheritance information, and can be one of:
        - `'rule'`: using rules as introduced in section 7.5
        - `'python'`: using Python nested for-loops and tests as introduced in section 7.5
        - `'distalgo'`: using DistAlgo queries
        - `'combine'`: using a combination of rules and DistAlgo queries
<!-- 2. the timing of compiling the program will be in the `timing` folder -->

<!-- ##### Transforming loops to comprehensions
This example performs a series of analysis on Python for-loops as discussed in section 7.6.
1. to  an analysis, run
	`python -m da ast_analysis_rule.da DATASET QUERY`, where
	- `DATASET` is the name of the package to analyze,
	- `QUERY` specifies the analysis to perform, and can be one of:
		- `'loopdepth'`: computing the depth of for-loops
		- `'candidate'`: identifying candidate for-loops that might be transformable to comprehensions
		- `'forToCompSimple'`: running the basic transformer to transform for-loops into comprehensions
2. the output of the analysis will be in the `output` folder -->