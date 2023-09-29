"""
Library for easily creating anisotropic cellular automata
"""

from dataclasses import dataclass
from typing import Literal

# ------------------ VARIABLES ------------------

__ALL__ = ["cell_state_register", "cell_state_add_new_rule", "cell_pattern_create", "grid_step"]

CELL_STATE_REGISTRY = {}

BORDER_VALUE = "border"
EMPTY_VALUE = "empty"
NEIGHBORHOODS = {}

# ------------------ DEFINITIONS ------------------

@dataclass
class Pattern:
    pattern: list
    neighborhood_type: str

@dataclass
class Cell:
    name: str
    rules: list
    data: dict

# ------------------ CELL STATE FUNCTIONS ------------------

def cell_state_register(name: str, **kwargs) -> None:
    CELL_STATE_REGISTRY[name] = Cell(name, [], kwargs)


def cell_state_add_new_rule(matching_pattern: Pattern, resulting_new_state: str) -> None:
    name = matching_pattern.pattern[0]
    CELL_STATE_REGISTRY[name].rules.append((matching_pattern, resulting_new_state))


def _cell_pattern_match(pattern: Pattern, neighborhood: list) -> bool:

    _pattern = pattern.pattern

    for i in range(len(_pattern)):

        pattern_i = _pattern[i]
        neighborhood_i = neighborhood[i]

        match(pattern_i):
            case "*":  # wildcard
                continue
            case _:
                if pattern_i != neighborhood_i:
                    return False

    return True

# ------------------ GRID FUNCTIONS ------------------

def grid_step(grid: list[list]) -> list[list]:

    NEIGHBORHOOD_TYPE_COUNT = len(NEIGHBORHOODS.keys())

    # Create new grid
    new_grid = [[EMPTY_VALUE for _ in range(len(grid[0]))] for _ in range(len(grid))]

    # Iterate over grid
    for y, row in enumerate(grid):
        for x, cell_state_name in enumerate(row):
            for pattern, cell_new_state_name in CELL_STATE_REGISTRY[cell_state_name].rules:

                neighborhood_type = pattern.neighborhood_type
                neighborhood = NEIGHBORHOODS[neighborhood_type](grid, x, y)
                # for cells with bunch of rules neighbor gets calculated multiple times
                # simple cache could be implemented to avoid this

                if _cell_pattern_match(pattern, neighborhood):
                    new_grid[y][x] = cell_new_state_name
                    break
            else:
                new_grid[y][x] = cell_state_name

    return new_grid

# ------------------ UTILS ------------------

def cell_pattern_create(rule_parts: dict, neighborhood_type: Literal["moore", "von_neumann"]) -> Pattern:

    empty_pattern = []
    positions = []

    if (0, 0) not in rule_parts.keys():
        raise ValueError("Rule must contain (0, 0) offset (self)")

    # Get position (list containting index information of offsets and length of pattern)
    match(neighborhood_type):
        case "moore":
            positions = [(0, 0), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        case "von_neumann":
            positions = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]
        case _:
            raise ValueError("Invalid neighborhood type")

    # Create new empty pattern
    new_pattern = ["*" for _ in positions]

    for offset, state_id in rule_parts.items():
        if offset in positions:
            index = positions.index(offset)
            new_pattern[index] = state_id

    return Pattern(new_pattern, neighborhood_type)


def print_grid(grid):
    for row in grid:
        print(row)

# ------------------ NEIGHBORHOOD FUNCTIONS ------------------

def _get_moore_neighborhood(arr, x, y):
    return (
        arr[y][x],
        arr[y - 1][x] if y > 0 else BORDER_VALUE,
        arr[y - 1][x + 1] if y > 0 and x < len(arr[y]) - 1 else BORDER_VALUE,
        arr[y][x + 1] if x < len(arr[y]) - 1 else BORDER_VALUE,
        arr[y + 1][x + 1] if y < len(arr) - 1 and x < len(arr[y]) - 1 else BORDER_VALUE,
        arr[y + 1][x] if y < len(arr) - 1 else BORDER_VALUE,
        arr[y + 1][x - 1] if y < len(arr) - 1 and x > 0 else BORDER_VALUE,
        arr[y][x - 1] if x > 0 else BORDER_VALUE,
        arr[y - 1][x - 1] if y > 0 and x > 0 else BORDER_VALUE
    )
NEIGHBORHOODS["moore"] = _get_moore_neighborhood

def _get_von_neuman_neighborhood(arr, x, y):
    return (
        arr[y][x],
        arr[y - 1][x] if y > 0 else BORDER_VALUE,
        arr[y][x + 1] if x < len(arr[y]) - 1 else BORDER_VALUE,
        arr[y + 1][x] if y < len(arr) - 1 else BORDER_VALUE,
        arr[y][x - 1] if x > 0 else BORDER_VALUE,
    )
NEIGHBORHOODS["von_neumann"] = _get_von_neuman_neighborhood

# ------------------ TESTS ------------------

def _test_neighborhood_functions():

    TEST_RESULT_MOORE = ("5", "2", "3", "6", "9", "8", "7", "4", "1")
    TEST_RESULT_VON_NEUMANN = ("5", "2", "6", "8", "4")

    # Sample grid
    grid = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"]
    ]

    # Test coordinates
    x, y = 1, 1

    print("Grid:")
    print_grid(grid)

    print("Coordinates:", x, y)

    res = []
    for _t, func in NEIGHBORHOODS.items():
        neighborhood = func(grid, x, y)
        print(f"{_t.capitalize()} Result:", neighborhood)
        res.append(neighborhood)

    assert res[0] == TEST_RESULT_MOORE, f"Moore neighborhood function failed with {res[0]}. Expected: {TEST_RESULT_MOORE}" # noqa
    assert res[1] == TEST_RESULT_VON_NEUMANN, f"Von Neumann neighborhood function failed with {res[1]}. Expected: {TEST_RESULT_VON_NEUMANN}" # noqa


def _test_cell_pattern_create():

    TEST_PATTERN = Pattern(["self", "1", "2", "3", "4", "5", "6", "7", "8"], "moore")

    # Sample rule
    rule = {
        (0, 0): "self",
        (0, 1): "1",
        (1, 1): "2",
        (1, 0): "3",
        (1, -1): "4",
        (0, -1): "5",
        (-1, -1): "6",
        (-1, 0): "7",
        (-1, 1): "8",
    }

    # Sample neighborhood type
    neighborhood_type = "moore"

    pattern = cell_pattern_create(rule, neighborhood_type)

    assert pattern == TEST_PATTERN, f"Pattern creation util failed with {pattern}. Expected: {TEST_PATTERN}"

    print("Pattern:", pattern)


def _test_cell_state_and_pattern_matching_functions():

    # Create cell states
    cell_state_register("empty", color=(0, 0, 0))
    cell_state_register("sand", color=(255, 255, 0))

    assert CELL_STATE_REGISTRY["sand"] == Cell("sand", [], {"color": (255, 255, 0)})

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

    print("Cell State Registry:", CELL_STATE_REGISTRY)

    example_grid = [
        ["empty", "empty", "empty", "empty"],
        ["empty", "sand", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
    ]

    print("Example Grid:")
    print_grid(example_grid)

    # Check if pattern matches at (1, 2)
    print("\nChecking if pattern matches at (1, 2)")
    neighborhood = NEIGHBORHOODS["moore"](example_grid, 1, 2)
    print("Neighborhood:", neighborhood)
    assert _cell_pattern_match(pattern, neighborhood), f"Pattern matching failed with {neighborhood}. Expected: {pattern}" # noqa
    print("Success!")

    # Check if pattern does not match at (0, 0)
    print("\nChecking if pattern does not match at (0, 0)")
    neighborhood = neighborhood = NEIGHBORHOODS["moore"](example_grid, 0, 0)
    print("Neighborhood:", neighborhood)
    assert not _cell_pattern_match(pattern, neighborhood), f"Pattern matching failed with {neighborhood}. Expected: {pattern}" # noqa
    print("Success!")

def _test_grid_step():
    example_grid = [
        ["empty", "empty", "empty", "empty"],
        ["empty", "sand", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
    ]

    TEST_STEP_1_GRID = [
        ["empty", "empty", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
        ["empty", "sand", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
    ]

    TEST_STEP_2_AND_3_GRID = [
        ["empty", "empty", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
        ["empty", "empty", "empty", "empty"],
        ["empty", "sand", "empty", "empty"],
    ]

    TEST_GRIDS = [TEST_STEP_1_GRID, TEST_STEP_2_AND_3_GRID, TEST_STEP_2_AND_3_GRID]

    print("Testing grid step watch if the sand falls")

    print("Example Grid:")
    print_grid(example_grid)

    for i in range(3):
        print(f"\nStep {i+1}:")
        example_grid = grid_step(example_grid)
        print_grid(example_grid)
        assert example_grid == TEST_GRIDS[i], f"Grid step failed with {example_grid}. Expected: {TEST_GRIDS[i]}" # noqa
        print("Success!")

# ------------------ DEBUG ------------------

def debug():
    # Call the test function
    print("-" * 20)
    _test_neighborhood_functions()
    print("-" * 20)
    _test_cell_pattern_create()
    print("-" * 20)
    _test_cell_state_and_pattern_matching_functions()
    print("-" * 20)
    _test_grid_step()
    print("-" * 20)
    print("\nAll tests passed successfully!")


if __name__ == "__main__":
    debug()
