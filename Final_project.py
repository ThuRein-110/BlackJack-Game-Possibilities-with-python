import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# ------------------------
# Sound (Strongest working version)
# ------------------------
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    PYGAME_OK = True
except Exception as e:
    print("Sound init failed:", e)
    PYGAME_OK = False

def play_sound(path):
    """Plays a sound safely."""
    if PYGAME_OK and os.path.exists(path):
        try:
            snd = pygame.mixer.Sound(path)
            snd.play()
        except Exception as e:
            print("Sound error:", e)


# ------------------------
# Card utilities
# ------------------------
RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
SUITS = ["H","D","C","S"]
RANK_VALUE = {**{str(i): i for i in range(2, 11)}, **{"J":10,"Q":10,"K":10,"A":11}}

def make_full_deck():
    deck = []
    for s in SUITS:
        for r in RANKS:
            filename = f"{r}{s}.jpg"
            deck.append((r, s, RANK_VALUE[r], filename))
    random.shuffle(deck)
    return deck

def hand_score(hand):
    total = sum(c[2] for c in hand)
    aces = sum(1 for c in hand if c[0] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


# ------------------------
# GUI Class
# ------------------------
class BlackjackGUI:
    CARD_SIZE = (65, 95)
    SPACING = 85

    def __init__(self, root):
        self.root = root
        root.title("🎴 Blackjack Player vs AI 🎴")
        root.geometry("900x650")
        root.resizable(False, False)
        root.configure(bg="#1b1b1b")

        self.images_cache = {}
        self.deck_cards = make_full_deck()
        self.player_hand = []
        self.ai_hand = []
        self.game_over = False

        # Title
        self.title_label = tk.Label(root, text="Blackjack Player vs AI", 
                                    font=("Arial", 24, "bold"), fg="white", bg="#1b1b1b")
        self.title_label.pack(pady=10)

        # Score
        self.score_label = tk.Label(root, text="", font=("Arial", 14),
                                    fg="#ffffff", bg="#1b1b1b")
        self.score_label.pack()

        # Canvas
        self.canvas = tk.Canvas(root, width=900, height=500, bg="#000000", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#1b1b1b")
        btn_frame.pack()

        self.hit_btn = tk.Button(btn_frame, text="Hit", width=12, font=("Arial", 12), command=self.on_hit)
        self.stand_btn = tk.Button(btn_frame, text="Stand", width=12, font=("Arial", 12), command=self.on_stand)
        self.restart_btn = tk.Button(btn_frame, text="Restart", width=12, font=("Arial", 12), command=self.on_restart)

        self.hit_btn.grid(row=0, column=0, padx=10)
        self.stand_btn.grid(row=0, column=1, padx=10)
        self.restart_btn.grid(row=0, column=2, padx=10)

        # Load images
        self.back_img = self.load_image("back.jpg", size=self.CARD_SIZE)
        self.bg_img = self.load_image("bg.jpg", size=(900, 500))

        self.start_game()

    # Load card images
    def load_image(self, fname, size=None):
        if fname in self.images_cache:
            return self.images_cache[fname]

        if size is None:
            size = self.CARD_SIZE

        path = os.path.join("images", fname)
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
        except:
            img = Image.new("RGB", size, (80, 80, 80))

        pimg = ImageTk.PhotoImage(img)
        self.images_cache[fname] = pimg
        return pimg


    # -------------------
    # Game Setup
    # -------------------
    def start_game(self):
        self.deck_cards = make_full_deck()
        self.player_hand = [self.deck_cards.pop(), self.deck_cards.pop()]
        self.ai_hand = [self.deck_cards.pop(), self.deck_cards.pop()]
        self.game_over = False

        self.draw_board()
        self.update_scoreboard()

        # AUTO BLACKJACK CHECK (Ace + 10-value)
        self.check_blackjack_start()

    def check_blackjack_start(self):
        p = hand_score(self.player_hand)
        a = hand_score(self.ai_hand)

        if p == 21 and a == 21:
            self.end_game("Both have BLACKJACK — Draw!", "sounds/lose.wav")
        elif p == 21:
            self.end_game("You got BLACKJACK!\nYOU WIN!", "sounds/win.wav")
        elif a == 21:
            self.end_game("AI got BLACKJACK!\nAI WINS!", "sounds/lose.wav")


    # -------------------
    # Drawing
    # -------------------
    def draw_board(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        # Labels ABOVE cards
        self.canvas.create_text(450, 30, text="AI Hand", fill="white", font=("Arial", 16, "bold"))
        self.canvas.create_text(450, 280, text="Player Hand", fill="white", font=("Arial", 16, "bold"))

        # Deck
        deck_x, deck_y = 90, 220
        self.canvas.create_image(deck_x, deck_y, image=self.back_img, anchor="center")
        self.canvas.create_text(deck_x, deck_y + 70, text=f"Deck: {len(self.deck_cards)}",
                                fill="white", font=("Arial", 11))

        self.draw_cards()

    def card_positions(self, center_x, count):
        total = self.SPACING * (count - 1)
        start = center_x - total // 2
        return [start + i * self.SPACING for i in range(count)]

    def draw_cards(self):
        self.canvas.delete("card")

        # AI cards
        ai_y = 60
        pos_ai = self.card_positions(450, len(self.ai_hand))
        for i, c in enumerate(self.ai_hand):
            img = self.back_img if (i == 1 and not self.game_over) else self.load_image(c[3])
            self.canvas.create_image(pos_ai[i], ai_y, image=img, anchor="n", tags="card")

        # Player cards
        pl_y = 310
        pos_pl = self.card_positions(450, len(self.player_hand))
        for i, c in enumerate(self.player_hand):
            img = self.load_image(c[3])
            self.canvas.create_image(pos_pl[i], pl_y, image=img, anchor="n", tags="card")


    def update_scoreboard(self):
        p = hand_score(self.player_hand)
        a_show = self.ai_hand[0][2]
        self.score_label.config(text=f"Player: {p}   |   AI Showing: {a_show}   |   Deck: {len(self.deck_cards)}")


    # -------------------
    # Player Hit
    # -------------------
    def on_hit(self):
        if self.game_over:
            return

        if len(self.player_hand) >= 5:
            messagebox.showinfo("Limit", "You already have 5 cards!")
            return

        play_sound("sounds/hit.wav")
        self.player_hand.append(self.deck_cards.pop())

        self.draw_board()
        self.update_scoreboard()

        score = hand_score(self.player_hand)

        # Auto-win with 21 (includes Ace + face card)
        if score == 21:
            self.end_game("You hit EXACT 21!\nYOU WIN!", "sounds/win.wav")
            return

        # Five-card Charlie
        if len(self.player_hand) == 5 and score <= 21:
            self.end_game("Five-Card Charlie!\nYOU WIN!", "sounds/win.wav")
            return

        # Bust
        if score > 21:
            self.end_game("You busted!\nAI Wins!", "sounds/lose.wav")


    # -------------------
    # Stand = AI Turn
    # -------------------
    def on_stand(self):
        if self.game_over:
            return

        ai_score = hand_score(self.ai_hand)

        # AI auto-win if 21
        if ai_score == 21:
            self.end_game("AI has 21!\nAI Wins!", "sounds/lose.wav")
            return

        # AI logic
        while ai_score < 14 and len(self.ai_hand) < 5 and self.deck_cards:
            self.ai_hand.append(self.deck_cards.pop())
            ai_score = hand_score(self.ai_hand)

        self.draw_board()
        self.final_result()


    # -------------------
    # Final Results
    # -------------------
    def final_result(self):
        p = hand_score(self.player_hand)
        a = hand_score(self.ai_hand)

        # 5 card charlie
        if len(self.ai_hand) == 5 and a <= 21:
            self.end_game("AI Five-Card Charlie!\nYou lose!", "sounds/lose.wav")
            return

        if a == 21:
            self.end_game("AI got 21!\nYou lose!", "sounds/lose.wav")
            return

        # Compare
        if a > 21:
            self.end_game("AI busted!\nYou WIN!", "sounds/win.wav")
        elif p > a:
            self.end_game("You WIN!", "sounds/win.wav")
        elif a > p:
            self.end_game("AI wins!", "sounds/lose.wav")
        else:
            self.end_game("Draw!", "sounds/lose.wav")


    # -------------------
    # Helper: end game
    # -------------------
    def end_game(self, msg, sound=None):
        self.game_over = True
        self.draw_board()
        if sound:
            play_sound(sound)
        messagebox.showinfo("Game Over", msg)


    def on_restart(self):
        self.start_game()


# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    if not os.path.isdir("images"):
        print("⚠ Create 'images/' folder with cards, back.jpg, and bg.jpg")
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()
