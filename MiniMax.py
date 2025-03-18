# Games: AI, AI, AI, ME, ME (i found a cheat HEHEHE), ME, ME, Me, me, me

import numpy as np
import threading
import random
import time

# This class handles the timed input, that pressure the user and the AI to play.
# Utilizes Daemon threads, which automatically stop when the main program exits.
class InputWithTimeout:
    def __init__(self, prompt, timeout=5):
        self.prompt = prompt
        self.timeout = timeout
        self.input_value = None
        self.thread = threading.Thread(target=self.get_input, daemon=True)  # Daemon thread here
    
    def get_input(self):
        try:
            self.input_value = input(self.prompt)
        except EOFError:
            self.input_value = None  # Handle Ctrl+D or unexpected EOF
    
    def run(self):
        self.thread.start()
        self.thread.join(self.timeout)  # Wait up to timeout
        if self.thread.is_alive():
            return None  # Timed out
        return self.input_value

# Size of Board
ROWS = 6
COLUMNS = 7

# Function to return an array of 0's symbolizing the board of play
def createBoard():
    return np.zeros((ROWS, COLUMNS))

# Function to print the board in a nice looking way 
def print_board(board):
    print("\n  " + "   ".join(str(c) for c in range(COLUMNS)))  # Column numbers
    print("-" * (COLUMNS * 3 + COLUMNS))  # Separator line
    
    for r in range(ROWS):
        row = ""
        for c in range(COLUMNS):
            piece = board[r][c]
            if piece == 0:
                row += " . "  # Empty
            elif piece == 1:
                row += " X "  # Player 1
            elif piece == 2:
                row += " O "  # Player 2

        # Column separators
        # Example: ["ABC", "DEF", "GHI"] becomes "ABC|DEF|GHI".
        # range(start, stop, increment by)
        print("|" + "|".join(row[i:i+3] for i in range(0, len(row), 3)) + "|")
    print("-" * (COLUMNS * 3 + COLUMNS))  # Separator line

# Function that evaluates the given "window", this is used for the AI to decide where to go.
# A window is any bit of 4 space in a line throughout the board.
def evaluate_window(window, piece):
    opp_piece = 1 if piece == 2 else 2

    # The evaluation is just saying that you want to have more pieces than the opponent
    # In as many windows as possible. So in most cases this leads to the AI stopping a 4 in a row.
    return window.count(piece) - window.count(opp_piece)

# Function that evaluates the board for a winner... 4 pieces in a row
def checkWinner(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMNS - 3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check vertical locations for win
    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check positively sloped diagonals
    for c in range(COLUMNS - 3):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check negatively sloped diagonals
    for c in range(COLUMNS - 3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False  # No winner

# Functoin that determines all of the places the player is able to play
def get_valid_locations(board):
    return [col for col in range(COLUMNS) if board[0][col] == 0]

# Function to tell if a node concludes the game, so if theres a winner of the board is full (draw)
# timed_minimax() relies on this to stop searching, assign final scores, and prevent unneccessary calcs
def is_terminal_node(board):
    return checkWinner(board, 1) or checkWinner(board, 2) or len(get_valid_locations(board)) == 0

# Evaluates how good a board configuration is for the AI player
# Prioritizes center and evaluates each windows score to determine the best place to go.
def score_position(board, piece):
    score = 0

    ## Score center column (prioritize middle)
    center_array = [int(board[i][COLUMNS//2]) for i in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROWS):
        row_array = [int(board[r][c]) for c in range(COLUMNS)]
        for c in range(COLUMNS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMNS):
        col_array = [int(board[r][c]) for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    ## Score positive sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    ## Score negative sloped diagonal
    for r in range(3, ROWS):
        for c in range(COLUMNS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

# This function allows the AI to search deeper if time permits, rather than being at a fixed depth.
def iterative_deepening_minimax(board, max_time, is_maximizing):
    start_time = time.time()
    time_limit = start_time + max_time
    best_move = None

    depth = 1

    # This loop is to go through the minimax tree, depth by depth
    while True:
        if time.time() >= time_limit:
            break  # Stop if out of time
        
        # Will return the best move for each depth
        # Interesting question would be if the best one on one depth is always better than a previous
        move, score = timed_minimax(board, depth, -np.inf, np.inf, is_maximizing, time_limit)
        
        if move is not None:
            best_move = move  # Update best move if a valid one is found
        
        depth += 1  # Go deeper for next iteration

    return best_move

# This function is a minimax implementation, but with respect to being timed.
# works in tandem with the iterative_deepening_minimax function.
def timed_minimax(board, depth, alpha, beta, maximizingPlayer, time_limit):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    # Max depth, or game over, or time exeeded
    if depth == 0 or is_terminal or time.time() >= time_limit:
        if is_terminal:
            if checkWinner(board, 2):
                return (None, 1000000)
            elif checkWinner(board, 1):
                return (None, -1000000)
            else:
                return (None, 0)
        else: # depth==0 or is_terminal
            return (None, score_position(board, 2))

    if maximizingPlayer: # maximizingPlayer is a parameter passed into function
        value = -np.inf
        best_col = None
        for col in valid_locations:
            temp_board = np.copy(board)

            # Goes through and tests the AI placing a piece in each column
            for row in range(ROWS - 1, -1, -1):
                if temp_board[row][col] == 0:
                    temp_board[row][col] = 2  # AI
                    break

            # Get the score of that new board where the AI played.
            _, new_score = timed_minimax(temp_board, depth - 1, alpha, beta, False, time_limit)
            if time.time() >= time_limit:
                break  # Stop if out of time

            #Maximizing, so if the score is greater, save the column the AI should play in.
            if new_score > value:
                value = new_score
                best_col = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:
        value = np.inf
        best_col = None
        for col in valid_locations:
            temp_board = np.copy(board)

            # Goes through and tests placing a piece in each column
            for row in range(ROWS - 1, -1, -1):
                if temp_board[row][col] == 0:
                    temp_board[row][col] = 1  # USER
                    break
            # Get the score of the new board where the PLAYER could play
            _, new_score = timed_minimax(temp_board, depth - 1, alpha, beta, True, time_limit)
            if time.time() >= time_limit:
                break  # Stop if out of time

            # Minimizing, so if its worse for the player keep that.
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# -------------------------
# Main game loop
# -------------------------

board = createBoard()
print_board(board)

gameOver = False
turn = 0

while not gameOver:
    # Handles whose turn it is.
    currentPlayer = 1 if turn % 2 == 0 else 2
    print(f"Player {currentPlayer}'s turn.")

    # Human player
    if currentPlayer == 1:
        input_handler = InputWithTimeout("Please Choose a Column (0-6): ", timeout=10)
        user_input = input_handler.run()

        # If the player doesn't play, it selects a random valid column
        if user_input is None:
            print("⏰ Time's up! Making a random move for you!\n")
            valid_columns = get_valid_locations(board)
            if not valid_columns:
                print("The board is full! It's a draw!")
                break
            selection = random.choice(valid_columns)
        # Handles invalid inputs, which allow the user to try again.
        else:
            try:
                selection = int(user_input)
                if selection not in get_valid_locations(board):
                    print("Invalid or full column. Try Again.\n")
                    continue
            except ValueError:
                print("Invalid input. Try Again..\n")
                continue
    else:
        # AI player
        print("AI is thinking...")
        selection = iterative_deepening_minimax(board, max_time=10, is_maximizing=True)  # e.g., 5 seconds
        if selection is None:
            selection = random.choice(get_valid_locations(board))  # Fallback, shouldn't happen tho.

    # Place piece
    for row in range(ROWS - 1, -1, -1):
        if board[row][selection] == 0:
            board[row][selection] = currentPlayer
            break

    print_board(board)
    
    # Check for winner
    if checkWinner(board, currentPlayer):
        print(f"🎉 PLAYER {currentPlayer} WINS!! 🎉")
        gameOver = True
    else:
        turn += 1
        if turn == ROWS * COLUMNS:
            gameOver = True
            print("GAME DRAW")

