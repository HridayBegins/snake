import tkinter as tk
import random
import json
import os

# Game constants
GRID_SIZE = 25
INITIAL_SPEED = 120
SPEED_INCREMENT = 2
MIN_SPEED = 50

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game - Full Screen Edition")

        # Get screen dimensions
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # Full screen mode
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#2C3E50")

        # Calculate grid based on screen size
        self.GRID_COLS = self.screen_width // GRID_SIZE
        self.GRID_ROWS = (self.screen_height - 100) // GRID_SIZE
        self.WIDTH = self.GRID_COLS * GRID_SIZE
        self.HEIGHT = self.GRID_ROWS * GRID_SIZE

        # Center the game area
        self.offset_x = (self.screen_width - self.WIDTH) // 2
        self.offset_y = (self.screen_height - self.HEIGHT) // 2 + 30

        # High score file
        self.score_file = "snake_highscore.json"
        self.high_score = self.load_high_score()

        # Main canvas (full screen with dark background)
        self.canvas = tk.Canvas(root, width=self.screen_width, height=self.screen_height, 
                                bg="#2C3E50", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Game area background (darker)
        self.game_bg = self.canvas.create_rectangle(
            self.offset_x - 5, self.offset_y - 5,
            self.offset_x + self.WIDTH + 5, self.offset_y + self.HEIGHT + 5,
            fill="#1A252F", outline="#34495E", width=3
        )

        # UI Frame (top)
        self.score_label = tk.Label(root, text="Score: 0", 
                                    font=("Arial", 28, "bold"), bg="#2C3E50", fg="white")
        self.score_label.place(x=50, y=20)

        self.high_label = tk.Label(root, text="High: " + str(self.high_score), 
                                   font=("Arial", 28, "bold"), bg="#2C3E50", fg="#F1C40F")
        self.high_label.place(x=250, y=20)

        self.level_label = tk.Label(root, text="Level: 1", 
                                     font=("Arial", 28, "bold"), bg="#2C3E50", fg="#2ECC71")
        self.level_label.place(x=450, y=20)

        self.hint_label = tk.Label(root, text="SPACE = Start/Pause | WASD/Arrows = Move | ESC = Quit | F11 = Toggle Full Screen", 
                                   font=("Arial", 14), bg="#2C3E50", fg="#95A5A6")
        self.hint_label.place(x=self.screen_width - 650, y=25)

        # Game state
        self.score = 0
        self.level = 1
        self.game_running = False
        self.game_over = False
        self.paused = False
        self.speed = INITIAL_SPEED

        # Snake
        self.snake = []
        self.snake_direction = "RIGHT"
        self.next_direction = "RIGHT"

        # Food
        self.food = None
        self.food_x = 0
        self.food_y = 0

        # Draw grid pattern (subtle)
        self.draw_grid()

        # Show start screen
        self.show_start_screen()

        # Bind keys
        self.root.bind("<space>", self.toggle_game)
        self.root.bind("<Up>", lambda e: self.change_direction("UP"))
        self.root.bind("<Down>", lambda e: self.change_direction("DOWN"))
        self.root.bind("<Left>", lambda e: self.change_direction("LEFT"))
        self.root.bind("<Right>", lambda e: self.change_direction("RIGHT"))
        self.root.bind("<w>", lambda e: self.change_direction("UP"))
        self.root.bind("<s>", lambda e: self.change_direction("DOWN"))
        self.root.bind("<a>", lambda e: self.change_direction("LEFT"))
        self.root.bind("<d>", lambda e: self.change_direction("RIGHT"))
        self.root.bind("<W>", lambda e: self.change_direction("UP"))
        self.root.bind("<S>", lambda e: self.change_direction("DOWN"))
        self.root.bind("<A>", lambda e: self.change_direction("LEFT"))
        self.root.bind("<D>", lambda e: self.change_direction("RIGHT"))
        self.root.bind("<r>", self.restart_game)
        self.root.bind("<R>", self.restart_game)
        self.root.bind("<Escape>", self.quit_game)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<p>", self.toggle_pause)
        self.root.bind("<P>", self.toggle_pause)

    def load_high_score(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        try:
            with open(self.score_file, "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass

    def draw_grid(self):
        # Draw subtle grid lines
        for col in range(self.GRID_COLS + 1):
            x = self.offset_x + col * GRID_SIZE
            self.canvas.create_line(x, self.offset_y, x, self.offset_y + self.HEIGHT,
                                   fill="#243342", width=1, tags="grid")
        for row in range(self.GRID_ROWS + 1):
            y = self.offset_y + row * GRID_SIZE
            self.canvas.create_line(self.offset_x, y, self.offset_x + self.WIDTH, y,
                                   fill="#243342", width=1, tags="grid")

    def show_start_screen(self):
        self.title_text = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 3,
            text="SNAKE GAME",
            font=("Arial", 72, "bold"),
            fill="#2ECC71",
            tags="start"
        )
        self.instruction_text = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2,
            text="Press SPACE to start\nUse WASD or Arrow Keys to move",
            font=("Arial", 28),
            fill="white",
            tags="start"
        )
        self.high_score_text = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 + 80,
            text="High Score: " + str(self.high_score),
            font=("Arial", 32, "bold"),
            fill="#F1C40F",
            tags="start"
        )

    def hide_start_screen(self):
        self.canvas.delete("start")

    def init_game(self):
        # Clear old snake and food
        for segment in self.snake:
            self.canvas.delete(segment)
        if self.food:
            self.canvas.delete(self.food)

        # Reset snake (start in middle)
        start_col = self.GRID_COLS // 2
        start_row = self.GRID_ROWS // 2
        self.snake = []

        # Create snake head (darker green with eyes)
        head_x = self.offset_x + start_col * GRID_SIZE
        head_y = self.offset_y + start_row * GRID_SIZE

        # Head body
        head = self.canvas.create_oval(
            head_x + 2, head_y + 2,
            head_x + GRID_SIZE - 2, head_y + GRID_SIZE - 2,
            fill="#27AE60", outline="#1E8449", width=2, tags="snake"
        )
        # Eyes
        eye1 = self.canvas.create_oval(
            head_x + 6, head_y + 6, head_x + 10, head_y + 10,
            fill="white", outline="black", tags="snake"
        )
        eye2 = self.canvas.create_oval(
            head_x + 15, head_y + 6, head_x + 19, head_y + 10,
            fill="white", outline="black", tags="snake"
        )
        pupil1 = self.canvas.create_oval(
            head_x + 7, head_y + 7, head_x + 9, head_y + 9,
            fill="black", tags="snake"
        )
        pupil2 = self.canvas.create_oval(
            head_x + 16, head_y + 7, head_x + 18, head_y + 9,
            fill="black", tags="snake"
        )
        # Tongue
        tongue = self.canvas.create_line(
            head_x + GRID_SIZE - 2, head_y + GRID_SIZE // 2,
            head_x + GRID_SIZE + 5, head_y + GRID_SIZE // 2 - 3,
            head_x + GRID_SIZE + 8, head_y + GRID_SIZE // 2,
            head_x + GRID_SIZE + 5, head_y + GRID_SIZE // 2 + 3,
            fill="#E74C3C", width=2, tags="snake"
        )

        self.snake.append([head, eye1, eye2, pupil1, pupil2, tongue, start_col, start_row])

        # Add initial body segments
        for i in range(1, 3):
            body_col = start_col - i
            body_row = start_row
            body_x = self.offset_x + body_col * GRID_SIZE
            body_y = self.offset_y + body_row * GRID_SIZE

            body = self.canvas.create_oval(
                body_x + 3, body_y + 3,
                body_x + GRID_SIZE - 3, body_y + GRID_SIZE - 3,
                fill="#2ECC71", outline="#27AE60", width=2, tags="snake"
            )
            # Body pattern (stripe)
            stripe = self.canvas.create_oval(
                body_x + 8, body_y + 8,
                body_x + GRID_SIZE - 8, body_y + GRID_SIZE - 8,
                fill="#27AE60", outline="", tags="snake"
            )

            self.snake.append([body, stripe, None, None, None, None, body_col, body_row])

        self.snake_direction = "RIGHT"
        self.next_direction = "RIGHT"

        # Spawn food
        self.spawn_food()

    def spawn_food(self):
        if self.food:
            self.canvas.delete(self.food)

        # Find valid position (not on snake)
        valid = False
        while not valid:
            self.food_x = random.randint(0, self.GRID_COLS - 1)
            self.food_y = random.randint(0, self.GRID_ROWS - 1)
            valid = True
            for segment in self.snake:
                if segment[6] == self.food_x and segment[7] == self.food_y:
                    valid = False
                    break

        food_px = self.offset_x + self.food_x * GRID_SIZE
        food_py = self.offset_y + self.food_y * GRID_SIZE

        # Draw apple-like food
        self.food = self.canvas.create_oval(
            food_px + 3, food_py + 3,
            food_px + GRID_SIZE - 3, food_py + GRID_SIZE - 3,
            fill="#E74C3C", outline="#C0392B", width=2, tags="food"
        )
        # Apple highlight
        self.food_highlight = self.canvas.create_oval(
            food_px + 7, food_py + 7,
            food_px + 13, food_py + 13,
            fill="#FF6B6B", outline="", tags="food"
        )
        # Apple stem
        self.food_stem = self.canvas.create_line(
            food_px + GRID_SIZE // 2, food_py + 3,
            food_px + GRID_SIZE // 2, food_py - 2,
            fill="#8B4513", width=2, tags="food"
        )
        # Apple leaf
        self.food_leaf = self.canvas.create_oval(
            food_px + GRID_SIZE // 2, food_py - 4,
            food_px + GRID_SIZE // 2 + 8, food_py + 2,
            fill="#2ECC71", outline="#27AE60", tags="food"
        )

    def toggle_game(self, event=None):
        if self.game_over:
            self.restart_game()
            return
        if not self.game_running:
            self.hide_start_screen()
            self.init_game()
            self.game_running = True
            self.game_loop()
        else:
            self.toggle_pause()

    def toggle_pause(self, event=None):
        if self.game_running and not self.game_over:
            self.paused = not self.paused
            if self.paused:
                self.pause_text = self.canvas.create_text(
                    self.screen_width // 2, self.screen_height // 2,
                    text="PAUSED",
                    font=("Arial", 48, "bold"),
                    fill="white",
                    tags="pause"
                )
            else:
                self.canvas.delete("pause")

    def change_direction(self, direction):
        if not self.game_running or self.game_over or self.paused:
            return

        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if direction != opposites.get(self.snake_direction, ""):
            self.next_direction = direction

    def update_snake(self):
        self.snake_direction = self.next_direction

        # Get head position
        head = self.snake[0]
        head_col = head[6]
        head_row = head[7]

        # Calculate new head position
        if self.snake_direction == "UP":
            new_row = head_row - 1
            new_col = head_col
        elif self.snake_direction == "DOWN":
            new_row = head_row + 1
            new_col = head_col
        elif self.snake_direction == "LEFT":
            new_col = head_col - 1
            new_row = head_row
        else:  # RIGHT
            new_col = head_col + 1
            new_row = head_row

        # Check wall collision
        if new_col < 0 or new_col >= self.GRID_COLS or new_row < 0 or new_row >= self.GRID_ROWS:
            self.game_over_screen()
            return

        # Check self collision
        for segment in self.snake:
            if segment[6] == new_col and segment[7] == new_row:
                self.game_over_screen()
                return

        # Check food collision
        ate_food = (new_col == self.food_x and new_row == self.food_y)

        if not ate_food:
            # Remove tail
            tail = self.snake.pop()
            for item in tail[:6]:
                if item:
                    self.canvas.delete(item)
        else:
            # Increase score
            self.score += 10
            self.score_label.config(text="Score: " + str(self.score))

            # Check level up (every 50 points)
            new_level = (self.score // 50) + 1
            if new_level > self.level:
                self.level = new_level
                self.level_label.config(text="Level: " + str(self.level))
                self.speed = max(MIN_SPEED, INITIAL_SPEED - (self.level - 1) * SPEED_INCREMENT)

            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.high_label.config(text="High: " + str(self.high_score))
                self.save_high_score()

            # Spawn new food
            self.spawn_food()

        # Move body segments (update positions visually)
        # First, convert old head to body
        old_head = self.snake[0]
        head_x = self.offset_x + old_head[6] * GRID_SIZE
        head_y = self.offset_y + old_head[7] * GRID_SIZE

        # Delete old head parts
        for item in old_head[:6]:
            if item:
                self.canvas.delete(item)

        # Create body segment at old head position
        body = self.canvas.create_oval(
            head_x + 3, head_y + 3,
            head_x + GRID_SIZE - 3, head_y + GRID_SIZE - 3,
            fill="#2ECC71", outline="#27AE60", width=2, tags="snake"
        )
        stripe = self.canvas.create_oval(
            head_x + 8, head_y + 8,
            head_x + GRID_SIZE - 8, head_y + GRID_SIZE - 8,
            fill="#27AE60", outline="", tags="snake"
        )
        old_head[:2] = [body, stripe]
        for i in range(2, 6):
            old_head[i] = None

        # Create new head
        new_x = self.offset_x + new_col * GRID_SIZE
        new_y = self.offset_y + new_row * GRID_SIZE

        new_head = [None] * 8
        new_head[6] = new_col
        new_head[7] = new_row

        # Head body
        new_head[0] = self.canvas.create_oval(
            new_x + 2, new_y + 2,
            new_x + GRID_SIZE - 2, new_y + GRID_SIZE - 2,
            fill="#27AE60", outline="#1E8449", width=2, tags="snake"
        )
        # Eyes (position based on direction)
        if self.snake_direction == "RIGHT":
            eye1_x, eye1_y = new_x + 16, new_y + 6
            eye2_x, eye2_y = new_x + 16, new_y + 15
        elif self.snake_direction == "LEFT":
            eye1_x, eye1_y = new_x + 6, new_y + 6
            eye2_x, eye2_y = new_x + 6, new_y + 15
        elif self.snake_direction == "UP":
            eye1_x, eye1_y = new_x + 6, new_y + 6
            eye2_x, eye2_y = new_x + 15, new_y + 6
        else:  # DOWN
            eye1_x, eye1_y = new_x + 6, new_y + 16
            eye2_x, eye2_y = new_x + 15, new_y + 16

        new_head[1] = self.canvas.create_oval(
            eye1_x, eye1_y, eye1_x + 4, eye1_y + 4,
            fill="white", outline="black", tags="snake"
        )
        new_head[2] = self.canvas.create_oval(
            eye2_x, eye2_y, eye2_x + 4, eye2_y + 4,
            fill="white", outline="black", tags="snake"
        )
        new_head[3] = self.canvas.create_oval(
            eye1_x + 1, eye1_y + 1, eye1_x + 3, eye1_y + 3,
            fill="black", tags="snake"
        )
        new_head[4] = self.canvas.create_oval(
            eye2_x + 1, eye2_y + 1, eye2_x + 3, eye2_y + 3,
            fill="black", tags="snake"
        )

        # Tongue (based on direction)
        if self.snake_direction == "RIGHT":
            tongue_pts = [new_x + GRID_SIZE - 2, new_y + GRID_SIZE // 2,
                         new_x + GRID_SIZE + 6, new_y + GRID_SIZE // 2 - 3,
                         new_x + GRID_SIZE + 10, new_y + GRID_SIZE // 2,
                         new_x + GRID_SIZE + 6, new_y + GRID_SIZE // 2 + 3]
        elif self.snake_direction == "LEFT":
            tongue_pts = [new_x + 2, new_y + GRID_SIZE // 2,
                         new_x - 6, new_y + GRID_SIZE // 2 - 3,
                         new_x - 10, new_y + GRID_SIZE // 2,
                         new_x - 6, new_y + GRID_SIZE // 2 + 3]
        elif self.snake_direction == "UP":
            tongue_pts = [new_x + GRID_SIZE // 2, new_y + 2,
                         new_x + GRID_SIZE // 2 - 3, new_y - 6,
                         new_x + GRID_SIZE // 2, new_y - 10,
                         new_x + GRID_SIZE // 2 + 3, new_y - 6]
        else:  # DOWN
            tongue_pts = [new_x + GRID_SIZE // 2, new_y + GRID_SIZE - 2,
                         new_x + GRID_SIZE // 2 - 3, new_y + GRID_SIZE + 6,
                         new_x + GRID_SIZE // 2, new_y + GRID_SIZE + 10,
                         new_x + GRID_SIZE // 2 + 3, new_y + GRID_SIZE + 6]

        new_head[5] = self.canvas.create_line(
            *tongue_pts, fill="#E74C3C", width=2, tags="snake"
        )

        self.snake.insert(0, new_head)

    def game_over_screen(self):
        self.game_over = True
        self.game_running = False

        self.save_high_score()

        # Dark overlay
        self.canvas.create_rectangle(
            self.offset_x, self.offset_y,
            self.offset_x + self.WIDTH, self.offset_y + self.HEIGHT,
            fill="black", stipple="gray50", tags="gameover"
        )

        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 3,
            text="GAME OVER",
            font=("Arial", 72, "bold"),
            fill="#E74C3C",
            tags="gameover"
        )

        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 - 20,
            text="Score: " + str(self.score),
            font=("Arial", 36),
            fill="white",
            tags="gameover"
        )

        new_record = self.score >= self.high_score and self.score > 0
        record_text = "NEW RECORD!" if new_record else "High Score: " + str(self.high_score)
        record_color = "#F1C40F" if new_record else "#F1C40F"

        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 + 30,
            text=record_text,
            font=("Arial", 32, "bold"),
            fill=record_color,
            tags="gameover"
        )

        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 + 100,
            text="Press R to restart\nPress ESC to quit",
            font=("Arial", 24),
            fill="white",
            tags="gameover"
        )

    def restart_game(self, event=None):
        if not self.game_over and self.game_running:
            return

        # Clear everything
        self.canvas.delete("snake")
        self.canvas.delete("food")
        self.canvas.delete("gameover")
        self.canvas.delete("pause")

        # Reset state
        self.score = 0
        self.level = 1
        self.speed = INITIAL_SPEED
        self.score_label.config(text="Score: 0")
        self.high_label.config(text="High: " + str(self.high_score))
        self.level_label.config(text="Level: 1")
        self.game_running = False
        self.game_over = False
        self.paused = False
        self.snake = []
        self.snake_direction = "RIGHT"
        self.next_direction = "RIGHT"

        # Show start screen
        self.show_start_screen()

    def toggle_fullscreen(self, event=None):
        is_full = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_full)
        return "break"

    def quit_game(self, event=None):
        self.save_high_score()
        self.root.destroy()

    def game_loop(self):
        if self.game_running and not self.game_over and not self.paused:
            self.update_snake()

        if self.game_running and not self.game_over:
            self.root.after(self.speed, self.game_loop)

def main():
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()