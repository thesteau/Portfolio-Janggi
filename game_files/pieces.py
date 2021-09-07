# All pieces that are used in the game of Janggi


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
