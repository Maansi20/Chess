import sys
import os
import pygame
import chess
import time
import threading
from datetime import datetime, timedelta
import random

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_SIZE = 400
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)  # Light brown
DARK_SQUARE = (181, 136, 99)    # Dark brown
HIGHLIGHT = (124, 252, 0)       # Green highlight
MOVE_HIGHLIGHT = (102, 255, 255, 128)  # Light blue with transparency

class ChessGame:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.ai_enabled = True
        self.show_help = False
        self.game_started = False
        
        # Load images
        self.piece_images = {}
        self.load_images()
        
        # Initialize sound
        self.init_sounds()
        
        # Initialize timer
        self.white_time = 180  # 3 minutes
        self.black_time = 180
        self.last_tick = None
        self.current_player = chess.WHITE
        
        # Font for text
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
    
    def load_images(self):
        """Load chess piece images"""
        pieces = ['p', 'r', 'n', 'b', 'q', 'k']
        colors = ['w', 'b']
        
        # Create images directory if it doesn't exist
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # Try to load images, or create placeholder images
        for color in colors:
            for piece in pieces:
                piece_key = color + piece
                image_path = os.path.join(images_dir, f"{piece_key}.png")
                
                try:
                    if os.path.exists(image_path):
                        img = pygame.image.load(image_path)
                    else:
                        # Create a placeholder image
                        img = self.create_placeholder_piece(color, piece)
                        # Save the placeholder for future use
                        pygame.image.save(img, image_path)
                    
                    # Scale the image to fit the square
                    self.piece_images[piece_key] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                except Exception as e:
                    print(f"Error loading image for {piece_key}: {e}")
                    # Create a simple colored rectangle as fallback
                    self.piece_images[piece_key] = self.create_simple_piece(color, piece)
    
    def create_placeholder_piece(self, color, piece_type):
        """Create a placeholder image for a chess piece"""
        # Create a surface for the piece
        img = pygame.Surface((100, 100), pygame.SRCALPHA)
        
        # Colors
        piece_color = (255, 255, 255) if color == 'w' else (0, 0, 0)
        outline_color = (0, 0, 0) if color == 'w' else (255, 255, 255)
        
        # Draw the base circle
        pygame.draw.circle(img, piece_color, (50, 50), 40)
        pygame.draw.circle(img, outline_color, (50, 50), 40, 2)
        
        # Draw piece-specific features
        if piece_type == 'p':  # Pawn
            pygame.draw.circle(img, outline_color, (50, 40), 15, 2)
            pygame.draw.rect(img, piece_color, (35, 50, 30, 20))
            pygame.draw.rect(img, outline_color, (35, 50, 30, 20), 2)
        elif piece_type == 'r':  # Rook
            pygame.draw.rect(img, piece_color, (25, 25, 50, 50))
            pygame.draw.rect(img, outline_color, (25, 25, 50, 50), 2)
            pygame.draw.rect(img, outline_color, (30, 15, 10, 10), 2)
            pygame.draw.rect(img, outline_color, (60, 15, 10, 10), 2)
            pygame.draw.rect(img, outline_color, (45, 15, 10, 10), 2)
        elif piece_type == 'n':  # Knight
            pygame.draw.polygon(img, outline_color, [(30, 20), (70, 30), (60, 70), (30, 60)], 2)
            pygame.draw.circle(img, outline_color, (40, 30), 5)
        elif piece_type == 'b':  # Bishop
            pygame.draw.polygon(img, outline_color, [(50, 20), (70, 70), (30, 70)], 2)
            pygame.draw.circle(img, outline_color, (50, 30), 10, 2)
        elif piece_type == 'q':  # Queen
            pygame.draw.polygon(img, outline_color, [(50, 20), (70, 70), (30, 70)], 2)
            pygame.draw.circle(img, outline_color, (50, 40), 15, 2)
            pygame.draw.rect(img, outline_color, (45, 15, 10, 10), 2)
        elif piece_type == 'k':  # King
            pygame.draw.polygon(img, outline_color, [(50, 20), (70, 70), (30, 70)], 2)
            pygame.draw.rect(img, outline_color, (45, 15, 10, 20), 2)
            pygame.draw.rect(img, outline_color, (40, 10, 20, 5), 2)
        
        return img
    
    def create_simple_piece(self, color, piece_type):
        """Create a simple colored shape for a chess piece"""
        img = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        
        # Colors
        piece_color = (255, 255, 255) if color == 'w' else (0, 0, 0)
        outline_color = (0, 0, 0) if color == 'w' else (255, 255, 255)
        
        # Draw the piece based on type
        if piece_type == 'p':  # Pawn
            pygame.draw.circle(img, piece_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
        elif piece_type == 'r':  # Rook
            pygame.draw.rect(img, piece_color, (SQUARE_SIZE//4, SQUARE_SIZE//4, SQUARE_SIZE//2, SQUARE_SIZE//2))
        elif piece_type == 'n':  # Knight
            points = [(SQUARE_SIZE//4, SQUARE_SIZE//4), (3*SQUARE_SIZE//4, SQUARE_SIZE//4), 
                     (3*SQUARE_SIZE//4, 3*SQUARE_SIZE//4), (SQUARE_SIZE//4, 3*SQUARE_SIZE//4)]
            pygame.draw.polygon(img, piece_color, points)
        elif piece_type == 'b':  # Bishop
            pygame.draw.polygon(img, piece_color, [(SQUARE_SIZE//2, SQUARE_SIZE//4), 
                                                 (3*SQUARE_SIZE//4, 3*SQUARE_SIZE//4), 
                                                 (SQUARE_SIZE//4, 3*SQUARE_SIZE//4)])
        elif piece_type == 'q':  # Queen
            pygame.draw.circle(img, piece_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
            pygame.draw.rect(img, outline_color, (SQUARE_SIZE//3, SQUARE_SIZE//3, SQUARE_SIZE//3, SQUARE_SIZE//3), 2)
        elif piece_type == 'k':  # King
            pygame.draw.circle(img, piece_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
            pygame.draw.line(img, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//4), 
                           (SQUARE_SIZE//2, 3*SQUARE_SIZE//4), 2)
            pygame.draw.line(img, outline_color, (SQUARE_SIZE//4, SQUARE_SIZE//2), 
                           (3*SQUARE_SIZE//4, SQUARE_SIZE//2), 2)
        
        # Draw outline
        if piece_type == 'p':
            pygame.draw.circle(img, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3, 2)
        elif piece_type == 'r':
            pygame.draw.rect(img, outline_color, (SQUARE_SIZE//4, SQUARE_SIZE//4, SQUARE_SIZE//2, SQUARE_SIZE//2), 2)
        elif piece_type in ['n', 'b']:
            if piece_type == 'n':
                points = [(SQUARE_SIZE//4, SQUARE_SIZE//4), (3*SQUARE_SIZE//4, SQUARE_SIZE//4), 
                         (3*SQUARE_SIZE//4, 3*SQUARE_SIZE//4), (SQUARE_SIZE//4, 3*SQUARE_SIZE//4)]
            else:
                points = [(SQUARE_SIZE//2, SQUARE_SIZE//4), (3*SQUARE_SIZE//4, 3*SQUARE_SIZE//4), 
                         (SQUARE_SIZE//4, 3*SQUARE_SIZE//4)]
            pygame.draw.polygon(img, outline_color, points, 2)
        elif piece_type in ['q', 'k']:
            pygame.draw.circle(img, outline_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3, 2)
        
        # Add text label
        text = self.small_font.render(piece_type.upper(), True, outline_color)
        text_rect = text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
        img.blit(text, text_rect)
        
        return img
    
    def init_sounds(self):
        """Initialize sound effects"""
        # Initialize mixer
        pygame.mixer.init()
        
        # Create sounds directory if it doesn't exist
        sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
        
        # Sound file paths
        self.sound_files = {
            "move": os.path.join(sounds_dir, "move.wav"),
            "capture": os.path.join(sounds_dir, "capture.wav"),
            "check": os.path.join(sounds_dir, "check.wav"),
            "checkmate": os.path.join(sounds_dir, "checkmate.wav"),
            "stalemate": os.path.join(sounds_dir, "stalemate.wav"),
            "select": os.path.join(sounds_dir, "select.wav"),
            "timeout": os.path.join(sounds_dir, "timeout.wav")
        }
        
        # Create simple sounds if they don't exist
        for sound_name, filepath in self.sound_files.items():
            if not os.path.exists(filepath):
                self._create_simple_sound(sound_name, filepath)
        
        # Load sounds
        self.sounds = {}
        for sound_name, filepath in self.sound_files.items():
            try:
                self.sounds[sound_name] = pygame.mixer.Sound(filepath)
            except:
                print(f"Could not load sound: {filepath}")
    
    def _create_simple_sound(self, sound_type, filepath):
        """Create a simple sound file"""
        try:
            import numpy as np
            import wave
            import struct
            
            # Parameters for sound generation
            sample_rate = 44100
            duration = 0.5  # seconds
            
            # Create a simple sine wave based on the sound type
            if sound_type == "move":
                freq = 440  # A4
                volume = 0.5
            elif sound_type == "capture":
                freq = 330  # E4
                volume = 0.7
            elif sound_type == "check":
                freq = 660  # E5
                volume = 0.8
            elif sound_type == "checkmate":
                freq = 880  # A5
                volume = 1.0
                duration = 1.0
            elif sound_type == "stalemate":
                freq = 220  # A3
                volume = 0.6
                duration = 1.0
            elif sound_type == "select":
                freq = 550  # C#5
                volume = 0.4
                duration = 0.2
            elif sound_type == "timeout":
                freq = 110  # A2
                volume = 0.9
                duration = 1.0
            else:
                freq = 440  # A4
                volume = 0.5
            
            # Generate a simple sine wave
            num_samples = int(sample_rate * duration)
            samples = np.sin(2 * np.pi * np.arange(num_samples) * freq / sample_rate)
            samples = (samples * volume * 32767).astype(np.int16)
            
            # Write to a WAV file
            with wave.open(filepath, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes (16 bits)
                wav_file.setframerate(sample_rate)
                for sample in samples:
                    wav_file.writeframes(struct.pack('<h', sample))
        except ImportError:
            print(f"Could not create sound file {filepath} - numpy not available")
        except Exception as e:
            print(f"Error creating sound file {filepath}: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def draw_board(self):
        """Draw the chess board"""
        # Calculate board position to center it
        board_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
        board_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        
        # Draw the squares
        for rank in range(8):
            for file in range(8):
                # Calculate square position
                x = board_x + file * SQUARE_SIZE
                y = board_y + (7 - rank) * SQUARE_SIZE  # Flip rank for display
                
                # Determine square color
                is_light = (rank + file) % 2 == 0
                color = LIGHT_SQUARE if is_light else DARK_SQUARE
                
                # Draw the square
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight selected square
                square = chess.square(file, rank)
                if self.selected_square == square:
                    pygame.draw.rect(self.screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)
                
                # Highlight valid moves
                if square in self.valid_moves:
                    # Create a transparent surface for the highlight
                    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, MOVE_HIGHLIGHT, (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                    self.screen.blit(highlight_surface, (x, y))
        
        # Draw rank and file labels
        for i in range(8):
            # Rank labels (1-8)
            rank_label = self.small_font.render(str(8 - i), True, BLACK)
            self.screen.blit(rank_label, (board_x - 20, board_y + i * SQUARE_SIZE + SQUARE_SIZE//2 - 10))
            
            # File labels (a-h)
            file_label = self.small_font.render(chr(97 + i), True, BLACK)
            self.screen.blit(file_label, (board_x + i * SQUARE_SIZE + SQUARE_SIZE//2 - 5, board_y + BOARD_SIZE + 10))
    
    def draw_pieces(self):
        """Draw the chess pieces on the board"""
        # Calculate board position to center it
        board_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
        board_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        
        # Draw each piece
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Get the file and rank (0-7)
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                
                # Calculate the position on screen
                x = board_x + file * SQUARE_SIZE
                y = board_y + (7 - rank) * SQUARE_SIZE  # Flip rank for display
                
                # Get the piece image
                piece_symbol = piece.symbol().lower()
                color = 'w' if piece.color == chess.WHITE else 'b'
                piece_key = color + piece_symbol
                
                if piece_key in self.piece_images:
                    self.screen.blit(self.piece_images[piece_key], (x, y))
    
    def draw_ui(self):
        """Draw UI elements like timer, game status, etc."""
        # Draw timer
        white_timer = self.format_time(self.white_time)
        black_timer = self.format_time(self.black_time)
        
        white_text = self.font.render(f"White: {white_timer}", True, BLACK)
        black_text = self.font.render(f"Black: {black_timer}", True, BLACK)
        
        self.screen.blit(white_text, (20, 20))
        self.screen.blit(black_text, (20, 50))
        
        # Draw current player indicator
        current_player = "White" if self.board.turn == chess.WHITE else "Black"
        player_text = self.font.render(f"Current Player: {current_player}", True, BLACK)
        self.screen.blit(player_text, (WINDOW_WIDTH - 250, 20))
        
        # Draw AI status
        ai_status = "ON" if self.ai_enabled else "OFF"
        ai_text = self.font.render(f"AI: {ai_status}", True, BLACK)
        self.screen.blit(ai_text, (WINDOW_WIDTH - 250, 50))
        
        # Draw game status
        status_text = ""
        if self.board.is_check():
            status_text = "CHECK!"
        if self.game_over:
            if self.winner == "Draw":
                status_text = "Game Over - Draw"
            else:
                status_text = f"Game Over - {self.winner} wins!"
        
        if status_text:
            status_render = self.font.render(status_text, True, (255, 0, 0))
            self.screen.blit(status_render, ((WINDOW_WIDTH - status_render.get_width()) // 2, WINDOW_HEIGHT - 50))
        
        # Draw help text
        help_text = self.small_font.render("Press H for help", True, BLACK)
        self.screen.blit(help_text, (WINDOW_WIDTH - 150, WINDOW_HEIGHT - 30))
    
    def draw_help_screen(self):
        """Draw the help screen overlay"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with alpha
        self.screen.blit(overlay, (0, 0))
        
        # Draw help text
        title = self.font.render("CHESS GAME HELP", True, WHITE)
        self.screen.blit(title, ((WINDOW_WIDTH - title.get_width()) // 2, 100))
        
        help_items = [
            "Click on a piece to select it",
            "Click on a highlighted square to move",
            "R: Reset the game",
            "H: Toggle this help screen",
            "A: Toggle AI opponent",
            "Q: Quit the game"
        ]
        
        y = 150
        for item in help_items:
            text = self.small_font.render(item, True, WHITE)
            self.screen.blit(text, ((WINDOW_WIDTH - text.get_width()) // 2, y))
            y += 30
        
        # Draw exit instruction
        exit_text = self.small_font.render("Press H to return to the game", True, WHITE)
        self.screen.blit(exit_text, ((WINDOW_WIDTH - exit_text.get_width()) // 2, WINDOW_HEIGHT - 100))
    
    def format_time(self, seconds):
        """Format time in MM:SS format"""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_timer(self):
        """Update the chess timer"""
        if not self.game_started or self.game_over:
            return
        
        current_time = time.time()
        if self.last_tick is None:
            self.last_tick = current_time
            return
        
        elapsed = current_time - self.last_tick
        self.last_tick = current_time
        
        if self.board.turn == chess.WHITE:
            self.white_time -= elapsed
            if self.white_time <= 0:
                self.white_time = 0
                self.game_over = True
                self.winner = "Black"
                self.play_sound("timeout")
        else:
            self.black_time -= elapsed
            if self.black_time <= 0:
                self.black_time = 0
                self.game_over = True
                self.winner = "White"
                self.play_sound("timeout")
    
    def get_square_at_pos(self, pos):
        """Convert screen position to chess square"""
        x, y = pos
        
        # Calculate board position
        board_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
        board_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        
        # Check if click is within the board
        if (board_x <= x < board_x + BOARD_SIZE and 
            board_y <= y < board_y + BOARD_SIZE):
            
            # Calculate file and rank
            file = (x - board_x) // SQUARE_SIZE
            rank = 7 - ((y - board_y) // SQUARE_SIZE)  # Flip rank for display
            
            # Convert to square index
            return chess.square(file, rank)
        
        return None
    
    def get_valid_moves(self, square):
        """Get all valid moves for the piece at the given square"""
        valid_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                valid_moves.append(move.to_square)
        return valid_moves
    
    def ai_move(self):
        """Make a move for the AI"""
        if not self.ai_enabled or self.game_over or self.board.turn == chess.WHITE:
            return
        
        # Small delay to make AI moves more natural
        time.sleep(0.5)
        
        # Try to use stockfish if available
        try:
            from stockfish import Stockfish
            stockfish = Stockfish()
            stockfish.set_fen_position(self.board.fen())
            best_move = stockfish.get_best_move()
            if best_move:
                move = chess.Move.from_uci(best_move)
                if move in self.board.legal_moves:
                    self.make_move(move)
                    return
        except:
            pass
        
        # Fallback to random move
        legal_moves = list(self.board.legal_moves)
        if legal_moves:
            move = random.choice(legal_moves)
            self.make_move(move)
    
    def make_move(self, move):
        """Make a chess move and update the game state"""
        # Check if it's a capture
        is_capture = self.board.is_capture(move)
        
        # Make the move
        self.board.push(move)
        
        # Start timer after white's first move
        if not self.game_started and self.board.fullmove_number > 1:
            self.game_started = True
            self.last_tick = time.time()
        
        # Play appropriate sound
        if self.board.is_check():
            self.play_sound("check")
        elif is_capture:
            self.play_sound("capture")
        else:
            self.play_sound("move")
        
        # Check for game end conditions
        if self.board.is_checkmate():
            self.game_over = True
            self.winner = "White" if not self.board.turn else "Black"
            self.play_sound("checkmate")
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            self.game_over = True
            self.winner = "Draw"
            self.play_sound("stalemate")
    
    def reset_game(self):
        """Reset the game to the starting position"""
        self.board.reset()
        self.selected_square = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.white_time = 180
        self.black_time = 180
        self.last_tick = None
        self.game_started = False
        self.play_sound("select")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle keyboard input
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_h:
                        self.show_help = not self.show_help
                    elif event.key == pygame.K_a:
                        self.ai_enabled = not self.ai_enabled
                
                # Handle mouse input
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.show_help:
                    if event.button == 1:  # Left click
                        square = self.get_square_at_pos(event.pos)
                        
                        if square is not None:
                            if self.selected_square is None:
                                # Try to select a piece
                                piece = self.board.piece_at(square)
                                if piece is not None and piece.color == self.board.turn:
                                    self.selected_square = square
                                    self.valid_moves = self.get_valid_moves(square)
                                    self.play_sound("select")
                            else:
                                # Try to move the selected piece
                                if square in self.valid_moves:
                                    move = chess.Move(self.selected_square, square)
                                    
                                    # Check for promotion
                                    if (self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                                        ((square >= 56 and self.board.turn == chess.WHITE) or
                                         (square <= 7 and self.board.turn == chess.BLACK))):
                                        # Always promote to queen for simplicity
                                        move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                                    
                                    self.make_move(move)
                                    
                                    # AI's turn
                                    if self.ai_enabled and not self.game_over and self.board.turn == chess.BLACK:
                                        threading.Thread(target=self.ai_move).start()
                                
                                # Clear selection
                                self.selected_square = None
                                self.valid_moves = []
            
            # Update timer
            self.update_timer()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_pieces()
            self.draw_ui()
            
            # Draw help screen if active
            if self.show_help:
                self.draw_help_screen()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()