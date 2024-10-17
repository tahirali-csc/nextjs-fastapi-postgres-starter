import threading

sample_responses = [
    "Humans have this incredible ability to connect deeply with each other through empathy, "
    "understanding each other's joys and pains as if they were their own. "
    "Curiosity drives human progress. It's a relentless quest for knowledge and understanding that has led "
    "to some of the most profound discoveries",
    "Conflict is a part of human nature too. It stems from differing perspectives and can lead to "
    "growth and understanding when addressed constructively",
    "Compassion leads humans to act selflessly and help others, often putting others' needs before their own",
    "Creativity is a hallmark of human nature. It's the spark that leads to art, music, innovation, "
    "and all forms of expression that enrich our lives"
]


class _ReplyCounter:
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


reply_counter = _ReplyCounter(1, len(sample_responses))


def get_response():
    """
     We could have used random() here, but we want unique replies, so
     using thread safe counter.
    """
    reply = sample_responses[reply_counter.get_value() - 1]
    reply_counter.increment()
    return reply
