class ValveController:
    def __init__(self, model):
        self.model = model

    def set_valve_states(self, front_valve_states, back_valve_states):
        trace = self.model.set_valve_states(front_valve_states, back_valve_states)
        return trace

    def set_default_valve_states(self):
        trace = self.model.set_default_valve_states()
        return trace

    def reset_valve_states(self):
        trace = self.model.play_sequence()
        return trace

    def get_sampling_rate(self):
        return self.model.sample_rate