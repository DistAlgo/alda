# README

DA-rules is an extension of DistAlgo with rules and constraints.  This implementation requires Python 3.7.

## 1. Installation
1. Install DA-rules by (1) copying or extracting the DA-rules files to a path, designated as `<DArulesROOT>`, in the local file system, and (2) adding `<DArulesROOT>/distalgo` to the front of the `PYTHONPATH` environment variable so that Python can load the `da` module.
2. To use the extension with rules, install XSB from http://xsb.sourceforge.net/.
3. To use the extension with constraints, (1) install MiniZinc from https://www.minizinc.org/software.html, (2) add the path for MiniZinc to the `PATH` environment variable, and (3) install the MiniZinc Python interface by running `pip install minizinc`.


## 2. Using the extension with rules
- A set of Datalog rules can be written as easy as a Python function
  ```python
	def rules(name='name_of_rule'):
		conclusion_1, if_(condition_1, condition_2, ...)
		conclusion_2, if_(conclusion_1, condition_3, ...)

	result = infer(rule='name_of_rule', 
                       bindings=[('condition_1',variable_1),('condition_2',variable_2)],
                       queries=['conclusion_2'])
  ```
- The function must be named by `rules`, with an argument `name` indicating the unique identifier of the rule set.
- Inside the function block, Datalog rules of form `conclusion :- condition_1, condition_2, ....` can be written as `conclusion_1, if_(condition_1, condition_2, ...)`. Each conclusion and condition are predicates of the form `predicate(var_1, var_2, ...)`
- Datalog rules can be used to easily write database alike queries and recursion. For example, the following rule set can be used to computing the [transitive closure](https://en.wikipedia.org/wiki/Transitive_closure) of a graph:
	```python
	def rules(name='transitive_closure'):
		path(x,y), if_(edge(x,y))
		path(x,y), if_(edge(x,z), path(z,y))
	```
- Understanding rules with Python thinking
	- Each predicate on the right hand side of the rule set can be seen as a membership check of set. For example, `edge(x,y)` returns `True` if tuple `(x,y)` is in the set `edge`. 
	- Between different conditions on the right hand side of a rule is logic `and` relation. 
	- And each predicate on the left hand side can be seen as a set add operation that for the rule `path(x,y), if_(edge(x,y))`, if there is tuple `(x,y)` in `edge`, then add `(x,y)` to set `path`. 
	- The rules in a rule set will be executed repeatedly until no changes can be made.
	- Although this is not exactly how Datalog engine works, the idea is the most equivalent correspondence in Python.
- Infer with rules:
	```python
	result_1, result_2 = infer(rule='name_of_rule', 
                               bindings=[('condition_1',variable_1),('condition_2',variable_2)],
                               queries=['conclution_1','conclusion_2'])
	```

	call function `infer` with 
	- parameter `rule` specifies the name of rule you want to use,
	- parameter `bindings` is a list of tuples that binds predicate with a variable of set type in Python program.
		- the first element is the name of a predicate in the rule set
		- the second element is the name of a variable in Python program
		- when a variable is defined in the same scope as calling of the `infer` function or is a global variable, and the name of the variable is the same as the predicate it is to be bound, the binding of this pair of predicate and variable can be omitted.
	- parameter `queries` is a list specifying the predicates you want to return from calling the `infer` function. It can be any predicate appears in a rule set.
	- the return value of the `infer` function is a tuple of values for the required predicates specified in `queries`. Just the same as getting return values from calling functions that return multiple values.

### Example programs that use rules

#### Trans
This problem computes the transitive closure of a graph
1. USAGE:  
	to get all the statistics in the graph, run `./test_trans.sh`.  
	to run a single round of trans, call  
	`python3 -m da --rule --message-buffer-size=409600 trans.da --nume=NUMEDGE --mode=MODE`  
	where `NUMEDGE` is the number of edges of input data, and  
	`MODE` can take value from: `'rule'`, `'rev_rule'`, `'distalgo'` and `'python'`.
2. the data provided in the `input` folder is those used when generating the graphs in the paper
3. to generate your own input data  
	run `gen_input.py` in `gen_input` folder, and move the results in `./gen_input/input` to `./input`

#### Hrbac
This example is about hierachical role-based access control.
1. USAGE:  
	to get all the statistics in the graph, run `./test_hrbac.sh`.  
	to run a single round of hrbac, call  
	`python3 -m da --rule --message-buffer-size=409600 hrbac.da  --numr=NUMROLE --numq=NUMOP --q=NUMQUERY --mode=MODE`  
	where `NUMROLE` is the number of roles,  
	`NUMOP` is the basic number of operations that: 
	* adding/deleting user (each `NUMOP` times), 
	* adding/deleting role (each `NUMOP/10'` times), 
	* adding/deleting UR pair (each `NUMOP*1.1` times), 
	* adding/deleting RH pair (each `NUMOP/10` times)

	`NUMQUERY` is the number of `AuthorizedUsers` query, and  
	`MODE` can take value from: `'rule'`, `'rolerule'`, `'transRH'`, `'python'`, and `'distalgo'`.
2. the data provided in the `input` folder is those used when generating the graphs in the paper
3. to generate your own input data  
	run `gen_input.py` in `gen_input` folder, and move the results in `./gen_input/input` to `./input`.

#### pyAnalysis
This example is about analysis of Python programs.
1. USAGE:  
	to get all the statistics in the graph, run `./test_pyanalysis.sh`.  
	to run a single analysis, call  
	`python3 -m da ast_analysis_rule.da DATASET MODE QUERY`  
	where `DATASET` is the name of the package you want to analyasis,  
	`MODE` can take value from: `rule`, `python`, `distalgo` and `combine`, and  
	`QUERY` can take value from: `subclass`, and `class`   
	the output of the analysis will be in the `output` folder
2. to generate input data  
	run `python3 -m da prepare_data.da PACKAGE_FOLDER`.  
	generated data will be in `./data` folder.


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

A Constraint Satisfaction Problem (CSP) is defined by a triple `<X,D,C>` where `X` is a set of variables, `D` is a set of domains respective to the variables and `C` is a set of constraints. Variables can be further subdivided into parameters and decision variables where parameters are variables whose values are known before solving the problem while decision variables are those whose values are to be decided.
The goal of solving a CSP is to find a solution, which is an assigment to all variables with values in their respective domains, such that all the constraints are satisfied.

Constraint Optimization Problem (COP) generalizes CSP with an objective, which is a function of some variables. The goal of solving a COP is to find an optimal solution, which is an assignment of variables such that the objective is minimized or maximized depending on the setting of problem while all the constraints are satisfied.

The vertex cover problem is a COP with parameters `vertex` and `edge`, decision variables `vc` and `nvertex` where `nvertex` takes value from the objective function, and constraint `cover`. The goal of the problem is to find an optimal solution that the objective is minimized.

### Specifying the problem
A constraint satisfaction problem can be specified as easily as a function.
```python
def constraint(name, pars)
```
The function must be named `constraint`, with two parameters `name` and `pars`. 
- `name` is the name of the problem, which is `'vertex_cover'` in the example.
The name serves as the unique identifier of the problem and shares the same naming convention as python identifiers.
- `pars` is a set containing the parameters whose values need to be given when instantiating the problem. In the example `vertex` and `edge` are parameters.

Inside the body of the constraint function, 3 kinds of information need to be defined: variables, constraints and the return value.

#### Variables
There are two types of variables: parameters and decision variables.
1. Parameters are variables whose values must have known when the problem is instantiated. Parameters must be explicitly specified when defining the problem, 
2. Decision variables are variables whose values are to be decided during solving the problem. 
	
	For some problems such as Sudoku, a partial filled playboard will be passed in as a parameter. Its empty cells are indicated by `_` and will be assigned with values when solving the problem. Parameters with empty cells are also treated as decision variables.
- Variables need to be explicitly declared with domain information. The syntax of variable definition is in the form of type annotation, the value of which is optional:
	```python
	variable: domain = value
	```
  - The domain of a variable can be
	1. basic domains: `int, float, str, bool`,
	2. bounded `int` domain: `ints(lb,ub)`
		- `ints(lb,ub)` presents a `int` domain taking value from lowerbound `lb` to upperbound `ub` (included),
		- `lb` and `ub` are of `int/ints` domain,
	3. map domain: `dict(key=domain, val=domain)`. The map domain can be viewed as an array. `key` defines the domain of the dimension and must be of `int/ints` domain or tuple of `int/ints` for multidimensional arrays. `value` must be of `int/ints` or `float` domain,
	4. `set`: A `set` can be defined precisely by `set[domain]` where `domain` can be of `int/ints` or `float` domain. Set varaibles can only be parameters.
	5. variables can be used as domains presenting the domains of themselves.

#### Constraints
Constraints are the conditions that must be satisfied when assigning values to decision variables. There are two ways of defining a constraints:
1. as an assignment statement: `c_1 = bexp`, so that the name of the constraint is named by that of the target in the assignment statement, in this case `c_1`,
2. as a function: 
	```python
	def c_2():
		bexp1
		bexp2
		...
	```
	The expressions inside the body of the function are of `and` relation, so that compared to the first way, defining constraints can be simplified by omitting the `and` operators if multiple constraints are of conjunction relation. All constraints inside the body together are named by the function name, in this case `c_2`.
- Theoretically, `bexp` can be any expression that returns boolean value. But currently only expressions of the following forms are allowed:
	1. Universal quantification: returns `True` if for all combinations of values of variables that satisfy all membership clauses `vi in sexpi`, the condition `bexp` evaluates to `True`. A membership clause `v in sexp` returns `True` if value `v` is a member of `sexp`, 
		- `each(v1 in sexp1, ..., vk in sexpk, has= bexp)`,
	2. Existential quantification: returns `True` if for some combinations of values of variables that satisfy all membership clauses `vi in sexpi`, the condition `bexp` evaluates to `True`,
		- `some(v1 in sexp1, ..., vk in sexpk, has= bexp)`,
	3. binary comparison expression with operator: `==`, `!=`, `<`, `<=`, `>`, `>=`, 
	4. global constraint `alldiff`. `alldiff` is a builtin constraint of one of the form:
		- `alldiff(sexp)`,
		- `alldiff(exp, v1 in sexp1, ..., vk in sexpk, bexp)`. 
		 
	   It returns `True` if 
		- all items in `sexp`, for the first case
		- all items in the set of values of `exp` for all combinations of values of variables that satisfy all membership clauses `vi in sexpi` and condition `bexp`, for the second case

	   take pairwisely different values, otherwise returns `False`.
	5. boolean operators (`and`, `or`, `not`) connected `bexp`'s
			
#### Return
The return value of a constraint problem is defined by a `return` statement of target function. As described above, the goal of CSPs and COPs are different so their target functions are in different forms:
1. CSP: `anyof(variables, c_1, ..., c_k)`
2. COP: `anyof(variables, c_1, ..., c_k, agg(opt))`
- The first argument of both target functions is the return value of the constraint problem. It can be a single decision variable or a tuple of decision variables.
- The last argument of COP target function is the calling of aggregation function `agg` on the objective `opt`. The aggregation function can be one of `to_max` or `to_min` performing maximization or minimization respectively.
- The other arguments are names of constraints that must be satisfied.

### Solving the problem
After specifying the problem, call the following function to solve the problem:
```python
query(constraint, **kwargs)
``` 
- `constraint` argument should be set to the name of a constraint problem
- `kwargs` are keyword arguments used to pass in the parameters of a constraint problem. The keys are names of parameters
- When passing in a keyword argument, if the variable to be passed is 
	- in the same scope as calling `query`, or 
	- an instance variable in a class, or
	- a global variable,

  and of the same name as the target parameter, the passing in of that argument can be omitted.
- The return value of `query` function is a dictionary, whose keys are names of decision variables appearing in the first argument of the target function. If the problem is COP, an additional `objective` item will also be returned if not already been specified in the first argument, which is the optimal value of the objective. Besides, the statistics of solving the problem are also returned under key `statistics`. The detailed explanation of all the items in statistics can be found [here](https://minizinc-python.readthedocs.io/en/latest/_modules/minizinc/result.html).

### Running the program
Usage: `python3 -m da --constraint <filename>`

save the example program to a file named `vertex_cover.da`, then running following command can get the output:

`>>> python3 -m da --constraint vertex_cover.da`
```python
[0, 1, 1, 0, 0, 0]
2
```
<!-- ### Running the Constaint Examples
1. USAGE: `python3 -m da --constraint <filename>`
2. some working examples are inside `examples/constraints` folder. -->
