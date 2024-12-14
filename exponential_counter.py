class ExponentialCounter:
    def __init__(self, decay: float, initial_value: float):
        """
        Initialize the ExponentialCounter.

        Args:
            decay (float): Decay factor between updates. Must be greater than 0.
                - A higher decay value gives more weight to recent updates, making the counter adapt faster to new changes.
                - A lower decay value gives more weight to the historical values, making the counter change more gradually.
            initial_value (float): The initial value of the counter.
        """
        if decay <= 0:
            raise ValueError("Decay factor must be greater than 0.")

        self.decay = decay
        self.value = initial_value

    def update(self, new_value: float):
        """
        Update the counter with a new value using the EMA-like weight.

        Args:
            new_value (float): The new value to incorporate into the counter.
        """
        weight = 1 / self.decay
        self.value = (weight * self.value + new_value) / (weight + 1)

    def get_value(self) -> float:
        """
        Retrieve the current value of the counter.

        Returns:
            float: The current value.
        """
        return self.value
