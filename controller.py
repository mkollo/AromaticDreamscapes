class OdourSeqController:
    def __init__(self, valve_model, sequence_model):
        self.valve_model = valve_model
        self.sequence_model = sequence_model

    def get_sampling_rate(self):
        return self.valve_model.sample_rate

    def play_valve_sequence(self, odour_valves, duty_cycles, label):
        traces = self.valve_model.play_valve_sequence(odour_valves, duty_cycles, label)
        return traces