from scipy import constants

class Range:
    def __init__(self, a, b):
        self.min = min([a, b])
        self.max = max([a, b])
        assert(a < b)

    @property
    def low(self):
        return self.min

    @property
    def high(self):
        return self.max

    def mean(self):
        return (self.min + self.max)/2

    def __repr__(self):
        return "[{}, {}]".format(self.min, self.max)

    def is_in_range(self, value):
        return value <= self.max and value >= self.min

    def mult(self, a):
        return Range(self.min*a, self.max*a)



class Temperature:
    def __init__(self, value, unit="celsius"):
        k = value
        if unit.lower() in ["celsius", "c"]:
            k = self.celsius_to_kelvin(value)
        elif unit.lower() in ["fahrenheit", "f"]:
            k = self.fahrenheit_to_kelvin(value)
        elif unit.lower() in ["kelvin", "k"]:
            pass
        else:
            raise ValueError("unknown unit %s", str(unit))
        self._kelvin = k

    def __repr__(self):
        return str(self.celsius)

    def __lt__(self, b):
        return self.kelvin < b.kelvin

    def __gt__(self, b):
        return self.kelvin > b.kelvin

    def __eq__(self, b):
        return self.kelvin == b.kelvin

    def __ge__(self, b):
        return self.kelvin >= b.kelvin

    def __le__(self, b):
        return self.kelvin <= b.kelvin

    @staticmethod
    def kelvin_to_celsius(cls, value):
        return value - 273.15

    @staticmethod
    def kelvin_to_fahrenheit(cls, value):
        return 1.8*self.kelvin_to_celsius(value) + 32

    @staticmethod
    def celsius_to_kelvin(cls, value):
        return value + 273.15

    @staticmethod
    def fahrenheit_to_kelvin(cls, value):
        return (value - 32)/1.8

    @property
    def k(self):
        return self._kelvin

    @property
    def kelvin(self):
        return self._kelvin

    @property
    def c(self):
        return self.celsius

    @property
    def celsius(self):
        return self.kelvin_to_celsius(self.kelvin)

    @property
    def f(self):
        return self.fahrenheit

    @property
    def fahrenheit(self):
        return self.kelvin_to_fahrenheit(self.kelvin)

