# Author: Steven Au
# Date: 3/1/21
# Description: A Janggi chess game playable between two players.

class JanggiGame:
    """ Represents the Korean Chess game called Janggi. Handles game play logic."""

    def __init__(self):
        """ Initializes the Janggi Game Logic.
            Data members:
                game_state: Determines the state of the game.
                player_turn: Determines the turn of the player - begins with blue. Should alternative with red.
                game_board: Composition of the Board class for all Pieces class objects stored within the board.
                                The division allows for Board and Pieces to operate what they are required of.
                                    Otherwise, the Janggi class brings both the classes together alongside its
                                    own logic similar to a web page.
                move_counter: Stores the history of the move counter per player. Used to determine the first turn.
                pieces_loc: Coordinate location of all pieces for check status purposes.
                gen_coords: Used as an absolute determinate of a General piece location per player.
            """
        self._game_state = 'UNFINISHED'  # Starts with unfinished. Possible states: 'RED_WON', 'BLUE_WON', 'UNFINISHED'
        self._player_turn = 'blue'        # Initializes to blue. Possible players: 'red', 'blue'
        self._game_board = Board()       # This game has a board
        self._move_counter = {'red': 0, 'blue': 0}  # Tracks the move history.
        self._pieces_loc = {'red': [], 'blue': []}  # Coordinate list
        self._gen_coords = {'red': None, 'blue': None}  # General Coordinates for check "destination" purposes.

    # Movement
    def make_move(self, move_from, move_to):
        """ Returns a boolean of the move made.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
            If the move is valid, then the game is updated accordingly
            for where a turn is changed and game status is determined after the "Executed" Attack Phase.
            Phases are delineated as followed:
                Turn Phase - The turn is determined per the player. Draws out the board if the game has not initiated.
                Evaluation Phase - The game state is checked.
                Main Phase 1 - Moves to be conducted are checked if they are valid - returns to turn phase if invalid.
                        Returns False and restarts to the Turn Phase
                Battle Phase - The move is made - a player may directly take out a piece or get a general into check.
                Main Phase 2 - Game status is re-evaluated and applies any necessary conditions of the game.
                Close Phase - Per the events of main phase 2 - the game turn is switched to the opposing player.
                        Returns True and restarts to the Turn Phase of the opponent.
            (* Each move does not guarantee a trap card per the general to be in check status.)
        """
        # Turn Phase
        self.start_game()   # Auto start game - only works if it was not started yet.
        # Opponent Determinant
        opponent = self.get_opponent_turn()

        # Evaluation Phase
        # Is the game still playable? (No player has won yet)
        if self._game_state != 'UNFINISHED':
            return False

        # Check Status - Note that thte general's location is dynamic.
        self.gather_active_pieces()  # Update the records
        self.check_moves_in_check()

        # Is this move even in the game board?
        if not self._game_board.is_within_board(move_from, move_to):
            return False

        # Main Phase 1
        # Checks for move legality and if the piece is owned by the player.
        #  Is the piece owned by the player?
        #   If the move is valid, then proceed to piece selector if tree.
        if not self.piece_to_board_selector(move_from, move_to):
            return False

        # Battle Phase
        history = self._game_board.move_square(move_from, move_to)

        self.gather_active_pieces()  # Update the records
        self.check_moves_in_check()

        # If the general is in check and the move did not remove the check status, undo move.
        # Unless the piece is the general - in this case, the player is electing to forfeit.
        if self.is_in_check(self.get_player_turn()) and self._game_board.get_square(move_from).get_name() != 'General':
            self._game_board.undo_move_sq(history[0], history[1], history[2], history[3])
            self.gather_active_pieces()  # Retract to previous records.
            self.check_moves_in_check()
            return False

        # Main Phase 2
        self.check_gen_mod()  # General positions check "check" status

        # Change game state - check counter increments on a change turn or after a move is made.
        # Since the counter is called on the opponents turn, the 2nd count or more equates to the win condition.
        if self.get_general_dat(self.get_player_turn()).get_chk_count() >= 2:
            self.toggle_game_state(opponent)
        elif self.get_general_dat(opponent).get_chk_count() >= 2:
            self.toggle_game_state(self.get_player_turn())
        else:  # Defaults to UNFINISHED
            self.toggle_game_state()

        # Close Phase
        self.change_player_turn()  # Change player turn
        return True  # Yes, based on that card game.

    # Validity check
    def is_in_check(self, player):
        """ Checks the player's general if it is in check.
            Returns the Boolean True if a check was found.
            Parameter:
                Requires a player to be passed to check whether their general is currently in Check."""
        self.start_game()
        self.gather_active_pieces()

        # Get the general's coordinates of a certain player.
        gen_piece = self.get_general_dat(player.lower())  # Not none square, then do the get square data method.

        if gen_piece.get_check_status():
            return True
        return False

    # Move from/to move coordinator
    def piece_to_board_selector(self, move_from, move_to):
        """ Returns the appropriate movement boolean of a selected piece on the game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
        """
        square_data = self._game_board.get_square(move_from)
        in_board = self._game_board.is_within_board(move_from, move_to)
        destination_data = self._game_board.get_square(move_to)

        try:
            landing_area = destination_data.get_player()  # In case this is None, then still proceed
        except:
            landing_area = None

        if square_data is not None and in_board:
            # Check if the square is has a piece and movements are within the game board.

            # Player cannot move opposing player's pieces.
            if square_data.get_player() != self._player_turn:
                return False

            # If from and To are the same, the player passes up their turn.
            if move_from == move_to:  # Acts as a forfeit move if the player is already in check.
                return True            # As long as the piece is not the general

            # Player cannot eliminate own pieces
            if square_data.get_player() == self._player_turn and landing_area == self._player_turn:
                return False

            piece_name = square_data.get_name()
            # We have a piece, then route to the individual movements
            # Each checks if the moves can be made.
            # Moves will be checked if it's restricted after the distance check.
            if piece_name == 'Soldier':
                return self.soldier_movement(move_from, move_to, square_data)
            elif piece_name == 'Cannon':
                return self.cannon_movement(move_from, move_to, square_data)
            elif piece_name == 'Chariot':
                return self.chariot_movement(move_from, move_to, square_data)
            elif piece_name == 'Horse':
                return self.horse_movement(move_from, move_to, square_data)
            elif piece_name == 'Elephant':
                return self.elephant_movement(move_from, move_to, square_data)
            elif piece_name == 'Guard':
                return self.guard_movement(move_from, move_to, square_data)
            elif piece_name == 'General':
                return self.general_movement(move_from, move_to, square_data)

        return False  # None or not in board

    # Game piece/board/game movement logic
    def move_dist_data(self, move_from, move_to):
        """ Returns the movement distance data list of the piece.
            Assumes that the movement check is valid prior this method.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
            """
        column_to_number = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5,'f': 6, 'g': 7, 'h': 8, 'i': 9}

        fcol = move_from[0]         # from column
        tcol = move_to[0]           # to column
        frow = int(move_from[1:])   # from row
        trow = int(move_to[1:])     # to row

        col_dif = column_to_number[tcol] - column_to_number[fcol]  # Take the difference per the translated col
        row_dif = trow - frow  # Take the difference per the row

        if self._player_turn == 'red':
            if row_dif < 0:
                forward_direction = 'backward'
            elif row_dif == 0:
                forward_direction = 'stay'
            else:
                forward_direction = 'forward'
            if col_dif < 0:
                side_direction = 'right'  # This is from a top down perspective where RED starts from A1 to I4
            elif col_dif == 0:
                side_direction = 'stay'
            else:
                side_direction = 'left'
        else:
            if row_dif < 0:
                forward_direction = 'forward'
            elif row_dif == 0:
                forward_direction = 'stay'
            else:
                forward_direction = 'backward'
            if col_dif < 0:
                side_direction = 'left'  # This is from a top down perspective where RED starts from A1 to I4
            elif col_dif == 0:
                side_direction = 'stay'
            else:
                side_direction = 'right'

        diag_direction = 'normal'  # Can be just a pure stay-stay or a normal non-diagonal movement.
        if 'stay' not in [forward_direction, side_direction]:
            diag_direction = 'diagonal'

        return [abs(col_dif), abs(row_dif), forward_direction, side_direction, diag_direction]  # Returns move details

    # Mechs
    def cannon_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the cannon to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        piece_name = square_data.get_name()

        if self.mech_move_inval_checker(move_from, move_to, move_data, piece_name):
            return False

        # Restriction check
        # Cannons cannot take out/land on/eat any cannons
        landing_sq = self._game_board.get_square(move_to)
        if landing_sq is not None:
            if landing_sq.get_name() == 'Cannon':
                return False

        # Cannot be moved on player's first turn.
        if self._move_counter[self._player_turn] == 0:
            return False
        return True

    def chariot_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the chariot to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        piece_name = square_data.get_name()

        if self.mech_move_inval_checker(move_from, move_to, move_data, piece_name):
            return False
        return True

    # Beasts
    def elephant_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the elephant to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        max_movement = square_data.get_move()
        beast_num = self._game_board.get_square(move_from).get_beast_num()

        valid_move = True

        if self.beast_move_inval_checker(move_from, move_to, move_data, max_movement, beast_num):
            valid_move = False

        return valid_move

    def horse_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the horse to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        max_movement = square_data.get_move()
        beast_num = self._game_board.get_square(move_from).get_beast_num()

        valid_move = True

        if self.beast_move_inval_checker(move_from, move_to, move_data, max_movement, beast_num):
            valid_move = False

        return valid_move

    # Humans
    def soldier_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the soldier to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        max_movement = square_data.get_move()

        if self.human_move_inval_checker(move_from, move_to, move_data, max_movement):
            return False

        # Restriction check
        if move_data[2] == 'backward':
            # Soldiers cannot move backwards
            return False
        return True  # Movement is valid.

    def guard_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the guard to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        max_movement = square_data.get_move()

        if self.human_move_inval_checker(move_from, move_to, move_data, max_movement):
            return False

        # Restriction check - All movements are confined in the palace
        if not (self._game_board.is_palace(move_from) and self._game_board.is_palace(move_to)):
            return False

        return True

    def general_movement(self, move_from, move_to, square_data):
        """ Handles the movements of the general to game board.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                square_data: The square data object contents usually with a piece data.
            """
        # Move check
        move_data = self.move_dist_data(move_from, move_to)
        max_movement = square_data.get_move()

        if self.human_move_inval_checker(move_from, move_to, move_data, max_movement):
            return False

        # Restriction check - All movements are confined in the palace
        if not self._game_board.is_palace(move_from) or not self._game_board.is_palace(move_to):
            return False

        # Check state restrictions
        self.check_moves_in_check()

        # Temporary movement to check if the movement is valid.
        history = self._game_board.move_square(move_from, move_to)
        self.gather_active_pieces()
        self.check_moves_in_check()

        # IF the general became checked, then this move cannot be done.
        if self.is_in_check(self.get_player_turn()):
            self._game_board.undo_move_sq(history[0], history[1], history[2], history[3])
            self.gather_active_pieces()  # Retract to previous records.
            self.check_moves_in_check()
            return False

        # When things are moved, you have to put them back! Otherwise, Nonetype error for 3 hours.
        # So this has to appear twice.
        self._game_board.undo_move_sq(history[0], history[1], history[2], history[3])

        return True

    # Invalid Move Group Checkers
    def mech_move_inval_checker(self, move_from, move_to, move_data, piece_name):
        """ Returns the boolean of the mechanical piece movement check if it is invalid.
            Mechanical pieces are: Chariot (Mechanical Wagon) and Cannon. These both operate similarly.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                move_data: The data list values used to evaluate the move.
                piece_name: The name of the piece, only used for differentiating movements.
            """
        # No diagonal movement allowed unless in palace
        if move_data[4] == 'diagonal' and not self._game_board.is_palace(move_from):
            return True

        # Col to num translation
        column_to_number = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9}
        number_to_column = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i'}

        # Columns and Rows
        from_col = move_from[0]
        to_col = move_to[0]
        from_row = int(move_from[1:])
        to_row = int(move_to[1:])

        blockade = False
        blockade_count = 0      # For cannon
        cannon_jump_check = 0   # For cannon

        # Movement checks
        if move_data[2] != 'stay' and move_data[4] == 'normal':  # Forward/Backwards is extracted, not diagonal
            # THe column must be the same - otherwise move_data[4] indicates diagonal

            step_type = 1
            if from_row > to_row:  # Shift the step type due to where the coordinates are located.
                step_type = -1

            for each_movement in range(from_row, to_row, step_type):  # Step up or Step down.
                if each_movement == from_row:  # Skip the origin square because that's where the piece is.
                    continue

                path_dat = self._game_board.get_square(from_col + str(each_movement))

                if path_dat is not None:  # Path data not None will be checked.
                    blockade = True
                    blockade_count += 1
                    if path_dat.get_name() == 'Cannon':
                        cannon_jump_check += 1

        elif move_data[3] != 'stay' and move_data[4] == 'normal':  # Move data indicates a sideways direction.
            # The row must be the same - otherwise move_data[4] indicates diagonal

            from_col_num = column_to_number[from_col]
            to_col_num = column_to_number[to_col]

            step_type = 1
            if from_col_num > to_col_num:  # Shift the step type due to where the coordinates are located.
                step_type = -1

            for each_movement in range(from_col_num, to_col_num, step_type):  # Step up or Step down.
                if each_movement == from_col_num:  # Skip the origin square because that's where the piece is.
                    continue

                path_dat = self._game_board.get_square(number_to_column[each_movement] + move_from[1:])

                if path_dat is not None:  # Path data not None will be checked.
                    blockade = True
                    blockade_count += 1
                    if path_dat.get_name() == 'Cannon':
                        cannon_jump_check += 1

        else:  # Diagonal direction - palace conditions apply.
            if not self._game_board.is_palace(move_from):
                return True  # Diagonal movement is only allowed in the palace - Must start at palace

            if move_data[0] != move_data[1]:
                return True  # Diagonal movement have to be a 45 degree movement

            col_step_num = 1
            if move_data[3] == 'left':
                col_step_num = -1
            col_num = column_to_number[from_col]

            step_type = 1
            if from_row > to_row:  # Shift the step type due to where the coordinates are located.
                step_type = -1

            for each_movement in range(from_row, to_row, step_type):  # Step up or Step down.
                if each_movement == from_row:  # Skip the origin square because that's where the piece is.
                    col_num += col_step_num
                    continue

                path_dat = self._game_board.get_square(number_to_column[col_num] + str(each_movement))

                if path_dat is not None:  # Path data not None will be checked.
                    blockade = True
                    blockade_count += 1
                    if path_dat.get_name() == 'Cannon':
                        cannon_jump_check += 1

                col_num += col_step_num  # Add constant to mutable to "increment" to the respective direction

            if piece_name == 'Chariot':
                # Chariot has to have all movements within the palace to move diagonal.
                if not self._game_board.is_palace(move_to):
                    return True

                if self._game_board.invalid_palace_movement(move_from, move_to):  # All moves have to be valid
                    return True                                                   # per the diagonal of the palace

        if piece_name == 'Cannon':
            # No "screen" to jump over and 2 or more pieces are in the way - can hop only 1. Cannot hop over cannons.
            if not blockade or blockade_count > 1 or cannon_jump_check != 0:
                return True

        else:  # Chariot
            if blockade:  # Chariots cannot "jump" so a blockade is a not allowed.
                return True

        return False  # Movement is valid

    def beast_move_inval_checker(self, move_from, move_to, move_data, max_movement, beast_num):
        """ Returns the boolean of the beast piece movement check if it is invalid.
            Beasts are: Elephant (3) and Horse (2).
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                move_data: The data list values used to evaluate the move.
                max_movement: The maximum movement distance of the piece
                beast_num: Used to find the maximum diagonal move difference.
            """
        # Col to num translation
        column_to_number = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9}
        number_to_column = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i'}

        # Index short keys
        from_col = move_from[0]
        to_col = move_to[0]
        from_row = int(move_from[1:])
        to_row = int(move_to[1:])

        # Differentials of index
        col_delta = column_to_number[from_col] - column_to_number[to_col]
        row_delta = from_row - to_row

        # Diagonal direction of the beast
        if col_delta < 0:  # Right
            if row_delta < 0:  # Down
                diagonalization = 'downright'  # Quadrant 4
            else:  # Up
                diagonalization = 'upright'  # Quadrant 1
        else:  # Left
            if row_delta < 0:  # Down
                diagonalization = 'downleft'  # Quad 3
            else:  # Up
                diagonalization = 'upleft'  # Quad 2

        # Of the board perspective - Cross - block initialized
        block_left = False
        block_right = False
        block_up = False
        block_down = False

        if (move_data[0] + move_data[1]) in [max_movement, 0] and beast_num in [move_data[0], move_data[1]]:
            # Value has to be of the beast's movement max and must have the maximum movement differential of the beast.
            # 3 for Elephant, 2 for Horse.

            # From epicenter (From the piece)
            left_col = column_to_number[from_col] - 1
            right_col = column_to_number[from_col] + 1
            up_row = from_row - 1       # Assuming the coordinate system is up decreasing, down is increasing.
            down_row = from_row + 1     # Like a spreadsheet - A1 is top left

            # Border check of beast piece
            if left_col <= 0:
                block_left = True
            if right_col >= 10:
                block_right = True
            if up_row <= 0:
                block_up = True
            if down_row >= 11:
                block_down = True

            # Check the directions if they have pieces. The current blocks are based on the above "board" limit.
            if not block_left:
                left_sq = number_to_column[left_col] + move_from[1:]  # Address
                left_dat = self._game_board.get_square(left_sq)       # Data
                if left_dat is not None:
                    block_left = True
            if not block_right:
                right_sq = number_to_column[right_col] + move_from[1:]
                right_dat = self._game_board.get_square(right_sq)
                if right_dat is not None:
                    block_right = True
            if not block_up:
                up_sq = from_col + str(up_row)
                up_dat = self._game_board.get_square(up_sq)
                if up_dat is not None:
                    block_up = True
            if not block_down:
                down_sq = from_col + str(down_row)
                down_dat = self._game_board.get_square(down_sq)
                if down_dat is not None:
                    block_down = True

            # All directions are blocked
            if block_left and block_right and block_up and block_down:
                return True

            # Diagonal direction check
            # Return the appropriate boolean from the diagonal.
            if move_data[0] > move_data[1]:  # Column is larger - Restricted to Right or Left moves
                # As long as the direction is not blocked, then the restriction check will go into the diagonal check.
                # For the horse or if the direction is blocked for the elephant, the move wil lbe sent to True.

                if diagonalization == 'upleft':
                    if not block_left:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, -2, -1)
                if diagonalization == 'downleft':
                    if not block_left:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, -2, 1)
                if diagonalization == 'upright':
                    if not block_right:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, 2, -1)
                if diagonalization == 'downright':
                    if not block_right:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, 2, 1)

            else:  # Row is larger - restricted to up or down moves.
                if diagonalization == 'upleft':
                    if not block_up:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, -1, -2)
                if diagonalization == 'downleft':
                    if not block_down:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, -1, 2)
                if diagonalization == 'upright':
                    if not block_up:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, 1, -2)
                if diagonalization == 'downright':
                    if not block_down:
                        return self.beast_diag_helper(beast_num, number_to_column, column_to_number, from_col, from_row, 1, 2)

        return True  # Move is out of bounds or blocked

    def beast_diag_helper(self, beast_num, number_to_column, column_to_number, from_col, from_row, col_delta, row_delta):
        """ Returns the boolean for the diagonal movement of a beast piece.
            The affected piece used in this evaluation will be the Elephant.
            Otherwise, as long as the horse was not blocked, then invalid is false.
            Parameters:
                beast_num: The number indicating which piece it is by movement terms.
                number_to_column: The translation of the number to a column letter
                column_to_number: The translation of the column letter to a number
                from_col: The origin column that the move is being made
                from_row: The origin row that the move is being made
                col_delta: The directional change of the column to be evaluated
                row_delta:The directional change of the row to be evaluated
            """
        if beast_num == 3:  # Only the elephant will do the additional diagonal check.
            new_col = number_to_column[column_to_number[from_col] + col_delta]
            new_row = str(from_row + row_delta)
            new_sq = new_col + new_row
            new_dat = self._game_board.get_square(new_sq)

            if new_dat is not None:
                return True

        return False  # Horse is not blocked perpendicularly! Or the Elephant doesn't have any obstruction!

    def human_move_inval_checker(self, move_from, move_to, move_data, max_movement):
        """ Returns the boolean of the human piece movement check if it is invalid.
            Humans are: Soldier, Guard, and General.
            Parameters:
                move_from: The entry origin location assuming the following format "[col][row]"
                move_to: The entry destination location assuming the following format "[col][row]"
                move_data: The data list values used to evaluate the move.
                max_movement: The maximum movement distance of the piece allowed.
            """
        if (move_data[0] + move_data[1]) > max_movement:
            # If the move sum is greater than 1, then this move could be in the palace.
            if (move_data[0] + move_data[1]) == 2 and move_data[4] == 'diagonal' and self._game_board.is_palace(move_from):
                # Palace movement check
                if self._game_board.invalid_palace_movement(move_from, move_to):
                    # The move is in the palace
                    return True  # Invalid movement choices
                if not self._game_board.is_palace(move_to):
                    return True  # Is from the palace but moving to outside diagonally - not valid.
            else:
                return True  # Diagonal movement and is not from the palace - invalid
        return False  # All movements are valid

    # Game Status Data - getters
    def get_game_state(self):
        """ Returns the current state of the game.
            Possible outputs: 'RED_WON', 'BLUE_WON', 'UNFINISHED'."""
        return self._game_state

    def get_player_turn(self):
        """ Returns who is the current player's turn.
            Possible outputs: 'red', 'blue'."""
        return self._player_turn

    def get_opponent_turn(self, player=None):
        """ Returns who is the current player's opponent turn.
            Possible outputs: 'red', 'blue'.
            Parameter:
                player: Optional - defaults to None to get the player's turn. Otherwise, explicitly determine the opponent.
            """
        if player is None:
            player = self._player_turn

        if player == 'red':
            opponent = 'blue'
        else:
            opponent = 'red'
        return opponent

    # Gameplay methods
    def change_player_turn(self):
        """ Changes the player turn, binarily.
            Possible turns: red, blue."""
        if self._player_turn == 'red':
            self._player_turn = 'blue'
            self._move_counter['red'] += 1  # Red has moved
        else:
            self._player_turn = 'red'
            self._move_counter['blue'] += 1  # Blue has moved

    def set_player_turn(self, player):
        """ Sets the player turn explicitly.
            Parameter:
                player: The player's turn to be set to."""
        self._player_turn = player

    def get_general_dat(self, player):
        """ Returns the general's data of the player.
            Parameter:
                player: The player evaluated to get their general's square data."""
        self.start_game()
        return self._game_board.get_square(self._gen_coords[player])

    def set_general_check(self, player, boolean):
        """ Sets the general of a certain player to the check status.
            Parameters:
                player: The player evaluated to get their general piece data.
                boolean: Simply a true or false to set the general's check state.
            """
        self.start_game()
        self.get_general_dat(player).set_check_status(boolean)

    def gather_active_pieces(self):
        """ Gathers all the coordinate pieces of the players and store into their respective list.
            This is used to evaluate the condition of the current board pieces."""
        red_list = []  # Initiate the lists
        blue_list = []

        # Gather the items on the board: each_row is the row number key, row data are the values.
        for each_row, each_row_dat in self._game_board.get_board().items():

            # Each col is column key, sq is the value.
            for each_col, each_sq in each_row_dat.items():

                coordinate = each_col + str(each_row)  # Coordinates are created each iteration

                if each_sq is None:
                    continue  # Skip the square

                if each_sq.get_player() == 'red':  # If it is owned by red
                    red_list.append(coordinate)
                    if each_sq.get_name() == 'General':
                        self._gen_coords['red'] = coordinate
                else:                              # else blue
                    blue_list.append(coordinate)
                    if each_sq.get_name() == 'General':
                        self._gen_coords['blue'] = coordinate

            # Inject the coordinate list.
            self._pieces_loc['red'] = red_list
            self._pieces_loc['blue'] = blue_list

    def check_moves_in_check(self):
        """ Returns a boolean after applying the appropriate check status to a general.
            From all the gathered pieces, check if the pieces would "check" the opposing generals.
                If so, then a check status will be applied to the player's piece.
            Attacker are all pieces of the player evaluated.
            Defender is the opposing player's general."""
        self.gather_active_pieces()
        current_turn = self._player_turn  # Save the current turn
        sides = ['red', 'blue']

        for a_side in sides:  # Check all sides to exhaust the list

            self.set_player_turn(a_side)  # Temporarily change the turn
            opponent = self.get_opponent_turn(a_side)
            was_checked = False

            atk_pieces = self._pieces_loc[a_side]  # The pieces used to evaluate
            gen_coord = self._gen_coords[opponent]  # The general evaluated

            for each_piece in atk_pieces:

                if self.piece_to_board_selector(each_piece, gen_coord):
                    # Apply the status and then prevent the status to be removed until further gameplay.
                    self.set_general_check(opponent, True)  # Apply the check status
                    was_checked = True

                if not was_checked:
                    self.set_general_check(opponent, False)  # No check status were found

        self.set_player_turn(current_turn)  # Return to the original state

    def check_gen_mod(self):
        """ Applies a check counter per the Generals accordingly when invoked."""
        player = self.get_player_turn()
        opponent = self.get_opponent_turn(player)

        if self.is_in_check(player):
            self.get_general_dat(player).add_chk_count()
        else:
            self.get_general_dat(player).sub_chk_count()
        if self.is_in_check(opponent):
            self.get_general_dat(opponent).add_chk_count()
        else:
            self.get_general_dat(opponent).sub_chk_count()

    # Game Operations
    def start_game(self):
        """ Starts up the game up if the game was not started."""
        # if the game board is None, then run the board setup method.
        if self._game_board.get_board() is None:
            self._game_board.setup_game()
            self.gather_active_pieces()
            self.check_moves_in_check()
            self.check_gen_mod()

    def restart_game(self):
        """ Restarts the entire game of Janggi."""
        self._game_board.setup_game()    # The board is flipped back to the beginning set up.
        self._game_state = 'UNFINISHED'  # Starts with unfinished. Possible states: 'RED_WON', 'BLUE_WON', 'UNFINISHED'
        self._player_turn = 'red'        # Initializes to red. Possible players: 'red', 'blue'
        self._move_counter = {'red': 0, 'blue': 0}  # Tracks the move history.
        self._pieces_loc = {'red': [], 'blue': []}  # Coordinate location of all pieces for check status purposes.
        self._gen_coords = {'red': None, 'blue': None}  # General's location

    def show_game(self):
        """ Prints the current game board on a viewer friendly fashion."""
        self.start_game()

        # Turn Details
        current = self.get_player_turn().upper()
        opponent = self.get_opponent_turn().upper()
        move_num = self._move_counter[self.get_player_turn()]+1

        print('Current Player:', current, '| Turn:', move_num, '| Previous Board Move:', opponent)
        self._game_board.show_board()

    def get_move_counter(self):
        """ Returns the move counter of the current game."""
        return self._move_counter

    def get_game(self):
        """ Returns the raw game board object."""
        return self._game_board

    def toggle_game_state(self, game_state='UNFINISHED'):
        """ Changes the current state of the game given the status. Can manually set the state.
            'RED_WON', 'BLUE_WON', or 'UNFINISHED'."""
        if game_state == 'red':
            game_state = 'RED_WON'
        elif game_state == 'blue':
            game_state = 'BLUE_WON'
        self._game_state = game_state

    # Optional swapping mechanic
    def swap_piece(self, first_square, second_square):
        """ Swaps the Elephant with Horse of the same side only on the first turn of the owning player.
            Parameters:
                first_square: The first target piece square. Entered as [col][num]
                second_square: The second target piece square. Entered as [col][num]"""
        self.start_game()

        swapables = ['Elephant', 'Horse']  # THe only pieces that can be swapped on the first turn of this game.

        if self._game_board.is_within_board(first_square, second_square):
            # If this is a valid move, then proceed with the swap check.

            # Grab the pieces
            first_piece = self._game_board.get_square(first_square)
            second_piece = self._game_board.get_square(second_square)

            if self.swap_logic(self._player_turn, self._move_counter, first_piece, second_piece, swapables, first_square, second_square):
                # IF all the logic holds, then swap the pieces.
                self._game_board.set_square(first_square, second_piece)
                self._game_board.set_square(second_square, first_piece)

    def swap_logic(self, player, counter, first_piece, second_piece, swap_list, first_square, second_square):
        """ Returns the boolean on whether the swap could work or not.
            Parameters:
                player: The player currently evaluated to swap adjacent pieces.
                counter: Counter is used to check if the player turn is their first turn only. Cannot swap any other turn.
                first_piece: First piece to be swap with
                second_piece: Second piece to swap with
                swap_list: The list is for only the elephant and horse.
                first_square: Location selected to swap from
                second_square: Location select to swap to
            """
        if counter[player] == 0 and first_piece.get_player() == player and second_piece.get_player() == player:
            # player check
            if first_piece.get_name() in swap_list and second_piece.get_name() in swap_list:
                # Piece name check
                if first_square[0] in ['b', 'c'] and second_square[0] in ['b', 'c'] or first_square[0] in ['g', 'h'] and second_square[0] in ['g', 'h']:
                    # Square check
                    return True
        return False


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
        self.set_square('a1', Chariot('red'))
        self.set_square('b1', Elephant('red'))
        self.set_square('c1', Horse('red'))

        self.set_square('b3', Cannon('red'))

        self.set_square('a4', Soldier('red'))
        self.set_square('c4', Soldier('red'))

        # Cols g - i (Player's left, opponent's right)
        self.set_square('g1', Elephant('red'))
        self.set_square('h1', Horse('red'))
        self.set_square('i1', Chariot('red'))

        self.set_square('h3', Cannon('red'))

        self.set_square('g4', Soldier('red'))
        self.set_square('i4', Soldier('red'))

        # Cols d - f (Palace and outside)
        self.set_square('d1', Guard('red'))
        self.set_square('f1', Guard('red'))
        self.set_square('e2', General('red'))

        self.set_square('e4', Soldier('red'))

    def setup_blue_initializer(self):
        """ Set up the blue side of the warring faction."""
        if self._board is None:      # Set the board up if the board was never initiated.
            self.start_board()

        # Cols a - c (Player's left, opponent's right)
        self.set_square('a10', Chariot('blue'))
        self.set_square('b10', Elephant('blue'))
        self.set_square('c10', Horse('blue'))

        self.set_square('b8', Cannon('blue'))

        self.set_square('a7', Soldier('blue'))
        self.set_square('c7', Soldier('blue'))

        # Cols g - i (Player's right, opponent's left)
        self.set_square('g10', Elephant('blue'))
        self.set_square('h10', Horse('blue'))
        self.set_square('i10', Chariot('blue'))
        self.set_square('h8', Cannon('blue'))
        self.set_square('g7', Soldier('blue'))
        self.set_square('i7', Soldier('blue'))

        # Cols d - f (Palace and outside)
        self.set_square('d10', Guard('blue'))
        self.set_square('f10', Guard('blue'))
        self.set_square('e9', General('blue'))

        self.set_square('e7', Soldier('blue'))

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


class Pieces:
    """ Represents the Janggi pieces.
        Each piece will hold its individual information."""

    def __init__(self, player):
        """ Initializes the Janggi pieces.
            Data member:
                player: The player in which the piece will now belong to."""
        self._player = player.lower()

    def get_player(self):
        """ Returns the owner of the piece."""
        return self._player


class Chariot(Pieces):
    """ Represents the Chariot piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
            Data members:
                name: The name of the piece.
                move: max movement limits."""
        super().__init__(player)
        self._name = 'Chariot'
        self._move = 10  # Within the game limits

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move


class Elephant(Pieces):
    """ Represents the Elephant piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
            Data members:
                name: The name of the piece.
                move: max movement limits."""
        super().__init__(player)
        self._name = 'Elephant'
        self._move = 5

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move

    def get_beast_num(self):
        """ Returns the beast number (Colloquial on diagonal move difference)."""
        return 3


class Horse(Pieces):
    """ Represents the Horse piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
             Data members:
                name: The name of the piece.
                move: max movement limits."""
        super().__init__(player)
        self._name = 'Horse'
        self._move = 3

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move

    def get_beast_num(self):
        """ Returns the beast number (Colloquial on diagonal move difference)."""
        return 2


class Cannon(Pieces):
    """ Represents the Cannon piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
            Data members:
                name: The name of the piece.
                move: max movement limits."""
        super().__init__(player)
        self._name = 'Cannon'
        self._move = 10

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move


class Soldier(Pieces):
    """ Represents the Soldier piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
            Data members:
                name: The name of the piece.
                move: max movement limits."""
        super().__init__(player)
        self._name = 'Soldier'
        self._move = 1

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move


class Guard(Pieces):
    """ Represents the Guard piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
            Data members:
                name: The name of the piece.
                move: max movement limits."""
        super().__init__(player)
        self._name = 'Guard'
        self._move = 1

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move


class General(Pieces):
    """ Represents the General piece."""

    def __init__(self, player):
        """ Initiates the piece's data accordingly.
            Data members:
                name: The name of the piece.
                move: max movement limits.
                check: The check status of the piece.
                chk_count: The number of check have applied to the piece."""
        super().__init__(player)
        self._name = 'General'
        self._move = 1
        self._check = False
        self._chk_count = 0

    def __repr__(self):
        """ Pretty print the name of the piece."""
        return self.get_player()[0].upper()+'.'+self._name[:3]

    def get_name(self):
        """ Returns the name of the piece."""
        return self._name

    def get_move(self):
        """ Returns the maximum movement square."""
        return self._move

    def get_check_status(self):
        """ Returns whether the piece is in check or not."""
        return self._check

    def get_chk_count(self):
        """ Returns the amount of checks imposed to the piece."""
        return self._chk_count

    def set_check_status(self, boolean=False):
        """ Sets the check status of the piece."""
        self._check = boolean

    def add_chk_count(self):
        """ Adds a check count to the piece."""
        self._chk_count += 1

    def sub_chk_count(self):
        """ Subtracts a check count to the piece."""
        self._chk_count -= 1
        if self._chk_count < 0:
            self._chk_count = 0  # Negative check count is not possible.


if __name__ == "__main__":
    # Base game sample checker
    game = JanggiGame()
    move_result = game.make_move('c1', 'e3')  # should be False because it's not Red's turn
    blue_in_check = game.is_in_check('blue')  # should return False
    game.make_move('a4', 'a5')  # should return True
    state = game.get_game_state()  # should return UNFINISHED
    game.make_move('b7', 'b6')  # should return True
    game.make_move('b3', 'b6')  # should return False because it's an invalid move
    game.make_move('a1', 'a4')  # should return True
    game.make_move('c7', 'd7')  # should return True
    game.make_move('a4', 'a4')  # this will pass the Red's turn and return True
    # game.show_game()
