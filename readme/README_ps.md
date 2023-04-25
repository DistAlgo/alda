# Program Storage

A persistent program database for a Python program file, directory of files, or abstract syntax tree (AST), with creation and lookup functions.

## Example

```python
from ps import ps, CODE

filename = 'FILE_OR_DIRECTORY_TO_BE_ANALYZED'
db = dict()         # variable db will hold generated program facts
ps.read(source=filename, target=db, encode=True)  # read the file and encode the generated facts
print(db.keys())    # print all AST node types
print(ps.decode(180, format=CODE, target=db))     # print the code corresponding to AST node 180
```

## Specification

The `ps` module has the following functions:

- `read`: read a program and create a database for the abstract syntax structure of the program.
- `config`: configure the parameters, also called options, of a program database
- `encode`: return the internal representation of an abstract syntax node.
- `decode`: return the text or abstract syntax node of an internal representation.

### read

Read a Python source program and create a persistent program database. The source program can be either a file or directory, or an abstract syntax tree (AST). The database consists of sets of tuples representing the ASTs of the source files and the directory structure---one set of each AST node type, and one set for the directory nesting structure.

```python
def read(self, *, source, target, db_path, db_name, db_update, omit, encode)
```

Keyword-only arguments:

- `source`: source program to be read. This can be one of two types of values:
    - string for path of a file or directory, where all `.py` files will be parsed using Python's `ast.parse` and the directory structure will be captured
    - AST object returned by `ast.parse`, or generally any tree object of arbitrarily nested objects and lists
- `target`: target object or dictionary to hold generated sets of tuples. This can be one of two types of values:
    - object for which an attribute for each generated set will be created. A common use case is
        - `self`: each generated set will be a field of `self`, when used in a method with argument `self`
    - dictionary for which a key for each generated set will be created. Two common use cases are
        - `globals()`: each generated set will be a global variable
        - `locals()`: each generated set will be a local variable

- `db_path`: string for path of persistent database to store generated sets to disk, or `None` for not storing the generated sets. The default is a directory named `ps_db` in the home directory.
- `db_name`: string for name of the database, as a subdirectory of `db_path`. If `source` is a path, the default is the name of the file (without extension) or directory.
- `db_update`: whether to re-generate the database (or otherwise load the last generated sets from database) when the database was already generated. The default is `False`.
- `omit`: AST object fields and attributes to be omitted in generated database. This should be a dictionary with keys `fields` and `attributes`, each with a set of names to omit. The default is

    ```python
    dict(fields={'type_comment'}, attributes={'lineno','col_offset','end_lineno','end_col_offset'})
    ```

- `encode`: whether to encode objects in generated sets using internal representation (or otherwise leave as objects). The default is `True`. Encoding allows significantly improved performance of queries using generated sets. Not encoding allows direct queries using generated sets without encoding and decoding.

### config

Set the parameter values of a program database. It can be called with any subset of
the parameters.

```python
def config(source, target, db_path, db_name, db_update, omit, encode, file)
```

Share the same parameters as `read` except for `file`.

- `file`: path for a JSON file specifying the parameter values. If `file` and any other parameters are set,
those set in the parameters will override those in the file.

Parameter values set with `config` are used by `read` unless overridden by parameter values at a call to `read`.

### encode

```python
def encode(object, target)
```

Return the internal representation of a literal or AST source node object in `target`. The value must be presented in the corresponding source program of `target`.

### decode

```python
def decode(ir, target, format=CODE)
```

Return the corresponding code or AST node object of an internal representation `ir` in `target` when `format` is `CODE` or `AST`, respectively. The default for `format` is `CODE`.
    
