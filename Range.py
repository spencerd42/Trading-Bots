from collections import deque

# Class to store the range of prices over a specified interval
class Range:
    def __init__(self, minutes, step):
        self.minutes = minutes
        self.interval = step
        self.capacity = int(minutes/step)
        self.size = 0
        self.highs = deque([])
        self.lows = deque([])
        self.max = 0
        self.min = 0

    # add the next element to the range and recalculate max and min if necessary
    def add(self, high, low):
        if self.size == 0:
            self.min = low
            self.max = high

        self.highs.append(high)
        self.lows.append(low)
        if self.size < self.capacity:
            self.max = max(self.max, high)
            self.min = min(self.min, low)
        else:
            if self.max == self.highs.popleft():
                self.get_max()
            if self.min == self.lows.popleft():
                self.get_min()
        self.size += 1

    def get_max(self):
        self.max = self.highs[0]
        for high in self.highs:
            self.max = max(self.max, high)

    def get_min(self):
        self.min = self.lows[0]
        for low in self.lows:
            self.min = min(self.min, low)