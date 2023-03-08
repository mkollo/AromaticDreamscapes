class SequenceModel:
    def __init__(self):
        self.current_sequence = {'valves': [], 'duty_cycles': [], 'label': ''}
        self.next_sequence = [self.current_sequence]