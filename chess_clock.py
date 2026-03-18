class chess_clock:
    def __init__(self, time):
        self.white_time = time
        self.black_time = time
        self.white_timer_running = False
        self.black_timer_running = False
    
    def start_timer(self, white_move):
        # TODO start the timer for the given player
        pass

    def stop_timer(self, white_move):
        # TODO stop the timer for the given player
        pass


    def set_active_player(self, white_move):
        #### Set the active player for the clock, starting their timer and stopping the other player's timer

        self.start_timer(white_move)
        self.stop_timer(not white_move)

    def setup_clock(self, time):
        # TODO set up the clock with the given time for each player
        pass

    def check_time(self):
        # TODO check the time for each player and return if either player's time has run out
        pass

    def __repr__(self):
        return f"Time remaining:\n White: {self.white_time}, Black={self.black_time}"

        
