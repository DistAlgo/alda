# README

## Installation
1. Install XSB from http://xsb.sourceforge.net/.
2. Install MiniZinc from https://www.minizinc.org/software.html.
3. Add the path of container folder of minizinc binary/executable to your `PATH` environment variable.
4. Install MiniZinc Python interface with `pip install minizinc`.
5. Install DistAlgo: add path of `distalgo` folder to your `PATH` environment variable.

## Instruction

### How to write and solve a constraint solving problem
- A constriant solving problem can be written as easy as defining a function. 
```python
	def constraint(name='name_of_problem',parameters={set,of,parameters}):
		# Variables
		name_of_variable_1: domain_of_variable_1
		name_of_variable_2: domain_of_variable_2
		# Constraints
		c_1 = boolean_expr
		def c_2():
			boolean_expr_1
			boolean_expr_2
		# Target
		target: domain_of_target = usually_some_aggregation
		return anyof(some_decision_variable, c_1, c_2, to_max(target))

	result = query(constraint='name_of_problem',parameter_1=value_1,parameter_2=value_2,...)
```
- The function must be named by `constraint`, with two argument `name` and `parameters`. 
	- `name` is the unique identifier of the problem, 
	- `parameters` is a set containing the parameters whose values need to be passed in.
- Three components are required to define a constraint solving problem: variables, constraints and the target.
	1. Variables. There are two types of variables: parameters and decision variables.
		1. Parameters are variables that must be passed in when the problem is instantiated. Parameters must be explictly declared in the `parameters` argument of a constraint problem.
		2. Decision variables are computed during solving the problem. For some problems such as Sudoku, the partial filled playboard is passed in as a parameter, whose empty cells are indicated by `_` and will be computed as the solution of the problem. Parameters with empty cells are also treated as decision variables.

		Variables are defined in the form of type annotation, the value of which is optional:

		- `var_name: var_domain = value`

	 	The domain of a variable can be a type or other variables with the same domain. Applicable types are `int, ints, float, str, bool, dict, set`.
		- `ints(lb,ub)` presents a list of `int` with lowerbound `lb` and upperbound `ub`. The value of `ints(lb,ub)` is equivalent to `range(lb,ub+1)`.
		- Variables of `ints` type can be used inplace of `ints` in other variable definition.
		- The `dict(key=type, val=type)` type can be seen as an array, that `key` presents the dimensions. The domian of `key` must be of `ints` type or tuple of `ints` type. Currently the `value` of a `dict` can only be of `int` or `float` type.
		- The elements inside a `set` must of the same type. A `set` type variable can be defined more precicely by `set[type]`. Currently the elements of a `set` can only be of `int` or `float` type.
	2. Constraints. Constraints are the conditions must be satified when assigning values to decition variables. There are two ways of defining a constraints:
		1. as an assignment statement: `c_1 = boolean_expr`. 
		2. as a function: 
			```python
				def c_2(logic=and):
					boolean_expr_1
					boolean_expr_2
			```
			By defualt, the statements inside the block of a constraint definition are of `and` relation, so that compared to the first way, the definition of constraints can be simplified by omitting the `and` operator. By assigning the logic parameter to `or`, the logic relation between the statements are set to `or`.
		- Theoretically the `boolean_expr` can be any expression that returns boolean value. But currently only `some`, `each`, comparison, `alldiff` are supported. Boolean operators (`and`, `or`, `not`) can be used to connect the previous expressions.
		- Note: `alldiff` is a builtin function with one argument that takes a `dict` variable, or a generator, and returns `True` if each element in the sequence takes pairwisely different value, otherwise `False`.
	3. Target. Usually there are two types of constraint solving problems: constraint satisfaction problem (CSP) and constraint optimization problem (COP). The target of a CSP is to finding assignments to decision variables such that all the constraints are satified. For COPs, in addition to the constraints of CSP, there is also an optimization goal, usually is some expression of decision variables that needs to be minimized or maximized. The target is defined by a `return` statement of target function: 
		```python
			return anyof(some_decision_variable, c_1, c_2, to_max(target))
		```
		- There are two target functions: `anyof` and `setof`. `anyof` returns one of the assignments to decision variables and `setof` returns all the valid assignments. Currently only `anyof` is implemented.
		- The first argument of the target function indicates the decision variable or tuple of decision variables you want to get from solving the problem.
		- If the last argument of the function is a calling of `to_max` or `to_min`, it is the optimization target for a COP, solving maximize or minimize respectively. If the last argument is not a calling of `to_max` or `to_min`, then the problem is treated as a CSP.
		- The other arguments are name of constraints that you want to apply to the problem.
- Solving the problem. After defining the problem, call 
	```python
		query(constraint='name_of_problem',parameter_1=value_1,parameter_2=value_2,...)
	``` 
	to solve the problem.
	- parameters are passed in as keyword arguments.
	- Values or variables can be passed in as parameters. 
	- When passing in a variable, if a variable is in the same scope as calling `query` or is a global variable,  and of the same name as the target parameter in the defined problem, the passing in of that parameter can be omitted.
	- The return value of `query` function is a dictionary, whose keys are names of decision variables appearing in the first element of the target function of the problem. If the problem is COP, an additional `objective` item will also be returned. Besides, the statistics of solving the problem are also returned under key `statistics`. The detailed explaination of all the items in statistics can be found [here](https://minizinc-python.readthedocs.io/en/latest/_modules/minizinc/result.html).

### Running the Constaint Examsple
1. USAGE: `python3 -m da --constraint <filename>`
2. some working examples are inside `examples/constraints` folder.

### How to write with rules
1. TODO

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
