import numpy as np
import threading
import random

ROWS = 5
COLUMNS = 6

def createBoard():
    return np.zeros((ROWS, COLUMNS))

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

# -------------------------
# Threaded input function
# -------------------------

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


# -------------------------
# Main game loop
# -------------------------

board = createBoard()
print(board)

gameOver = False
turn = 0

while not gameOver:
    currentPlayer = 1 if turn % 2 == 0 else 2
    print(f"Player {currentPlayer}'s turn. You have 5 seconds to make a move!")

    # Get player input with timeout
    input_handler = InputWithTimeout("Please Choose a Column (0-5): ", timeout=5)
    user_input = input_handler.run()

    if user_input is None:
        print("⏰ Time's up! Making a random move for you!\n")
        
        # Find all valid columns
        valid_columns = [col for col in range(COLUMNS) if board[0][col] == 0]
        
        if not valid_columns:
            print("The board is full! It's a draw!")
            gameOver = True
            # Exit the game loop
        
        user_input = random.choice(valid_columns)  # Pick a random valid column

    # Validate input
    try:
        selection = int(user_input)
        if not (0 <= selection < COLUMNS):
            print("Invalid column number. Please enter a number between 0 and 5.\n")
            continue  # Ask again
        if board[0][selection] != 0:
            print("Column is full. Please try a different column.\n")
            continue  # Ask again
    except ValueError:
        print("Invalid input. Please enter a valid number between 0 and 5.\n")
        continue  # Ask again

    # Place piece
    for row in range(ROWS - 1, -1, -1):
        if board[row][selection] == 0:
            board[row][selection] = currentPlayer
            break

    print(board, "\n")

    # Check for winner
    if checkWinner(board, currentPlayer):
        print(f"🎉 PLAYER {currentPlayer} WINS!! 🎉")
        gameOver = True
    else:
        turn += 1  # Next turn
        if turn == ROWS*COLUMNS:
            gameOver = True
            print("GAME DRAW")
