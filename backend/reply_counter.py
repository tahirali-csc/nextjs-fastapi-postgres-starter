import threading


class ReplyCounter:
    def __init__(self, initial=0, max=0):
        self.value = initial
        self.max = max
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            if self.value == self.max:
                self.value = 1
            else:
                self.value += 1

    def get_value(self):
        with self.lock:
            return self.value