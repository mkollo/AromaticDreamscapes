class FlowDataController:

    def __init__(self, model):
        self.model = model

    def get_flow(self):
        return self.model.read_flow()

    def get_flow_history(self, num_samples):
        return self.model.get_flow_history(num_samples)
