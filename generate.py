import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for item in self.domains[var].copy():
                if len(item) != var.length:
                    self.domains[var].remove(item)

    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # encsure that all values is distinct
        values = assignment.values()
        if len(values) != len(set(values)):
            return False
        
        for var in assignment:
            # check if values are consistent with key
            if var.length != len(assignment[var]):
                return False
            
            # check if no conflict with neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    x_index, y_index = self.crossword.overlaps[var, neighbor]
                    if assignment[var][x_index] != assignment[neighbor][y_index]:
                        return False 
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        x_domain = self.domains[var]
        neighbors = self.crossword.neighbors(var)
        
        domain_rank = {}
        for x_value in x_domain:
            elimination_count = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                x_index, y_index = self.crossword.overlaps[var, neighbor]
                for y_value in self.domains[neighbor]:
                    if x_value[x_index] != y_value[y_index] or x_value == y_value:
                        elimination_count += 1
            domain_rank[x_value] = elimination_count
        
        sorted_domain = sorted(domain_rank, key= lambda keys: domain_rank[keys]) 
        return sorted_domain
          

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variable = [var for var in self.crossword.variables if var not in assignment]
        best_var = (None, float("inf"), float("-inf"))

        for var in unassigned_variable:
            num_domain = len(self.domains[var])
            degree = len(self.crossword.neighbors(var))
            if best_var[1] > num_domain:
                best_var = (var, num_domain, degree)
            elif best_var[1] == num_domain and best_var[2] < degree:
                best_var = (var, num_domain, degree)
        return best_var[0]
    
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        x_index, y_index = self.crossword.overlaps[x, y]
        revision = False
        for x_word in self.domains[x].copy():
            found = False
            for y_word in self.domains[y]:
                if x_word[x_index] == y_word[y_index]:
                    found = True
                    break
            if found == False:
                self.domains[x].remove(x_word)
                revision = True
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = set(key for key in self.crossword.overlaps if self.crossword.overlaps[key] is not None)
        while len(arcs) > 0:
            (x,y) = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for var in self.crossword.neighbors(x):
                    arcs.add((var, x))
        return True
    
    def inference(self, assignment):
        """
        Apply AC3 to infer further variable domains based on the current assignment.
        Return True if inference was successful (i.e., no domain is empty),
        otherwise return False.
        """
        # Create an initial list of arcs for the AC3 algorithm
        arcs = set()
        for var in self.crossword.variables:
            if var not in assignment:
                for neighbor in self.crossword.neighbors(var):
                    arcs.add((var, neighbor))

        # Run AC3 and check if the domains are consistent
        return self.ac3(arcs)
    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            # Check if this assignment is consistent
            if self.consistent(new_assignment):
                # Recursively call backtrack with the new assignment
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None

    

    # for case of backtracking with inference

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return a list of the removed values from `self.domains[x]`.
        """
        x_index, y_index = self.crossword.overlaps[x, y]
        removed_values = []
        for x_word in self.domains[x].copy():
            found = False
            for y_word in self.domains[y]:
                if x_word[x_index] == y_word[y_index]:
                    found = True
                    break
            if not found:
                self.domains[x].remove(x_word)
                removed_values.append(x_word)
        return removed_values
    
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return a list of domain modifications to be used for restoration.
        """
        # List to store domain modifications (variable, removed_value)
        domain_changes = []

        if arcs is None:
            arcs = set(key for key in self.crossword.overlaps if self.crossword.overlaps[key] is not None)
        
        while len(arcs) > 0:
            (x, y) = arcs.pop()
            removed_values = self.revise(x, y)
            
            # If we made revisions, record them for backtracking
            if removed_values:
                domain_changes.append((x, removed_values))
                if len(self.domains[x]) == 0:
                    return False, domain_changes
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        arcs.add((neighbor, x))

        return True, domain_changes
    
    def inference(self, assignment):
        """
        Apply AC3 to infer further variable domains based on the current assignment.
        Return True and the domain changes if inference was successful (i.e., no domain is empty),
        otherwise return False and the changes made.
        """
        # Create an initial list of arcs for the AC3 algorithm
        arcs = set()
        for var in self.crossword.variables:
            if var not in assignment:
                for neighbor in self.crossword.neighbors(var):
                    arcs.add((var, neighbor))

        # Run AC3 and return the result and domain changes
        return self.ac3(arcs)
    

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                # Apply inference and track domain changes
                inference_result, domain_changes = self.inference(new_assignment)
                
                if inference_result:
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result

                # Restore domains if inference or assignment was incorrect
                for var, removed_values in domain_changes:
                    self.domains[var].extend(removed_values)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
