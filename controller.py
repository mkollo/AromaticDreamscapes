class ValveController:
    def __init__(self, model):
        self.model = model

    def get_sampling_rate(self):
        return self.model.sample_rate

    def play_valve_sequence(self, odour_valves, duty_cycles, label):
        traces = self.model.play_valve_sequence(odour_valves, duty_cycles, label)
        return traces