"""
Tic Tac Toe X
"""
import copy, random

X        = "X"
O        = "O"
EMPTY    = None

WIN_X    = [X,X,X]
WIN_O    = [O,O,O]
"""Esta son los renglones ganadores"""

board_action = [
    (0,0), (0,1), (0,2),
    (1,0), (1,1), (1,2),
    (2,0), (2,1), (2,2)
]
"""Representacion del las posiciones del tablero"""

def extrac(board):
    #Columnas 
    col_1 = [board[0][0] , board[1][0] , board[2][0]]
    col_2 = [board[0][1] , board[1][1] , board[2][1]]
    col_3 = [board[0][2] , board[1][2] , board[2][2]]

    #Diagonal
    dia_1 = [board[0][0] , board[1][1] , board[2][2]]
    dia_2 = [board[0][2] , board[1][1] , board[2][0]]
    
    cols = (col_1, col_2, col_3)
    diag = (dia_1, dia_2)

    return cols, diag

def tie_terminal(board):
    """
    En caso de que el tablero termine en un empate
    """
    #En caso de que las casillas esten todas llenas
    stop = 0
    for i in range(3):
        if stop:
            break
        for j in range(3):
            if board[i][j] is EMPTY:
                stop = 1
                break
    else:
        return True #Si termino en empate
    return False   #Si no termino en empate

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns X who has the next turn on a board.
    """
    #El primer jugador sera la X, entoces el siguiente es O
    
    if terminal(board):
        return   
    
    if not board == initial_state():
        count_x = sum(row.count(X) for row in board)
        count_o = sum(row.count(O) for row in board)
        return X if count_x == count_o else O
    return X
    
def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board): 
        return

    moves = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                moves.add((i,j))

    return moves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    
    if action not in board_action:
        raise Exception("Movimiento invalido")
    
    stop = 0
    board_modified = copy.deepcopy(board)

    for i in range(3):
        if stop: 
            break
        for j in range(3):
            if (i,j) == action:
                board_modified[i][j] = player(board_modified)
                stop = 1
                break
    return board_modified

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    cols, diags = extrac(board)
    
    for row in board:
        if row == WIN_X:
            return X
        if row == WIN_O:
            return O
    
    for col in cols:
        if col == WIN_X:
            return X
        if col == WIN_O:
            return O
    
    for diag in diags:
        if diag == WIN_X:
            return X
        if diag == WIN_O:
            return O
    
    return None
    
def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    cols, diags = extrac(board)
    
    #Ahora toca comparar los renglones
    for row in board:
        #track_moves.clear()
        if row == WIN_X or row == WIN_O:
            return True
    
    for col in cols:
        
        if col == WIN_X or col == WIN_O:
            return True
    
    for diag in diags:
        
        if diag == WIN_X or diag == WIN_O:
            #track_moves.clear()
            return True
    
    return tie_terminal(board)

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    #Solo llamar cuando terminal sea igual a true
    if not win:
        return 0
    
    return 1 if win is X else -1

def min_value(board):
    """
    Funcion de min value, usando en el algoritmo del minimax
    """
    if terminal(board):
        return utility(board)
    
    value = float('inf')

    for action in actions(board):

        value = min(value, max_value(result(board, action)))

    return value

def max_value(board):
    """
    Funcion del max value, usado en el algoritmo del minimax 
    """
    if terminal(board):
        return utility(board) 
    
    value = -float('inf')

    for action in actions(board): 
        value = max(value, min_value(result(board, action)))

    return value

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    Assumes that X is the maximizer and O is the minimizer.
    """
    best_actions = []

    if terminal(board):
        return None 

    current_player = player(board)

    if current_player == 'X':
        # Maximizar para X
        best_value = -float('inf')
        for action in actions(board):
            value = min_value(result(board, action))
            if value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)
    else:
        # Minimizar para O
        best_value = float('inf')
        for action in actions(board):
            value = max_value(result(board, action))
            if value < best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

    # Retorna una de las mejores acciones al azar
    return random.choice(best_actions)