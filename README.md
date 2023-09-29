# calib

calib is a simple 2D cellualar automata library that is designed to be easy to use and extend. It is written in pure python and has no dependencies.

It was designed as a base library for `link missing`

# Basic Usage

```python
from calib import *

cell_state_register("empty", color=(0, 0, 0))
cell_state_register("sand", color=(255, 255, 0))

# Add rule (for converting sand with empty below it to empty since sand falls)
pattern = cell_pattern_create(
    rule_parts={
        (0, 00): "sand",  # self (sand)
        (0, -1): "empty",  # bottom (empty)
    },
    neighborhood_type="moore"
)
cell_state_add_new_rule(pattern, "empty")

# Add rule (for converting empty with sand above it to sand since sand falls)
pattern = cell_pattern_create(
    rule_parts={
        (0, 0): "empty",  # self (empty)
        (0, 1): "sand",  # top (sand)
    },
    neighborhood_type="moore"
)
cell_state_add_new_rule(pattern, "sand")

# Create grid
example_grid = [
    ["empty", "empty", "empty", "empty"],
    ["empty", "sand", "empty", "empty"],
    ["empty", "empty", "empty", "empty"],
    ["empty", "empty", "empty", "empty"],
]
example_grid = grid_step(example_grid)

print(example_grid)
>> [
    ["empty", "empty", "empty", "empty"],
    ["empty", "empty", "empty", "empty"],
    ["empty", "sand", "empty", "empty"],
    ["empty", "empty", "empty", "empty"],
]
```

# API
API consists of 4 functoins

```python
cell_state_register(name, **kwargs)
```
This function registers a new cell state with the given name and keyword arguments. Keyword arguments are optional and spesific to the use case. They are essantialy constants shared between all cells with the same state. 
For example, you could use color as a keyword argument that is used to determine the color of the cell when it is rendered.

```python
cell_pattern_create(rule_parts, neighborhood_type)
```
This function is used to easily create patterns for rules. It takes a dictionary of rule parts and a neighborhood type. Tuples are used to determine the relative position of the cell to the current cell. Strings are used to determine the state of the cell at the given position. See basic usage for an example.

```python
cell_state_add_new_rule(pattern, new_state)
```
This function is used to add a new rule to a cell state. It takes a pattern and a new state. The pattern is used to determine when the rule should be applied. The new state is used to determine what the state of the cell should be after the rule is applied.

```python
grid_step(grid)
```
Evaluates new grid based on all registered rules and returns it. Takes a grid as an argument. The grid is a 2D array of cell states. See basic usage for an example.
