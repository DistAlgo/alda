# README

Alda includes an extension of DistAlgo with rules.  This implementation supports Python 3.7 but can also run with Python 3.8 and 3.9.

## Installation

To use the extension with rules, install [XSB](http://xsb.sourceforge.net/):

1. download XSB from <https://sourceforge.net/projects/xsb> --- click "Download" for Windows, or download from "Source(GIT)" for Unix,
2. run the downloaded .exe file for Windows, or follow the instructions in Section 2.1 in the manual (just paragraph 1, items 1 and 4) for Unix, and
3. add the path for the XSB executable to the `PATH` environment variable.

## Using the extension with rules

### An example program that uses rules

Consider computing the [transitive closure](https://en.wikipedia.org/wiki/Transitive_closure) of edges in a graph. Given a graph with a set of edges, each from a vertex to another, the transitive closure is the set of all pairs of vertices such that there is a path from the first vertex to the second vertex following a sequence of edges.

The following Alda program computes the transitive closure of the set `e` of edges. Given predicate `edge` that asserts whether there is an edge from a first vertex to a second vertex, rule set `trans_rules` defines predicate `path` that asserts whether there is a path from a first vertex to a second vertex by following the given edges.

```python
def rules(name=trans_rules):
  path(x,y), if_(edge(x,y))
  path(x,y), if_(edge(x,z), path(z,y))

e = {(7,2), (7,3), (2,3), (2,4), (7,5), (3,6)}
print(infer(rules=trans_rules, bindings=[('edge',e)], queries=['path']))
```

The first rule says that there is a path from `x` to `y` if there is an edge from `x` to `y`. The second rule says that there is a path from `x` to `y` if there is an edge from `x` to `z` and there is a path from `z` to `y`.
Function `infer` uses rule set `trans_rules`, takes `edge` to be true for edges in `e`, and returns the set of pairs for which `path` is true.

### Specification of rules

A set of rules can be specified using a rule set of the following form:

```python
def rules(name=rsname):
  rule+
```

`rsname` is the name of the rule set and uses the same naming convention as Python identifiers; `name=` is optional. `rule+` is one or more rules.

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
- `arg_k` can be a variable name, a constant, or wildcard `_` indicating that its value does not mattter. A constant can be integers, `None`, `True`, `False`, or quoted strings. All variables in the conclusion must be in a condition.

In a rule set, predicates not in any conclusion are called *base predicates* of the rule set, and the other predicates are called *derived predicates* of the rule set.

### Inference using rules

One can do inference using rules by calling a built-in inference function `infer`, of the following form

```python
infer(rules=rsname, 
      bindings=[('pred_1',sexp_1),...,('pred_i',sexp_i)], 
      queries=['query_1',...,'query_j'])
```

- `rsname` is the name of a rule set.
- `bindings` is an optional keyword argument that specifies the assignment to each base predicate `pred_k` in the rule set with the value of a set-valued expression `sexp_k`. Each predicate name `pred_k` needs to be a quoted string. If `pred_k` is not local to rule set `rsname`, the assignment to `pred_k` can be omitted.
- `queries` is an optional keyword argument that specifies the queries to be made. Each `query_k` needs to be a quoted string of the form `pred(arg_1,...,arg_m)`, where `pred` is a predicate name in rule set `rsname` and `arg_k` is a constant or a wildcard `_`. Query `pred(_,...,_)` can be abbreviated as `pred`. When `queries` is omitted, `infer` treats all derived predicates as queries.
- Return value: For each value `k` from 1 to `j`, the result of `query_k` is returned as the `k`th component of the return value. The result of a query with `l` distinct variables that are not constants is a set of tuples of `l` components, one for each of the distinct variables in their order of first occurrence in the query. When `l` equals 1, the set of tuples is reduced to a set of elements in the tuples.

#### Automatic maintainence

When using rules with only non-local predicates, the derived predicates are automatically updated when any of the base predicate is updated, without explicit calls to `infer`.

### Running the program

Usage: `python -m da --rules <filename>`  
where `<filename>` is the name of a Alda program that uses rules.

Save the example program to a file, say named `trans.da`, then running the command
`>>> python -m da --rules trans.da`
produces the output

```python
{(7, 4), (2, 4), (7, 3), (2, 3), (7, 6), (2, 6), (7, 2), (3, 6), (7, 5)}
```
