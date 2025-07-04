import numpy as np
import bentoml

# The @bentoml.service decorator is the modern way to define a service.
@bentoml.service
class MySimpleService:
    # The @bentoml.api decorator is no longer needed when using native type hints.
    # We now use standard numpy type hints directly in the function signature.
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """
        This function accepts a numpy array and returns a numpy array.
        """
        # The logic is simple: multiply the input by 2
        return input_data * 2