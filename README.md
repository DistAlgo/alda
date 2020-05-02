# README

DA-rules is an extension of DistAlgo with rules and constraints.  This implementation requires Python 3.7.

## Installation
1. Install DA-rules by (1) copying or extracting the DA-rules files to a path, designated as `<DArulesROOT>`, in the local file system, and (2) adding `<DArulesROOT>/distalgo` to the front of the `PYTHONPATH` environment variable so that Python can load the `da` module.
2. To use the extension with rules, install XSB from http://xsb.sourceforge.net/.
3. To use the extension with constraints, (1) install MiniZinc from https://www.minizinc.org/software.html, (2) add the path for MiniZinc to the `PATH` environment variable, and (3) install the MiniZinc Python interface by running `pip install minizinc`.

## Instruction

### An example program that uses constraints
<table style="width:100%">
  <tr>
	<td><img src="https://user-images.githubusercontent.com/2973457/80774269-82595000-8b2a-11ea-84de-99c5ac8b963c.png" width="750px"/></td>
	<td>Consider the graph shown on the left. The red vertices form a minimum <a href="https://en.wikipedia.org/wiki/Vertex_cover">vertex cover</a> of the graph. A vertex cover of a graph is a set of vertices in the graph such that each edge of the graph is attached to at least one vertex in the set. The minimum vertex cover problem is to find a vertex cover with the minimum number of vertices. The problem can be specified as a constraint solving problem in DA-rules as shown below.</td>
  </tr>
</table>

```python
def constraint(name= 'vertex_cover', pars={vertex, edge}):

 	# Parameters: vertices as a set of integers; edges as an adjacency matrix
	vertex: set[int]
	edge: dict(key= (vertex, vertex), val= ints(0,1))
	
	# Decision variables: a vertex cover as a dictionary too; number of vertices
	vc: dict(key= vertex, val= ints(0,1))
	num_vertex: int = sum(vs)

	# Constraints: each edge has at least one of its ends in the vertex cover
	cover = each(i in vertex, j in vertex, has=
	             edge[i,j] == 0 or vc[i] == 1 or vc[j] == 1)
	
	# Return: any vertex cover with the minimum number of vertices
	return anyof((vc, num_vertex), cover, to_min(num_vertex))
	
v = set(ints(1,6))
e = [[0,1,1,0,0,0],
     [1,0,1,1,1,1],
     [1,1,0,0,0,0],
     [0,1,0,0,0,0],
     [0,1,0,0,0,0],
     [0,1,0,0,0,0]]
result = query(constraint='vertex_cover', vertex=v, edge=e)
print(result['vc'])
print(result['num_vertex'])
```

- A constraint solving problem is the problem of finding assignments to decision variables while several constraints must be satisfied. In the vertex cover example, 
	- the decision variable is `mvc` which is a map from `vertex` to `0` or `1`. 
	  For vertex `v`, `mvc[v] == 1` means that `v` is inside the vertex cover, and `mvc[v] == 0` means `v` not inside.
	- the constraint `cover` defines the vertex cover condition.
	
	Depending on the target of a problem, there are two kinds of constraint solving problems: Constraint Satisfaction Problem (CSP) and Constraint Optimization Problem (COP). 
	1. The target of a CSP is to find an assignment of all decision variables while satisfying all the constraints,
	2. The target of a COP is that of a CSP with an additional optimization goal to be maximized or minimized.
		- The vertex cover example is a COP whose optimization goal is to minimize the size of vertex cover
- A constriant solving problem can be defined as easy as defining a function. 
  The function must be named `constraint`, with two argument `name` and `parameter`. 
	- `name` is the name of the problem, which is `'vertex_cover'` in the example.
	  The name is served as the unique identifier of a model and its naming convention is the same as python identifiers.
	- `parameter` is a set containing the parameters whose values need to be passed in. In the problem `vertex` and `edge` are the parameters.
- Inside the body of the constraint function, 3 kinds of information need to be defined: variables, constraints and the target.
	1. Variables. There are two types of variables: parameters and decision variables.
		1. Parameters are variables that must be passed in when the problem is instantiated. Parameters must be explictly specified in the `parameter` argument of the constraint function.
		2. Decision variables are variables whose values are to be decided during solving the problem. 
		   For some problems such as Sudoku, a partial filled playboard is passed in as parameter. The empty cells are indicated by `_` and will be computed when solving the problem. Parameters with empty cells are also treated as decision variables.
		- Variables needs to be explictly declared with domain informations. The syntax of variable definition is in the form of type annotation, the value of which is optional:
			- `variable_name: variable_domain = optional_value`
	 	- The domain of a variable can be
	 	 	1. basic domains: `int, float, str, bool`,
	 	 	2. `ints(lb,ub)`: preciser `int` domain
				- `ints(lb,ub)` presents the `int` domain taking value from lowerbound `lb` to upperbound `ub` (included),
				- `lb` and `ub` are of `int/ints` domain,
			3. map domain: `dict(key=domain, val=domain)`. The map domain can be viewed as array. `key` defines domain of the dimension and must be of `int/ints` domain or tuple of `int/ints` for multidimentional array. `value` must be of `int/ints` or `float` domain,
			4. `set`: A `set` can be defined precicely by `set[domain]` where `domain` can be of `int/ints` or `float` domain,
			5. variables can be used as domains presenting the domains of themselves.
	2. Constraints. Constraints are the conditions must be satified when assigning values to decition variables. There are two ways of defining a constraints:
		1. as an assignment statement: `c_1 = bexp`, so that the name of the constraint is named by the target name of assignment
		2. as a function: 
			```python
				def c_2():
					bexp1
					bexp2
					...
			```
			The expressions inside the body of function are of `and` relation, so that compared to the first way, defining of constraints can be simplified by omitting the `and` operator if mutiple constraints are of conjunction relation. All constraints inside the body together are named as the function name.
		- Theoretically, `bexp` can be any expression that returns boolean value. But currently only 
			1. Universal quantification: returns `True` if all of the memebership clauses `vk in sexpk` and condition `bexp` are `True`
				- `each(v1 in sexp1, ..., vk in sexpk, has= bexp)`,
			2. Existential quantification: returns `True` if some of the memebership clauses `vk in sexpk` and condition `bexp` are `True`
				- `some(v1 in sexp1, ..., vk in sexpk, has= bexp)`,
			3. comparison expression with operator: `==`, `!=`, `<`, `<=`, `>`, `>=`, 
			4. global constraint function call `alldiff`. `alldiff` is a builtin constraint function of the form
				- `alldiff(sexp)`,
				- `alldiff(exp, v1 in sexp1, ... vk in sexpk, bexp)`, 
				 
			   that returns `True` if 
			   - all items in `sexp` for the first case
			   - all `exp` that satisfies all membership clause `vk in sexpk` and condition `bexp` for the second case

			   take pairwisely different values, otherwise returns `False`.
			5. boolean operators (`and`, `or`, `not`) connected `bexp`'s

		  are allowed.
			
	3. Target. The target is defined by a `return` statement of target function. As described above, there are CSPs and COPs with different target functions:
		1. CSP target function: `anyof(variables, c_1, ..., c_k)`
		2. COP target function: `anyof(variables, c_1, ..., c_k, agg(opt_goal))`
		- The first argument of both target functions is the return value of the constraint problem. It can be a single decision variable or tuple of decision variables.
		- The last argument of COP target function is the calling of aggregation function `agg` on the optimization goal `opt_goal`. The aggregation function can be one of `to_max` or `to_min` doing maximize or minimize respectively. The `opt_goal` is usually some expression of decision variables.
		- The other arguments are names of constraints that must be satisfied.
- Solving the problem. After defining the problem, call 
	```python
	query(constraint, **kwargs)
	``` 
	to solve the problem.
	- `constraint` parameter should be set to the name of a constraint solving problem
	- `kwargs` are keyword arguments used to pass in the parameters of a constraint solving problem. The keys are name of parameters
	- When passing in a keyword arguments, if the passing variable is 
		- in the same scope as calling `query`, or 
		- is an instance variable in a class, or
		- is a global variable,

	  and of the same name as the target parameter, the passing in of that parameter can be omitted. In the vertex cover example, the pass in of parameter `edge` is omitted.
	- The return value of `query` function is a dictionary, whose keys are names of decision variables appearing in the first argument of the target function. If the problem is COP, an additional `objective` item will also be returned, which is the optimal value of the optimization goal. Besides, the statistics of solving the problem are also returned under key `statistics`. The detailed explaination of all the items in statistics can be found [here](https://minizinc-python.readthedocs.io/en/latest/_modules/minizinc/result.html).

- Running the program: `python3 -m da --constraint <filename>`

	save the example program to a file named `vertex_cover.da`, then running following command can get the output:

	`>>> python3 -m da --constraint vertex_cover.da`
  ```python
	{'mvc': [0, 1, 1, 0, 0, 0],
	 'objective': 2,
	 'statistics': {'evaluatedHalfReifiedConstraints': 6,
	                'flatIntConstraints': 13,
	                'flatIntVars': 13,
	                'flatTime': datetime.timedelta(microseconds=74739),
	                'method': 'minimize',
	                'nodes': 0,
	                'objective': 2,
	                'objectiveBound': 2,
	                'openNodes': -1,
	                'paths': 0,
	                'solveTime': datetime.timedelta(microseconds=29700),
	                'time': datetime.timedelta(microseconds=120000)}}
  ```
<!-- ### Running the Constaint Examples
1. USAGE: `python3 -m da --constraint <filename>`
2. some working examples are inside `examples/constraints` folder. -->

### Using the extension with rules
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

### Running the Rule Examples
#### Trans
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
