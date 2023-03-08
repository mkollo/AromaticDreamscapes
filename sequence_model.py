class SequenceModel:
    def __init__(self):
        self.current_sequence = {'valves': [], 'duty_cycles': [], 'label': 'RESET to default'}
        self.next_sequence = [self.current_sequence]

    def pop_next_sequence(self):
        if len(self.next_sequence) == 0:
            self.current_sequence = self.next_sequence.pop(0)
            return self.current_sequence
        else:
            return self.current_sequence