# Fact generator for preparing for python analysis

Parse file, directory of files or AST tree and generate facts.

## Example

```python
from pa import pa, CODE

if __name__ == '__main__':
    filename = 'FILE_OR_DIRECTORY_TO_BE_ANALYZED'
    output = dict()         # the encoded facts will be saved to this variable
    pa.read(source=filename, target=output, encode=True) # read in the file and encode the facts
    print(output.keys())             # prints all the names of AST nodes
    print(pa.decode(180, format=CODE, target=output)) # print the code snippet corresponding to the AST node with id 180
```

## Specification

The `pa` module has the following functions:

- `read`: read a program and create a database for the abstract syntax structure of the program.
- `config`: configure the parameters, also called options, of a program database
- `encode`: return the internal representation of an abstract syntax node.
- `decode`: return the text or abstract syntax node of an internal representation.

### read

Takes a source program and generates a persistent program database. The source program
can be either a file or directory, or an AST. The database consists of sets of tuples representing the ASTs of
the input program and the directory structure—one set of each AST node type, and one set for the directory
nesting structure.

```python
def read(self, *, source, target, db path, db name, db update, omit, encode)
```

Keyword-only arguments:

- `source`: source program to be read. This can be one of two types of values:
    - string for path of a file or directory, where all `.py` files will be parsed using Python’s `ast.parse` and the directory structure will be captured
    - AST object returned by `ast.parse`, or generally any tree object of arbitrarily nested objects and lists
- `target`: target object or dictionary to hold generated sets of tuples. This can be one of two types of values:
    - object for which an attribute for each generated set will be created. A common use case is
        - `self`: each generated set will be a field of self, when used in a method with argument `self`
    - dictionary for which a key for each generated set will be created. Two common use cases are
        - `globals()`: each generated set will be a global variable
        - `locals()`: each generated set will be a local variable

- `db_path`: string for path of persistent database to store generated sets to disk, or None for not storing the generated sets. The default is path of parent directory of `source`.
- `db_name`: string for name of database, as a subdirectory of db path. If source is a path, the default is the name of the file (without extension) or directory.
- `db_update`: whether to re-generate the database (or otherwise load the last generated sets from database) when the database was already generated, default to `False`.
- `omit`: AST object fields and attributes to be omitted in generated database. This should be a dictionary with keys fields and attributes, each with a set of names to omit. The default is

    ```python
    dict(fields=’type_comment’, attributes=’lineno’,’col_offset’,’end_lineno’,’end_col_offset’)
    ```

- `encode`: whether to encode objects in generated sets using internal representation (or otherwise leave as objects), default to `True`. Encoding allows significantly improved performance of queries using generated sets. Not encoding allows direct queries using generated sets without encoding and decoding.

### config

Sets the parameter values of a program database. It can be called with any subset of
the parameters.

```python
def config(self, *, source, target, db path, db name, db update, omit, encode, file)
```

Share the same parameters as `read` except for `file`.

- `file`: path for a JSON file specifying the parameter values. If `file` and any other parameters are set,
those set in parameters will override those in files.

Parameter values set with config are used by read unless overridden by parameter values at a call to read.

### encode

Return the internal representation of a literal value. The value must be presented in the source program.

```python
def encode(self, value, *, target)
```

Return the internal representation of a literal value. The value must be presented in the source program. By default, it will look up values in the last used target. But you can pass another target by argument `target`

### decode

Return the text or the AST node of the fact with internal representation.

```python
def decode(self, ir, *, format=CODE, target=None)
```

- `ir`: internal representation of AST fact

Keyword-only arguments:

- `format`: output target, takes the following values:
    - `CODE`: default, return the code snippet corresponding to the AST fact in string
    - `AST`: return the AST node object itself
- `target`: the target to find the node.

    By default, target refers to the last used target.
