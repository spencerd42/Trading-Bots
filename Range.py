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
        self.max = float('-inf')
        self.min = float('inf')
        self.sum = 0
        self.num_increases = 0

    # add the next element to the range and recalculate max and min if necessary
    def add(self, high, low):
        if self.size == 0:
            self.min = low
            self.max = high
        elif (low + high) / 2 > (self.lows[-1] + self.highs[-1]) / 2:
            self.num_increases += 1

        self.highs.append(high)
        self.lows.append(low)

        self.sum += high + low

        if self.size < self.capacity:
            self.max = max(self.max, high)
            self.min = min(self.min, low)
            self.size += 1
        else:
            popped_high = self.highs.popleft()
            popped_low = self.lows.popleft()
            if (popped_low + popped_high) / 2 < (self.lows[0] + self.highs[0]) / 2:
                self.num_increases -= 1
            self.sum -= (popped_high + popped_low)
            if self.max == popped_high:
                # don't need to search for new max if new element is greater than old max
                if high > self.max:
                    self.max = high
                else:
                    self.get_max()
            if self.min == popped_low:
                if low < self.min:
                    self.min = low
                else:
                    self.get_min()

    def get_max(self):
        self.max = self.highs[0]
        for high in self.highs:
            self.max = max(self.max, high)

    def get_min(self):
        self.min = self.lows[0]
        for low in self.lows:
            self.min = min(self.min, low)

    def get_avg(self):
        return self.sum / (self.capacity * 2)

    def get_percent_increases(self):
        return self.num_increases / (self.capacity - 1)