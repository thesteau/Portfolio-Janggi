# Author: Steven Au
# Date: 3/1/21
# Description: A Janggi chess game playable between two players.
from game_files import game as jg

def main():
    """ Sample starting game with preset moves."""
    # Base game sample checker

    game = jg.JanggiGame()
    move_result = game.make_move('c1', 'e3')  # should be False because it's not Red's turn
    blue_in_check = game.is_in_check('blue')  # should return False
    game.make_move('a4', 'a5')  # should return True
    state = game.get_game_state()  # should return UNFINISHED
    game.make_move('b7', 'b6')  # should return True
    game.make_move('b3', 'b6')  # should return False because it's an invalid move
    game.make_move('a1', 'a4')  # should return True
    game.make_move('c7', 'd7')  # should return True
    game.make_move('a4', 'a4')  # this will pass the Red's turn and return True
    game.show_game()

if __name__ == "__main__":
    main()
