# All board logic that is used in the game of Janggi
from game_files import pieces as pce


class Board:
    """ Represents the Janggi Chess Board  Handles game board logic. Does not handle piece/board gameplay logic."""

    def __init__(self):
        """ Initializes the Janggi Game board.
        Data members:
            board: The game board - begins as None because the game was never "set".
                        When start_board() is invoked, then a dictionary board will be stored."""
        self._board = None  # Board starts as none

    # Set ups for the board
    def setup_game(self):
        """ Sets up the game of Jangji."""
        self.start_board()
        self.setup_red_initializer()
        self.setup_blue_initializer()

    def start_board(self):
        """ Starts the game board up by the algebraic notation [letter: col][number: row].
            rows: 1 to 10
            cols: a to i """
        self._board = {
            1: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            2: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            3: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            4: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            5: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            6: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            7: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            8: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            9: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None},
            10: {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}
        }

    # Piece initializers
    def setup_red_initializer(self):
        """ Set up the red side of the warring faction."""
        if self._board is None:      # Set the board up if the board was never initiated.
            self.start_board()

        # Cols a - c (Player's right, opponent's left)
        self.set_square('a1', pce.Chariot('red'))
        self.set_square('b1', pce.Elephant('red'))
        self.set_square('c1', pce.Horse('red'))

        self.set_square('b3', pce.Cannon('red'))

        self.set_square('a4', pce.Soldier('red'))
        self.set_square('c4', pce.Soldier('red'))

        # Cols g - i (Player's left, opponent's right)
        self.set_square('g1', pce.Elephant('red'))
        self.set_square('h1', pce.Horse('red'))
        self.set_square('i1', pce.Chariot('red'))

        self.set_square('h3', pce.Cannon('red'))

        self.set_square('g4', pce.Soldier('red'))
        self.set_square('i4', pce.Soldier('red'))

        # Cols d - f (Palace and outside)
        self.set_square('d1', pce.Guard('red'))
        self.set_square('f1', pce.Guard('red'))
        self.set_square('e2', pce.General('red'))

        self.set_square('e4', pce.Soldier('red'))

    def setup_blue_initializer(self):
        """ Set up the blue side of the warring faction."""
        if self._board is None:      # Set the board up if the board was never initiated.
            self.start_board()

        # Cols a - c (Player's left, opponent's right)
        self.set_square('a10', pce.Chariot('blue'))
        self.set_square('b10', pce.Elephant('blue'))
        self.set_square('c10', pce.Horse('blue'))

        self.set_square('b8', pce.Cannon('blue'))

        self.set_square('a7', pce.Soldier('blue'))
        self.set_square('c7', pce.Soldier('blue'))

        # Cols g - i (Player's right, opponent's left)
        self.set_square('g10', pce.Elephant('blue'))
        self.set_square('h10', pce.Horse('blue'))
        self.set_square('i10', pce.Chariot('blue'))
        self.set_square('h8', pce.Cannon('blue'))
        self.set_square('g7', pce.Soldier('blue'))
        self.set_square('i7', pce.Soldier('blue'))

        # Cols d - f (Palace and outside)
        self.set_square('d10', pce.Guard('blue'))
        self.set_square('f10', pce.Guard('blue'))
        self.set_square('e9', pce.General('blue'))

        self.set_square('e7', pce.Soldier('blue'))

    # Square manipulators
    def get_square(self, square_coord):
        """ Returns the content on a certain address.
            Parameter:
                square_coord: The entry location assuming the following format "[col][row]"""
        if self.is_within_board(square_coord):  # Check if this is a valid coordinate
            return self._board[int(square_coord[1:])][square_coord[0]]  # Return the object/contents.
        return None  # If a piece does not exist, then return None.

    def set_square(self, square_coord, content=None):
        """ Sets the content on a certain address.
            Parameters:
                square_coord: The entry location assuming the following format "[col][row]
                content: Optional for None for no data value, otherwise, the object contents to be injected to the board.
                """
        if self.is_within_board(square_coord):  # As long as this is a valid coordinate
            self._board[int(square_coord[1:])][square_coord[0]] = content       # Default None

    def move_square(self, move_from, move_to):
        """ Moves the board pieces to a specific space.
            Does not check for game logic other than the out-of-boundary case.
            Each position-entry will Override existing positions.
            However, movement history is retained for move-undo.
            Returns None if the move is not within the board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                """
        if self.is_within_board(move_from, move_to):
            # Check if the move is within bounds and is a possible non-empty "from" target.

            from_piece = self._board[int(move_from[1:])][move_from[0]]  # Store the from data.
            to_piece = self._board[int(move_to[1:])][move_to[0]]

            self.set_square(move_from)  # Sets the former square to None
            self.set_square(move_to, from_piece)  # Inject the from data to new space.

            return [move_from, move_to, from_piece, to_piece]  # A list is exported

    def undo_move_sq(self, moved_from, moved_to, from_piece, to_piece):  # explicit arguments to pass.
        """ Undo the board move pieces."""
        if self.is_within_board(moved_from, moved_to):
            # Check if the move is within bounds and is a possible non-empty "from" target.
            self.set_square(moved_from, from_piece)
            self.set_square(moved_to, to_piece)

    # Board methods
    def get_board(self):
        """ Returns the board as an object."""
        return self._board

    # Human friendly board view
    def show_board(self):
        """ Returns and pretty prints the current state of the board."""
        if self._board is None:      # Set the board up if the board was never initiated.
            self.start_board()

        # pretty print the columns
        cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        dividers = '-'
        dividers_a = dividers * 58
        dividers_b = (dividers * 27) + '\\-----/' + (dividers * 24)  # Palace
        dividers_c = (dividers * 27) + '/-----\\' + (dividers * 24)

        # print dividers to separate visual view.
        print(dividers_a)
        print('  | ', end='')

        for each_col in cols:
            print(each_col, end='    |')

        print()
        print(dividers_a)

        # Print the board contents
        for each_row, each_row_dat in self._board.items():
            row_num = str(each_row)
            if each_row < 10:
                row_num = '_' + row_num

            print(row_num + '| ', end='')

            for each_col, each_sq in each_row_dat.items():
                if each_sq is None:
                    contents = '     '
                else:
                    contents = each_sq.get_player()[0].upper() + '.' + each_sq.get_name()[0:3]
                print(contents+'|', end='')    # Prints out the board

            # Palace Structure
            print()
            if each_row in [1, 8]:
                print(dividers_b)
            elif each_row in [2, 9]:
                print(dividers_c)
            else:
                print(dividers_a)

    # Board checks
    def is_within_board(self, move_from, move_to='a1'):
        """ Returns a boolean true or false by checking if the movement is within the limitations of the game.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                    Optional entry is within the board: 'a1'."""
        rows = [str(num) for num in range(1,11)]  # The move is a string entry - so convert number to string.
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

        try:  # In the event a non-string was entered; try-except block.
            # Check if the entry are within the string element logic: integer range from 2 to 3.
            if 1 < len(move_from) < 4 and 1 < len(move_to) < 4:

                # Check each individual entry is within the boundary
                if move_from[0] in columns and move_to[0] in columns and move_from[1:] in rows and move_to[1:] in rows:
                    return True
            return False  # Any criteria failures will return false.
        except:  # All exception errors will return false. No messages necessary.
            return False

    def is_palace(self, selected_square):
        """ Returns a boolean true or false if the squares are considered a palace.
            Method does not handle movement restrictions. Only indicates if square is palace or not.
            Parameter:
                selected_square: The entry location assuming the following format "[col][row]"
            """
        palace_columns = ['d', 'e', 'f']
        palace_rows = ['1', '2', '3', '8', '9', '10']  # Strings as this check is only to verify if it is palace or not.

        if self.is_within_board(selected_square):
            # As long as the movement is valid, proceed
            if selected_square[0] in palace_columns and selected_square[1:] in palace_rows:
                return True
        return False  # All other cases, then the piece is not in the palace.

    def invalid_palace_movement(self, move_from, move_to):
        """ Returns a boolean of true or false if the movement in the palace is allowed."""
        invalid_pairs = [
            ['e1', 'd2'], ['e1', 'f2'], ['e3', 'd2'], ['e3', 'f2'],     # Red palace pairs
            ['d2', 'e1'], ['f2', 'e1'], ['d2', 'e3'], ['f2', 'e3'],
            ['e8', 'd9'], ['e8', 'f9'], ['e10', 'd9'], ['e10', 'f9'],    # Blue palace pairs
            ['d9', 'e8'], ['f9', 'e8'], ['d9', 'e10'], ['f9', 'e10']
        ]
        move_pair = [move_from, move_to]

        if self.is_palace(move_from) and self.is_palace(move_to):
            # All squares in palace scenario
            for each_pair in invalid_pairs:  # Cycle through each pairing.
                if move_pair == each_pair:
                    return True  # Invalid movement
        return False  # Movement has passed the check
