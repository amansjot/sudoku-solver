from collections import deque
from flask import Flask, render_template_string, request
from sudoku_constraints4x4 import constraints4x4
from sudoku_constraints9x9 import constraints9x9
import json

app = Flask(__name__)

# PUZZLES

puzzle_1 = [
    [7, 0, 0, 4, 0, 0, 0, 8, 6],
    [0, 5, 1, 0, 8, 0, 4, 0, 0],
    [0, 4, 0, 3, 0, 7, 0, 9, 0],
    [3, 0, 9, 0, 0, 6, 1, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 0, 0],
    [0, 0, 4, 9, 0, 0, 7, 0, 8],
    [0, 8, 0, 1, 0, 2, 0, 6, 0],
    [0, 0, 6, 0, 5, 0, 9, 1, 0],
    [2, 1, 0, 0, 0, 3, 0, 0, 5],
]

puzzle_2 = [
    [1, 0, 0, 2, 0, 3, 8, 0, 0],
    [0, 8, 2, 0, 6, 0, 1, 0, 0],
    [7, 0, 0, 0, 0, 1, 6, 4, 0],
    [3, 0, 0, 0, 9, 5, 0, 2, 0],
    [0, 7, 0, 0, 0, 0, 0, 1, 0],
    [0, 9, 0, 3, 1, 0, 0, 0, 6],
    [0, 5, 3, 6, 0, 0, 0, 0, 1],
    [0, 0, 7, 0, 2, 0, 3, 9, 0],
    [0, 0, 4, 1, 0, 9, 0, 0, 5]
]

puzzle_3 = [
    [1, 0, 0, 8, 4, 0, 0, 5, 0],
    [5, 0, 0, 9, 0, 0, 8, 0, 3],
    [7, 0, 0, 0, 6, 0, 1, 0, 0],
    [0, 1, 0, 5, 0, 2, 0, 3, 0],
    [0, 7, 5, 0, 0, 0, 2, 6, 0],
    [0, 3, 0, 6, 0, 9, 0, 4, 0],
    [0, 0, 7, 0, 5, 0, 0, 0, 6],
    [4, 0, 1, 0, 0, 6, 0, 0, 7],
    [0, 6, 0, 0, 9, 4, 0, 0, 2]
]

puzzle_4 = [
    [0, 0, 0, 0, 9, 0, 0, 7, 5],
    [0, 0, 1, 2, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 0, 0, 1, 8, 0],
    [3, 0, 0, 6, 0, 0, 9, 0, 0],
    [1, 0, 0, 0, 5, 0, 0, 0, 4],
    [0, 0, 6, 0, 0, 2, 0, 0, 3],
    [0, 3, 2, 0, 0, 0, 0, 4, 0],
    [0, 0, 0, 0, 0, 6, 5, 0, 0],
    [7, 9, 0, 0, 1, 0, 0, 0, 0]
]

puzzle_5 = [
    [0, 0, 0, 0, 0, 6, 0, 8, 0],
    [3, 0, 0, 0, 0, 2, 7, 0, 0],
    [7, 0, 5, 1, 0, 0, 6, 0, 0],
    [0, 0, 9, 4, 0, 0, 0, 0, 0],
    [0, 8, 0, 0, 9, 0, 0, 2, 0],
    [0, 0, 0, 0, 0, 8, 3, 0, 0],
    [0, 0, 4, 0, 0, 7, 8, 0, 5],
    [0, 0, 2, 8, 0, 0, 0, 0, 6],
    [0, 5, 0, 9, 0, 0, 0, 0, 0]
]

puzzle_4x4 = [
    [1, 0, 0, 0],
    [0, 2, 0, 0],
    [0, 0, 3, 0],
    [0, 0, 0, 4]
]

# PART 2

def revise(csp, Xi, Xj):
    """ Removes values from Xi's domain that don't satisfy constraints with anything in Xj's domain. """
    variables, constraints = csp

    # If revise cannot be done, return False
    if not variables.get(Xi) or not variables.get(Xj):
        return False

    # Get the variable domains
    Di, Dj = variables[Xi], variables[Xj]
    revised = False
    
    # Check each value in Xi's domain
    for x in Di[:]:
        satisfies_constraint = False
        
        # Check if there's any satisfiable constraint for every value in Xj's domain 
        for y in Dj:
            if [x, y] in constraints.get((Xi, Xj), []) or [x, y] in constraints.get((Xj, Xi), []):
                satisfies_constraint = True
                break
                
        # If no Dj value satisfies the constraint, remove the Di value
        if not satisfies_constraint:
            Di.remove(x)
            revised = True

    return revised

# PART 3

def get_neighbors(csp, X):
    """ Helper function to get the cells with which cell X has a constraint. """
    constraints = csp[1]

    # Initialize neighbors as a set to ensure no duplicates and easily remove Xj in AC3
    neighbors = set()

    # If any constraint has cell X in it, add it to the set
    for constraint in constraints.keys():
        if constraint[0] == X:
            neighbors.add(constraint[1])
        elif constraint[1] == X:
            neighbors.add(constraint[0])

    return neighbors

def AC3(csp):
    """ Removes any inconsistencies across all domains in the given CSP. """
    variables, constraints = csp

    # Initialize a deque of the constraint pairs for O(1) pop and push
    queue = deque(constraints.keys())

    while queue:
        # Pop the leftmost value and revise it
        Xi, Xj = queue.popleft()

        if revise(csp, Xi, Xj):
            # False if there are no domains
            if not variables[Xi]:
                return False
            
            # Append each of Xi's neighbors besides Xj
            for Xk in sorted(get_neighbors(csp, Xi) - {Xj}):
                queue.append((Xk, Xi))

    return True

# PART 4

def minimum_remaining_values(csp, assignments):
    """ Among the unassigned variables, finds the one with the fewest domain values. """
    variables = csp[0]
    unassigned_vars = {}

    # Check each variable's domains and record their lengths
    for variable, domain in variables.items():
        if variable not in assignments:
            unassigned_vars[variable] = len(domain)
    
    # Get the variable with the minimum domain length 
    minimum_variable = min(unassigned_vars, key = unassigned_vars.get, default = None)
    return minimum_variable

# PART 5

def backtrack(assignment, csp, progress, assignments, domains, failed_values, backtracks, color_num=0):
    """ Backtracking search to recursively find assignments for all variables in the CSP. """
    variables, constraints = csp

    # Check if the assignment is finished
    if len(assignment) == len(variables):
        return assignment, progress, assignments, domains, failed_values, backtracks

    # Use the minimum remaining values heuristic to choose the unassigned variable
    var = minimum_remaining_values(csp, set(assignment.keys()))
    
    for value in variables[var]:
        # Create a new assignment that doesn't affect the current state
        new_assignment = assignment.copy()
        new_assignment[var] = value
        
        # Apply the assignment to the domain after deep copying
        new_domains = {v: list(d) for v, d in variables.items()}
        new_domains[var] = [value]
        
        # Create a new CSP for the new assignment
        new_csp = (new_domains, constraints)

        # Use AC-3 to keep arc consistency with the new assignment
        if AC3(new_csp):
            # Add the checked variable-value pair to the assignments
            new_assignments = assignments + [var]

            # If the cell hasn't been assigned, add it to the progress with the incremented color number
            if len(variables[var]) > 1:
                color_num += 1
                progress.append((var, value, color_num))

            result, progress, order, domains, failed, counts = backtrack(new_assignment, new_csp, progress, new_assignments, domains, failed_values, backtracks, color_num)
            
            # If a result is found, return it
            if result:
                return result, progress, order, domains, failed, counts
        else:
            # If this value led to failure, record it
            failed_values[var].append(value)
            backtracks[var] += 1
        
            # Store the domains for unassigned variables before backtracking
            unassigned_domains = {v: d for v, d in new_domains.items() if v not in new_assignment}
            domains.append(unassigned_domains)

    # If no valid assignment was found for the variable, return None
    return None, progress, assignments, domains, failed_values, backtracks

def backtracking_search(csp):
    """ Initialize places to record the data and call backtrack. """
    # Store the counts and assignments
    variables = csp[0]
    failed_values = {var: [] for var in variables}
    backtracks = {var: 0 for var in variables}

    # Start backtracking with empty lists, dicts, and numbers set to 0
    return backtrack({}, csp, [], [], [], failed_values, backtracks, 0)

# PART 6

def variables_from_puzzle(puzzle):
    """ Get the variables for each cell based on the puzzle as a 2D array. """
    variables = {}

    # A range from 1 through the puzzle length
    puzzle_range = range(1, len(puzzle) + 1)
    for i in puzzle_range:
        for j in puzzle_range:
            # Each variable's domain is the given value, otherwise a list of all possible values 
            cell = puzzle[i - 1][j - 1]
            variables[f'C{i}{j}'] = [cell] if cell else list(puzzle_range)

    return variables

@app.route("/")
def show_webpage():
    """ Flask function to show the solution as a webpage. """
    # Get the puzzle from the URL or default to puzzle_1 (check setup.txt for specifics)
    query = request.args.get('board', '')
    if query.startswith("puzzle_"):
        puzzle = globals().get(query) or puzzle_1
        print(f"Showing solution for {query if globals().get(query) else 'puzzle_1'}.")
    else:
        try:
            puzzle = json.loads(query)
            print(f"Showing solution for: {puzzle}.")
        except:
            puzzle = puzzle_1
            print(f"Invalid JSON. Showing solution for puzzle_1.")
        
    # Transform the puzzle into a valid CSP, then run backtracking search
    size = len(puzzle)
    box_size = int(size ** 0.5)
    variables = variables_from_puzzle(puzzle)
    constraints = constraints9x9 if size == 9 else constraints4x4
    csp = (variables, constraints)

    solution, progress, assignments, domains, failed_values, backtracks = backtracking_search(csp)
    
    # Log the solution and all other recorded data
    print("Solution:", solution)
    print("Progress:", progress)
    print("Order of assignment:", assignments)
    print("Domains after each assignment:", domains)
    print("Failed values for each variable:", failed_values)
    print("Number of backtracks for each variable:", backtracks)

    # Set the color of the given values to black
    cell_colors = [[(0, 0, 0) if cell else (100, 100, 100) for cell in row] for row in puzzle]

    # Add the color data to each cell in the puzzle
    puzzle_data = [[[puzzle[i][j], cell_colors[i][j]] for j in range(size)] for i in range(size)]

    # Sort the solution values into a 1D list
    solution_vals = list(dict(sorted(solution.items())).values())

    # Convert it into a 2D list, then add the color data to each cell
    solution_data = [solution_vals[i * size:(i + 1) * size] for i in range(size)]
    colored_solution_data = [[[solution_data[i][j], cell_colors[i][j]] for j in range(size)] for i in range(size)]

    # HTML code for the webpage structure and styling
    webpage_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sudoku Grid</title>
    <style>
        * {
            font-family: Arial, sans-serif;
        }
        .sudoku-grid {
            border-collapse: collapse;
            border: 3px solid #000;
        }
        .sudoku-grid td {
            width: 3em;
            height: 3em;
            border: 1px solid #888;
            text-align: center;
            vertical-align: middle;
            font-size: large;
        }
        .sudoku-grid tr:nth-child({{box_size}}n) td {
            border-bottom: 3px solid #000;
        }
        .sudoku-grid td:nth-child({{box_size}}n) {
            border-right: 3px solid #000;
        }
    </style>
    </head>
    <body>
    <h1>Sudoku Solver</h1>
    <a href="#solution">Go to Solution</a>''' + show_steps(puzzle_data, progress, colored_solution_data) + '''
    </body>
    </html>
    '''
    return render_template_string(webpage_html, box_size=box_size)

def show_steps(puzzle_data, progress, solution):
    """ Return the HTML for each progression in the solution steps. """
    # Show the initial board state
    solution_html = f'''
        <h3>State 0\n</h3>
        {sudoku_board(puzzle_data)}
        '''
    
    # Color each number based on the solution progression
    def get_color(number, max_num = progress[-1][2]):
        """ Adjust the color from blue towards red based on the progress number. """
        step = 255 // max_num
        red, _, blue = (0, 0, 255)
        red = min(255, red + step * number)
        blue = max(0, blue - step * number)
        return (red, 0, blue)

    # Loop through all states, each one determining the correct value of one cell 
    state = 1
    for change in progress:
        cell, value, color_num = change
        row, col = int(cell[1]) - 1, int(cell[2]) - 1

        # Calculate the rgb value and set it for the cell in the 2D list
        puzzle_data[row][col][1] = get_color(color_num)

        # Show the state only if the cell variable has not been assigned yet 
        if not puzzle_data[row][col][0]:
            puzzle_data[row][col][0] = value
            solution_html += f'''
            <h3>State {state}\n</h3>
            {sudoku_board(puzzle_data)}
            '''
            state += 1
        else:
            # If there's already a value there, prepend it to the strikethrough values
            puzzle_data[row][col][0] = str(value) + str(puzzle_data[row][col][0])

    # Show the solution state
    solution_html += f'''
        <h3 id="solution">Solution\n</h3>
        {sudoku_board(solution)}
        '''
    
    return solution_html

def sudoku_board(puzzle_data):
    """ Create the sudoku board in HTML based on the puzzle data. """
    # Determine the size of a box
    box_size = int(len(puzzle_data) ** 0.5)

    # Determine which numbers get strikethroughs
    def unique_guesses(guesses):
        """ Helper function to show the strikethroughs to the right of the correct guess. """
        seen = set(guesses[0])
        return guesses[0] + ''.join(s for s in guesses[1:] if s not in seen and not seen.add(s))

    # HTML to create the sudoku board grid
    grid_html = '''
    <table class="sudoku-grid">
        <tbody>
        {% for row in puzzle_data %}
            <tr>
            {% for value, color in row %}
                {% set rgb_color = 'rgb(%s, %s, %s)'|format(color[0], color[1], color[2]) %}
                <td style="color: {{ rgb_color }}; font-weight: {% if rgb_color == 'rgb(0, 0, 0)' %}bold{% else %}normal{% endif %};">
                    {% if value is string %}
                        {% set unique_guess_str = unique_guesses(value) %}
                        {{ unique_guess_str[0] }}{% for digit in unique_guess_str[1:] %}, <s>{{ digit }}</s>{% endfor %}
                    {% elif value %}
                        {{ value }}
                    {% endif %}
                </td>
            {% endfor %}
            </tr>
        {% endfor %}
        </tbody>
    </table>
    '''
    return render_template_string(grid_html, puzzle_data=puzzle_data, box_size=box_size, unique_guesses=unique_guesses)

# Run app on http://localhost:8080
if __name__ == "__main__":
    app.run(debug=True, port=8080)