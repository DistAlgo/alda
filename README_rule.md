# README

DA-rules is an extension of DistAlgo with rules.  This implementation supports Python 3.7 but can also run with Python 3.8 and 3.9.

## Installation

1. Install DA-rules by (1) copying or extracting the DA-rules files to a path, designated as `<DArulesROOT>`, in the local file system, and (2) adding `<DArulesROOT>/distalgo` to the front of the `PYTHONPATH` environment variable so that Python can load the `da` module.
2. To use the extension with rules, install [XSB](http://xsb.sourceforge.net/) by: (1) download XSB from <https://sourceforge.net/projects/xsb> --- click "Download" for Windows, or download from "Source(GIT)" for Unix, (2) run the downloaded .exe file for Windows, or follow the instructions in Section 2.1 in the manual (just paragraph 1, items 1 and 4) for Unix, and (3) add the path for the XSB executable to the `PATH` environment variable.

## Using the extension with rules

### An example program that uses rules

Consider computing the [transitive closure](https://en.wikipedia.org/wiki/Transitive_closure) of edges in a graph. Given a graph with a set of edges, each from a vertex to another, the transitive closure is the set of all pairs of vertices such that there is a path from the first vertex to the second vertex following a sequence of edges.

The following DA-rules program computes the transitive closure of the set `e` of edges. Given predicate `edge` that asserts whether there is an edge from a first vertex to a second vertex, rule set `trans_rules` defines predicate `path` that asserts whether there is a path from a first vertex to a second vertex by following the given edges.

```python
def rules(name=trans_rules):
  path(x,y), if_(edge(x,y))
  path(x,y), if_(edge(x,z), path(z,y))

e = {(7,2), (7,3), (2,3), (2,4), (7,5), (3,6)}
print(infer(rule=trans_rules, bindings=[('edge',e)], queries=['path']))
```

The first rule says that there is a path from `x` to `y` if there is an edge from `x` to `y`. The second rule says that there is a path from `x` to `y` if there is an edge from `x` to `z` and there is a path from `z` to `y`.
Function `infer` uses rule set `trans_rules`, takes `edge` to be true for edges in `e`, and returns the set of pairs for which `path` is true.

### Specification of rules

A set of rules can be specified using a rule set of the following form:

```python
def rules(name=rsname):
  rule+
```

`rsname` is the name of the rule set and uses the same naming convention as
Python identifiers;`name=` is optional. `rule+` is one or more rules.

#### Rules

Each rule is of the following form, indicating that if `condition_1` through `condition_n` all hold, then `conclusion` holds:

```python
  conclusion, if_(condition_1, condition_2, ..., condition_n)
```

Each condition and conclusion in a rule is an *assertion* of the following form,  possibly preceded with `not`:

```python
  pred(arg_1,...,arg_m)
```

- `pred` is a predicate name. A predicate can be a global variable, object field, or local variable of a rule set`.
- `arg_k` can be a variable name, a constant, or wildcard `_` indicating that its value does not mattter. A constant can be int numbers, `None`, `True`, `False`, or quoted strings. All variables in the conclusion must be in a condition.

In a rule set, predicates not in any conclusion are called *base predicates* of the rule set, and the other predicates are called *derived predicates* of the rule set.

### Inference using rules

We can do inference using rules by calling a built-in inference function `infer`, of the following form

```python
infer(rule=rsname, 
      bindings=[('pred_1',sexp_1),...,('pred_i',sexp_i)], 
      queries=['query_1',...,'query_j'])
```

- `rsname` is the name of a rule set.
- `bindings` is an optional keyword argument that specifies the assignment to each base predicate `pred_k` in the rule set with the value of a set-valued expression `sexp_k`. Each predicate name `pred_k` needs to be a quoted string. If `pred_k` is non-local to rule set `rsname`, the assignment to `pred_k` can be omitted.
- `queries` is an optional keyword argument that specifies the queries to be made. Each `query_k` needs to be a quoted string of the form `pred(arg_1,...,arg_m)`, where `pred` is a predicate name in rule set `rsname` and `arg_k` is a constant or a wildcard `_`. Query `pred(_,...,_)` can be abbreviated as `pred`. When `queries` is omitted, `infer` treats all derived predicates as queries.
- Return value: For each value `k` from 1 to `j`, return the result of `query_k` as the `k`th component of the return value. The result of a query with `l` distinct variables that are not constants is a set of tuples of `l` components, one for each of the distinct variables in their order of first occurrence in the query. When `l` equals 1, the set of tuples is reduced to a set of elements in the tuples.

#### Automatic maintainence

When using rules with only non-local predicates, the derived predicates are automatically updated when any of the base predicate is updated, without explicit calls to `infer`.

### Running the program

Usage: `python -m da --rule <filename>`  
where `<filename>` is the name of a DA-rules program.

Save the example program to a file, say named `trans.da`, then running the following command
`>>> python -m da --rule trans.da`
produces the output

```python
{(7, 4), (2, 4), (7, 3), (2, 3), (7, 6), (2, 6), (7, 2), (3, 6), (7, 5)}
```

### Running the experiments

In the `examples` directory, locate the source code of the experiments discussed in the paper. All the sections mentioned below are from the paper.

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
 `python pyast_views.da INPUT`, where input can be a Python module or a Python package
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
