# README

DA-rules is an extension of DistAlgo with rules and constraints.  This implementation requires Python 3.7.

## 1. Installation
1. Install DA-rules by (1) copying or extracting the DA-rules files to a path, designated as `<DArulesROOT>`, in the local file system, and (2) adding `<DArulesROOT>/distalgo` to the front of the `PYTHONPATH` environment variable so that Python can load the `da` module.
2. To use the extension with rules, install [XSB](http://xsb.sourceforge.net/) by: (1) download XSB from the [SVN repository](https://sourceforge.net/p/xsb/src/HEAD/tree/), (2) compile and install XSB following the instructions in the 2nd chapter of the [manual](http://xsb.sourceforge.net/manual1/manual1.pdf), and (3) add the path for the XSB executable to the `PATH` environment variable.
3. To use the extension with constraints, (1) install MiniZinc from https://www.minizinc.org/software.html, (2) add the path for MiniZinc to the `PATH` environment variable, and (3) install the MiniZinc Python interface by running `pip install minizinc`.


## 2. Using the extension with rules
### An example program that uses rules
The following rule set defines the [transitive closure](https://en.wikipedia.org/wiki/Transitive_closure) of edges in a graph. Given a predicate `edge` that asserts whether there is an edge from a first vertex to a second vertex, the transitive closure defines a predicate `path` that asserts whether there is a path though which a first vertex can reach a second vertex by following the given edges.
```python
def rules(name='trans_rs'):
  path(x,y), if_(edge(x,y))
  path(x,y), if_(edge(x,z), path(z,y))

trans = infer(rule='trans_rs', bindings=[('edge',E)], queries=['path'])
```
The first rule says that there is a path from `x` to `y` if there is an edge from `x` to `y`. The second rule says that there is a path from `x` to `y` if there is an edge from `x` to `z` and there is a path from `z` to `y`. Given a set `edge` of edges, the transitive closure of `edge` is the set `path` of all pairs of vertices `x` and `y` such that there is a path from `x` to `y`.

### Specification
A set of rules can be specified easily using the syntax of a Python function:
```python
def rules(name='rsname'):
  rule+
```
The function must be named `rules`, with a parameter `name`, which defines the name of the rule set. The name serves as the unique identifier of the rule set and uses the same naming convention as Python identifiers. The body of the rule function is a set of rules.
#### rule
Each rule is a Datalog rule of the form below, indicating that if `condition_1` through `condition_n` all hold, then `conclusion` holds.
```python
  conclusion, if_(condition_1, condition_2, ..., condition_n)
```
Each condition and conclusion in a rule is an *assertion* of the form
```python
  pred(arg_1, ..., arg_m)
```
- `pred` is a predicate name. Each predicate can be a global variable, object field or local variable of the rule set `rsname`.
- `arg_k` can be a variable name, a constant or an underscore `_` indicating an anonymous variable. A constant can be int numbers, `None`, `True`, `False` or quoted strings. An anonymous variable is a variable referred to only once in a rule so it does not need to be named. All variables in the conclusion must be in a condition.

In a rule set, predicates not in any conclusion are called *base predicates* of the rule set, and the other predicates are called *derived predicates* of the rule set.

### Inference with rules
We can infer with a rule set by calling the built-in function `infer` of the following form:
```python
infer(rule='rsname', 
      bindings=[('pred_1',sexp_1),...,('pred_2',sexp_2)], 
      queries=['query_1',...,'query_j'])
```
- `rule` is the name of a rule set.
- `bindings` is an optional keyword argument that specifies the assignment to each base predicate `pred_k` in the rule set with a set-valued expression `sexp_k`. Each predicate name `pred_k` needs to be written as a quoted string. If `pred_k` is non-local to rule set `rsname`, the assignment to `pred_k` can be omitted.
- `queries` is an optional keyword argument that specifies the queries to be made by calling the function. Each `query_k` must be written as a quoted string of the form `pred(arg_1, ..., arg_m)`, where `pred` is a predicate name in rule set `rsname` and `arg_k` can be a constant or an underscore `_` indicating a distinct variable to be inferred. Query `pred(_, ..., _)` can be abbreviated as `pred`. When `queries` is omitted, the `infer` function treats all the derived predicates as queries.
- The `infer` function returns a set for each query in the order of specifying `queries`.

#### Automatic maintainence
When using rules with only non-local predicates, the derived predicates are automatically updated without any explicit calls to `infer` when any of the base predicate is updated.


### Running a program with rules
Usage: `python3 -m da --rule <filename>`  
where `<filename>` is the name of a DA-rules script.

### Running the experiments

In the `examples` directory locates the source code of the experiments discussed in the paper. All the sections mentioned below are from the paper.

#### Trans
This example computes the transitive closure of a graph as discussed in section 2. The input data used in the paper is included in the repository.
1. to get all the statistics in section 7.3 Transitive closure, run `./test_trans.sh`
2. to run a single round of trans, call  
	`python3 -m da --rule --message-buffer-size=409600 trans.da --nume=NUMEDGE --mode=MODE`, where
	- `NUMEDGE` is the number of edges of input data, and  
	- `MODE` can take value from:
		- `'rule'`: using the rules in section 4.2 for computing transitive closure,
		- `'rev_rule'`: using the same rule as the program of `'rule'` but reversing the twoconditions in the recursive rule.
		- `'distalgo'`: using DistAlgo high-level queries for set queries as introduced in section 7.2
		- `'python'`: using Python comprehensions for set queries as introduced in section 7.2
3. the data provided in the `input` folder is those used when generating the graphs in the paper
4. to generate your own input data  
	run `gen_input.py` in `gen_input` folder, and move the results in `./gen_input/input` to `./input`
5. the output of the analysis will be in the `output` folder

#### Hrbac
This example is about hierachical role-based access control (HRBAC) discussed in section 2.
The input data used in the paper is included in the repository.
1. to get all the statistics in section 7.4 Hierarchical RBAC of the paper, run `./test_hrbac.sh`
2. to run a single round of hrbac, call  
	`python3 -m da --rule --message-buffer-size=409600 hrbac.da  --numr=NUMROLE --numq=NUMOP --q=NUMQUERY --mode=MODE`, where
	- `NUMROLE` is the number of roles,  
	- `NUMOP` is the basic number of operations that:
		- adding/deleting user (each `NUMOP` times), 
		- adding/deleting role (each `NUMOP/10'` times), 
		- adding/deleting UR pair (each `NUMOP*1.1` times), 
		- adding/deleting RH pair (each `NUMOP/10` times)
	- `NUMQUERY` is the number of `AuthorizedUsers` query, and  
	- `MODE` specifies the method used for quering the authorized users, and can take value from:
		- `'rule'`: using rules with only local predicates as introduced in section 4.2
		- `'rolerule'`: in addition to the previous rules in program `'rule'`, add a rule that uses a local `role` set as introduced in section 4.2
		- `'ROLErule'`: using rules with both local and non-local predicates as introduced in section 4.3
		- `'transRH'`: using rules with only non-local predicates as introduced in section 4.1
		- `'auth_rules'`: using rules for non-recursive set queries `AuthorizedUsers` as introduced in section 4.4
		- `'authUR'`: introducing set `authorizedUR` as a field so the previous rule in program `'auth_rules'` can be automatically triggered to update `authorizedUR` as introduced in section 4.4
		- `'python'`: using Python comprehensions for set queries as introduced in section 7.2
		- `'distalgo'`: using DistAlgo high-level queries for set queries as introduced in section 7.2
3. the data provided in the `input` folder is those used when generating the graphs in the paper
4. to generate your own input data  
	run `gen_input.py` in `gen_input` folder, and move the results in `./gen_input/input` to `./input`.
5. the output of the analysis will be in the `output` folder

#### pyAnalysis
This folder contains the examples about analysis of Python programs discussed in section 7.5 and 7.6.
- to generate input data, run  
	`python3 -m da prepare_data.da PACKAGE_FOLDER`  
	the generated data will be in `./data` folder.

##### Program analysis
This example computes the inheritance information of Python programs as discussed in section 7.5.
1. to get all the statistics in section 7.5 Program analysis, run `./test_pyanalysis.sh`.  
2. to run the analysis of getting the inheritance information, call  
	`python3 -m da ast_analysis_rule.da DATASET MODE`, where
	- `DATASET` is the name of the package to analyasis,  
	- `MODE` specifies the methods used for computing basic inheritance information, and can take value from:
		- `'rule'`: using the rules as introduced in section 7.5
		- `'python'`: using Python nested for loops and tests as introduced in section 7.5
		- `'distalgo'`: using DistAlgo queries
		- `'combine'`: using a combination of rules and DistAlgo queries
3. the output of the analysis will be in the `output` folder

##### Transforming loops to comprehensions
This example performs a series of analysis on Python for-loops as discussed in section 7.6.
1. to run an analysis, call  
	`python3 -m da ast_analysis_rule.da DATASET QUERY`, where
	- `DATASET` is the name of the package to analyasis,  
	- `QUERY` specifies the analysis to perform, and can take value from:
		- `'loopdepth'`: compute the depth of for-loops
		- `'candidate'`: identify candidate for-loops that might be transformable to comprehensions
		- `'forToCompSimple'`: run the basic transformer to translate for-loops into comprehensions
2. the output of the analysis will be in the `output` folder

## 3. Using the extension with constraints

### An example program that uses constraints
<table style="width:100%">
  <tr>
	<td><img src="https://user-images.githubusercontent.com/2973457/80774269-82595000-8b2a-11ea-84de-99c5ac8b963c.png" width="750px"/></td>
	<td>Consider the graph shown on the left. The red vertices form a minimum <a href="https://en.wikipedia.org/wiki/Vertex_cover">vertex cover</a> of the graph. A vertex cover of a graph is a set of vertices in the graph such that each edge of the graph is attached to at least one vertex in the set. The minimum vertex cover problem is to find a vertex cover with the minimum number of vertices. The problem can be specified as a constraint problem in DA-rules as shown below.</td>
  </tr>
</table>

```python
def constraint(name= 'vertex_cover', pars={vertex, edge}):

  # Parameters: 
  vertex: set[int]  # vertices as a set of integers
  edge: dict(key=(vertex,vertex), val=ints(0,1))  # edges as an adj matrix
  
  # Decision variables: 
  vc: dict(key=vertex, val=ints(0,1))  # vertex cover as a dict too
  nvertex: int = sum(vc)  # number of vertices, and objective function

  # Constraints: each edge has at least one end in the vertex cover
  cover = each(i in vertex, j in vertex, has=
               edge[i,j] == 0 or vc[i] == 1 or vc[j] == 1)
  
  # Return: any vertex cover with the minimum number of vertices
  return anyof((vc, nvertex), cover, to_min(nvertex))
    
v = set(ints(1,6))
e = [[0,1,1,0,0,0],
     [1,0,1,1,1,1],
     [1,1,0,0,0,0],
     [0,1,0,0,0,0],
     [0,1,0,0,0,0],
     [0,1,0,0,0,0]]

result = query(constraint='vertex_cover', vertex=v, edge=e)
print(result['vc'])  # value of decision variable vc in solution
print(result['nvertex'])  # value of decision variable nvertex
```

### Constraint satisfaction problems

A Constraint Satisfaction Problem (CSP) is defined by a triple `<X,D,C>` where `X` is a set of variables, `D` is a set of domains respective to the variables, and `C` is a set of constraints. Variables can be subdivided into parameters and decision variables, where parameters are variables whose values are given, and decision variables are those whose values are to be decided.
Solving a CSP is to find a solution, which is an assignment to decisions variables with values in their respective domains, such that all the constraints are satisfied.

Constraint Optimization Problem (COP) generalizes CSP with an objective, which is a function of some variables. Solving a COP is to find an optimal solution, which is an assignment of values to decision variables such that the value of the objective is minimized or maximized as required by the problem and all the constraints are satisfied.

The vertex cover problem is a COP with parameters `vertex` and `edge`, decision variables `vc` and `nvertex` where `nvertex` holds the value of the objective function, and constraint `cover`. The problem is to find a value of `vc` that minimizes the value of `nvertex` and satisfies `cover`.

### Specifying the problem
A CSP can be specified easily using the syntax of a Python function:
```python
def constraint(name, pars)
```
The function must be named `constraint`, with two parameters `name` and `pars`. 
- `name` is the name of the problem, which is `'vertex_cover'` in the example.
The name serves as the unique identifier of the problem and uses the same naming convention as Python identifiers.
- `pars` is a set containing the parameters whose values need to be given when instantiating the problem. In the example `vertex` and `edge` are parameters.

Inside the body of the constraint function, 3 kinds of information need to be specified: variable domains, constraints, and the return value.

#### Variables
There are two types of variables: parameters and decision variables.
1. Parameters are variables whose values must be known when the problem is instantiated.
2. Decision variables are variables whose values are to be decided. 
	
	For some problems such as Sudoku, a partially filled playboard can be passed in as a parameter. Its empty cells are indicated by `_` and will be assigned values when the problem is solved. Parameters with empty cells are also treated as decision variables.
- Variables need to be explicitly declared with domain information. The syntax for specifying the domain of a variable is of the following form, where `= value` is optional:
	```python
	variable: domain = value
	```
  - The domain can be one of 5 kinds:
	1. basic domain: `int`, `float`, `str`, or `bool`.
	2. bounded int domain: `ints(lb,ub)`
		- `ints(lb,ub)` represents an `int` domain taking values from lowerbound `lb` to upperbound `ub` (inclusive),
		- `lb` and `ub` are of `int` or bounded int domain.
	3. map domain: `dict(key=domain, val=domain)`. A map domain can be viewed as a multi-dimensional array. `key` specifies the domain of each dimension, which must be of `int` or bounded int domain. `value` must be of `int`, bounded int, or `float` domain.
	4. set domain: `set[domain]`.  `domain` can be of `int`, bounded int, or `float` domain. Set variables can only be parameters.
	5. variable: A variable name can be used as domains representing the domain of itself.

#### Constraints
Constraints are the conditions that must be satisfied when assigning values to decision variables. There are two ways of specifying a constraint:
1. in the form of an assignment statement: `c_1 = bexp`, where 'c_1' is the name of the constraint, or
2. in the form of a function definition: 
	```python
	def c_2():
		bexp1
		bexp2
		...
	```
	Expressions inside the function body are implicitly the conjuncts of logical conjunction, where `c_2` is the name of the conjunction.  Defining constraints this way can be simpler by omitting the `and` operator when there are multiple conjuncts.
- Theoretically, `bexp` can be any Boolean-valued expression. But currently only expressions of the following forms are supported:
	1. universal quantification: It evaluates to `True` iff for all combinations of values of variables that satisfy all membership clauses `vi in sexpi`, the condition `bexp` evaluates to `True`. A membership clause `v in sexp` is `True` if value `v` is a member of the set value of `sexp`,
		- `each(v1 in sexp1, ..., vk in sexpk, has= bexp)`
	2. existential quantification: It evaluates to `True` iff for some combinations of values of variables that satisfy all membership clauses `vi in sexpi`, the condition `bexp` evaluates to `True`,
		- `some(v1 in sexp1, ..., vk in sexpk, has= bexp)`
	3. binary expression with a comparison operator: `==`, `!=`, `<`, `<=`, `>`, `>=`
	4. global constraint `alldiff`. `alldiff` is a builtin constraint of one of the form:
		- `alldiff(sexp)`,
		- `alldiff(exp, v1 in sexp1, ..., vk in sexpk, bexp)`. 

	   It evaluates to `True` iff
		- all items in `sexp`, for the first case
		- all items in the set of values of `exp` for all combinations of values of variables that satisfy all membership clauses `vi in sexpi` and condition `bexp`, for the second case

	   take pairwisely different values.
	5. logical operators (`and`, `or`, `not`) applied `bexp`'s

#### Return
The return value of a constraint problem is specified in the form of a `return` statement.  As described above, CSPs and COPs are different so their returns are in different forms:
1. CSP: `anyof(variables, c_1, ..., c_k)`
2. COP: `anyof(variables, c_1, ..., c_k, opt(objective))`
- `variables` is a decision variable or a tuple of decision variables whose values are to be returned from solving the constraint problem.
- `c_1, ..., c_k` are names of constraints to be satisfied.
- `opt(objective)` specifies the desired optimization of the objective value `objective`, where `opt` can be `to_max` or `to_min`, denoting maximization or minimization, respectively.


### Solving the problem
After specifying the problem, call the following function to solve the problem:
```python
query(constraint, **kwargs)
``` 
- `constraint` is the name of the constraint problem
- `kwargs` are keyword arguments for passing in values of parameters of the constraint problem. The keys are names of parameters
- When passing in an argument, if the argument name is 
	- in the same scope as calling `query`, or 
	- an instance variable in a class, or
	- a global variable,

  that argument can be omitted from the call.
- The return value of calling `query` is a dictionary, whose keys are names of decision variables in the return of the constraint problem. If the problem is a COP, an additional key `objective` is also returned if not already specified in the return, and is the optimal value of the objective. Additionally, the statistics of solving the problem are also returned under key `statistics`. Detailed explanation of all items in the statistics can be found [here](https://minizinc-python.readthedocs.io/en/latest/_modules/minizinc/result.html).

### Running the program
Usage: `python3 -m da --constraint <filename>`

Save the example program to a file, say named `vertex_cover.da`, then running following command produces the output:

`>>> python3 -m da --constraint vertex_cover.da`
```python
[0, 1, 1, 0, 0, 0]
2
```
Some examples are given in the `examples/constraints` directory.
