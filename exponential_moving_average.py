class ExponentialMovingAverage:
    """
    A class to calculate the Exponential Moving Average (EMA) of a series of values.

    EMA gives more weight to recent values using a smoothing factor (alpha),
    which controls how quickly the influence of older values decays.

    Attributes:
        alpha (float): The smoothing factor, between 0 and 1. Higher values give more weight to recent values.
        ema (float): The current EMA value, initialized with a required starting value.
    """

    def __init__(self, alpha: float, initial_value: float):
        """
        Initialize the EMA class with a smoothing factor and initial value.
        :param alpha: float, smoothing factor between 0 and 1.
        :param initial_value: float, the initial value for the EMA.
        """
        if not (0 < alpha <= 1):
            raise ValueError("Alpha must be between 0 and 1.")
        self.alpha = alpha
        self.ema = initial_value

    def update(self, value: float):
        """
        Update the EMA with a new value.
        :param value: float, new value to include in the EMA calculation.
        """
        self.ema = self.alpha * value + (1 - self.alpha) * self.ema

    def average(self) -> float:
        """
        Return the current EMA value.
        :return: float, the current EMA.
        """
        return self.ema
