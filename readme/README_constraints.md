# README

## Installation

To use the extension with constraints,

1. install MiniZinc from <https://www.minizinc.org/software.html>,
2. add the path for MiniZinc to the `PATH` environment variable, and
3. install the MiniZinc Python interface by running `pip install minizinc`.

## Using the extension with constraints

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

Usage: `python -m da --constraints <filename>`

Save the example program to a file, say named `vertex_cover.da`, then running following command
`>>> python -m da --constraints vertex_cover.da`
produces the output:

```python
[0, 1, 1, 0, 0, 0]
2
```

Some examples are given in the `examples/constraints` directory.
