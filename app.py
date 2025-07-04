import numpy as np
import bentoml
from bentoml.io import NumpyNdarray

# Define a simple "runnable" class that contains our model logic.
# This is the modern way to define the model's computation.
@bentoml.service
class MySimpleService:
    @bentoml.api
    def predict(self, input_data: NumpyNdarray) -> NumpyNdarray:
        # The logic is simple: multiply the input by 2
        return input_data * 2