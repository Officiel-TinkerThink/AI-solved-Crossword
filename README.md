# AI-solved-Crossword
Given The Crossword and The bag-of-words. AI will solve it

## Objective

Develop an AI to generate crossword puzzles by utilizing a constraint satisfaction problem (CSP) model, which incorporates node consistency, arc consistency, and backtracking search.

## Background

The structure of a crossword puzzle consists of:

- The specific squares of the grid designated for filling with letters.
- The sequences of squares corresponding to the words to be filled in.
- The direction of each word—either across or down.

The challenge in generating a crossword puzzle involves selecting appropriate words for each sequence of squares.

Each sequence of squares represents a variable, and the corresponding value needs to be chosen from a domain of possible words that can fill the sequence. These variables are governed by both unary and binary constraints:

- **Unary Constraints**: A variable's unary constraint is determined by its length. For instance, a variable with four squares can only accept four-letter words. Values that do not meet this constraint can be immediately excluded from the variable's domain, thus enforcing node consistency.
  
- **Binary Constraints**: Binary constraints arise when squares from one variable overlap with those of another variable. For example, if Variable 1 and Variable 2 both consist of four squares and overlap such that Variable 1's second square corresponds to Variable 2's first square, the second character of Variable 1 must match the first character of Variable 2. Enforcing arc consistency ensures that any option removed from one variable has a corresponding valid option in the constrained variable. 

- **Distinctness Constraint**: Additionally, all words in the puzzle must be unique. This can be formalized as binary constraints between every pair of variables, ensuring no two variables can take on the same value.

### Node Consistency

- **Node Consistency**: A variable is considered node consistent when all values in its domain satisfy the variable's unary constraints.

### Arc Consistency

- **Arc Consistency**: A variable is arc consistent with another when all values in its domain satisfy that variable's binary constraints. To make variable X arc consistent with respect to variable Y, values from X's domain are removed until every choice for X has a corresponding valid choice in Y.


### Backtracking Search

- **Backtracking Search**: This recursive algorithm is commonly used to solve constraint satisfaction problems by assigning values to each variable from its domain, one at a time.
  - If the assignment adheres to the problem's constraints, the backtracking search is recursively invoked on the CSP until all variables are assigned. Upon successfully assigning all variables, the solution is returned.
  - If a variable cannot be assigned consistently, the algorithm backtracks to the previous variable to attempt a different assignment until all possibilities are exhausted. If all options for all variables are exhausted without finding a solution, it indicates that no solution exists.

### Improvements to Backtracking

Several enhancements can improve the efficiency of the backtracking search algorithm:

- **Maintaining Arc Consistency**: Whenever a new assignment is made to variable X, invoke the AC-3 algorithm for all arcs (Y, X) where Y is a neighbor of X. This action quickly reduces the state space for finding a solution by eliminating inconsistent values from neighboring variables.

- **Heuristics for SELECT-UNASSIGNED-VAR**:
  - **Minimum Remaining Values (MRV)**: Choose the variable with the fewest remaining values in its domain.
  - **Degree Heuristic**: Choose the variable with the highest number of binary constraints (neighbors).
  
- **Heuristics for DOMAIN-VALUES**:
  - **Least-Constraining Values Heuristic**: Order domain values by the number of choices eliminated for neighboring variables, prioritizing the least constraining values first.

## Usage:

Requires Python(3) to run, and installation of Pillow if output images are desired, which can be done via `pip install pillow`.

To run backtracking search with interleaved arc consistency:
$python(3) generate.py data/structureX.txt data/wordsX.txt [output_image_filename.png]


## Demo Video:
Check out a [demo video](https://drive.google.com/file/d/14lhgdW1Nfqcc3N3MKdeFUBcXElHv09i9/view?usp=sharing) to see the Crossword AI in action!
