# Portfolio-Janggi

Korean Chess Game

## Getting Started
You can initiate a game by running the following:
```python
from game_files import game as jg

game = jg.JanggiGame()
```

The main methods to play during your game turn is the following:
```python
game.make_move('a4', 'a5')
game.show_game()
```
## Gameplay Notes
- Game turns are based on the piece selected between player ```RED``` and ```BLUE```.
- Each valid move executed will then alternate the turn. 
  - Otherwise, the player must select a valid piece to make a valid move.
- Game ends when a checkmate is achieved
- Please see the ```Excel``` file for initial board positioning.
- Please see a Janggi playing guide for piece and movement details.
  - EG: Horse Piece movements and Checkmate conditions

## Program Structure
```graphql
portfolio-janggi/
├─ JanggiGame.py    # Main program execution
└─ program/
    ├─ __init__.py
    ├─ board.py     # Handles the gameboard logic
    ├─ game.py      # Handles the gameplay logic
    └─ pieces.py    # Handles the valid pieces and piece logic.
```

## Sample Game Interface
```
Current Player: BLUE | Turn: 2 | Previous Board Move: RED
----------------------------------------------------------
  | a    |b    |c    |d    |e    |f    |g    |h    |i    |
----------------------------------------------------------
_1| R.Cha|R.Ele|R.Hor|R.Gua|     |R.Gua|R.Ele|R.Hor|R.Cha|
---------------------------\-----/------------------------
_2|      |     |     |     |R.Gen|     |     |     |     |
---------------------------/-----\------------------------
_3|      |R.Can|     |     |     |     |     |R.Can|     |
----------------------------------------------------------
_4| R.Sol|     |R.Sol|     |R.Sol|     |R.Sol|     |R.Sol|
----------------------------------------------------------
_5|      |     |     |     |     |     |     |     |     |
----------------------------------------------------------
_6|      |     |     |     |     |     |     |     |     |
----------------------------------------------------------
_7| B.Sol|     |     |B.Sol|B.Sol|     |B.Sol|     |B.Sol|
----------------------------------------------------------
_8|      |B.Can|     |     |     |     |     |B.Can|     |
---------------------------\-----/------------------------
_9|      |     |     |     |B.Gen|     |     |     |     |
---------------------------/-----\------------------------
10| B.Cha|B.Ele|B.Hor|B.Gua|     |B.Gua|B.Ele|B.Hor|B.Cha|
----------------------------------------------------------
```

## Future Additions
- User interface to play the game without using the terminal.

## Author
Steven Au

## License
See the LICENSE.md for details
