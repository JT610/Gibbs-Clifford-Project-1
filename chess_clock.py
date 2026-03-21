from contextlib import contextmanager
import time


@contextmanager
def timer():
    # setup, equivalent to __enter__
    start = time.time()
    try:
        yield start  # user's 'with' block runs here
    finally:
        # teardown, equivalent to __exit__
        elapsed = time.time() - start
        print(f"Took {elapsed:.4f} sec")


class chess_clock:
    def __init__(self):
        self.white_time = 0
        self.black_time = 0
        self.white_timer_running = False
        self.black_timer_running = False
        self.white_start = None
        self.black_start = None
    
    def start_timer(self, white_move):
        # start the timer for the given player
        if white_move:
            self.white_timer_running = True
            self.white_start = time.time()
        else:
            self.black_timer_running = True
            self.black_start = time.time()

    def stop_timer(self, white_move):
         # stop the timer for the given player
        if white_move:
            if self.white_timer_running:
                elapsed = time.time() - self.white_start
                self.white_time -= elapsed
                self.white_timer_running = False
        else:
            if self.black_timer_running:
                elapsed = time.time() - self.black_start
                self.black_time -= elapsed
                self.black_timer_running = False

    def set_active_player(self, white_move):
        #### Set the active player for the clock, starting their timer and stopping the other player's timer

        self.start_timer(white_move)
        self.stop_timer(not white_move)

    def setup_clock(self, minutes):
        # set up the clock with the given time for each player
        self.white_time = minutes * 60
        self.black_time = minutes * 60

    def check_time(self):
        # check if either player has run out of time
        white_remaining = self.white_time
        black_remaining = self.black_time

        if self.white_timer_running:
            white_remaining = (self.white_time - (time.time() - self.white_start))
        if self.black_timer_running:
            black_remaining = (self.black_time - (time.time() - self.black_start))
        return white_remaining <= 0 or black_remaining <= 0

    def __repr__(self):
        # return remaining time for each player
        white_secs = max(0, self.white_time)
        black_secs = max(0, self.black_time)
        white_mins = int(white_secs // 60)
        white_sec = white_secs % 60
        black_mins = int(black_secs // 60)
        black_sec = black_secs % 60
        return f"Time remaining:\n White: {white_mins}.{white_sec:05.2f}, Black: {black_mins}.{black_sec:05.2f}"
