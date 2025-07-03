import bentoml
from bentoml.io import NumpyNdarray

# This is a dummy model for demonstration purposes.
# In a real project, you would load your trained model here.
class MyModel:
    def predict(self, input_data):
        return input_data * 2

# Save the model with BentoML's model store
my_model = MyModel()
bentoml.picklable_model.save_model("my_simple_model", my_model)


# Create a "runner" for our model
simple_runner = bentoml.picklable_model.get("my_simple_model:latest").to_runner()

# Create a BentoML service
svc = bentoml.Service("simple_prediction_service", runners=[simple_runner])

# Define an API endpoint on the service
@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def predict(input_data: NumpyNdarray) -> NumpyNdarray:
    # This now runs the prediction in a separate, optimized process
    result = simple_runner.predict.run(input_data)
    return result