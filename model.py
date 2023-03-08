from matplotlib import pyplot as plt
import nidaqmx
import numpy as np


class ValveModel:
    def __init__(self, sample_rate=10000, acquisition_time=5, pre_sequence_time=0, post_sequence_time=0.5, pulse_time=1):
        self.sample_rate = sample_rate
        self.acquisition_samples = int(acquisition_time * self.sample_rate)
        self.pre_sequence_samples = int(pre_sequence_time * self.sample_rate)
        self.post_sequence_samles = int(post_sequence_time * self.sample_rate)
        self.pulse_samples = int(pulse_time * self.sample_rate)
        self.cycle_samples = int(0.004 * self.sample_rate)
        self.ttl_bit_samples = int(0.004 * self.sample_rate)
        self.all_clean_air_valves = [0, 1, 8, 9]
        self.valves = nidaqmx.Task()
        self.ai = nidaqmx.Task()
        self.ttl = nidaqmx.Task()

        self.valves.do_channels.add_do_chan("Front_valves/port0/line0:15, Back_valves/port0/line0:7, Back_valves/port0/line16:23", line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE)
        self.ai.ai_channels.add_ai_voltage_chan("AI/ai0, AI/ai1")
        self.ttl.do_channels.add_do_chan("Front_valves/port0/line16")

        self.init_clock_and_trigger(self.valves)
        self.init_clock_and_trigger(self.ai)
        self.init_clock_and_trigger(self.ttl)
        self.generate_valve_pattern([3, 4, 13, 16], [1, 0.5, 0.1, 0.3], "F1-3,4,13,16")
        # self.generate_valve_pattern([], [])

    def __del__(self):
        self.valves.close()
        self.ai.close()
        self.ttl.close()

    def init_clock_and_trigger(self, task):
        task.timing.cfg_samp_clk_timing(self.sample_rate, source="OnboardClock", samps_per_chan=self.acquisition_samples, sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
        # task.triggers.start_trigger.cfg_dig_edge_start_trig("/cDAQ1/PFI0")

    def determine_clean_air_valve(self, odour_valve):
        return {k: (k > 8) * k // 8 * 8 + 1 - k % 2 for k in list(range(2, 8)) + list(range(10, 16))}.get(odour_valve)

    def generate_valve_pattern(self, odour_valves, duty_cycles, label=""):
        valves = np.vstack([np.ones((16, self.acquisition_samples)), np.zeros((17, self.acquisition_samples))])
        clean_air_valves = [self.determine_clean_air_valve(odour_valve - 1) for odour_valve in odour_valves]
        valves[self.all_clean_air_valves, :] = 0
        for k in range(len(odour_valves)):
            on_samples = int(self.cycle_samples * duty_cycles[k])
            pulse_pattern = np.concatenate(np.arange(0, self.pulse_samples, self.cycle_samples).reshape(-1, 1) + np.arange(on_samples))
            valves[odour_valves[k] - 1, pulse_pattern + self.pre_sequence_samples + self.pulse_samples * k] = 0
            valves[odour_valves[k] - 1 + 16, self.pre_sequence_samples + self.pulse_samples * k: self.pre_sequence_samples + self.pulse_samples * (k + 1)] = 1
            print(valves.shape)
            valves[clean_air_valves[k], pulse_pattern + self.pre_sequence_samples + self.pulse_samples * k] = 1
        # creating a binary code for the label
        bytes_array = np.frombuffer(label.encode(), dtype=np.uint8)
        binary_codes = np.unpackbits(bytes_array)
        binary_codes = binary_codes[:len(label) * 7].reshape(-1, 7).reshape(-1)
        true_indices = np.where(binary_codes)[0] + 2
        true_indices = np.hstack([0, true_indices])
        ttl_pattern = (true_indices[:, None] * self.ttl_bit_samples + np.arange(self.ttl_bit_samples)).ravel() + self.pre_sequence_samples
        valves[32, ttl_pattern] = 1
        plt.imshow(valves, cmap='gray', aspect='auto', interpolation='none')
        plt.show()

    def set_valve_states(self, front_valve_states, back_valve_states):
        self.valves.write(np.vstack([front_valve_states, back_valve_states]))
        self.valves.start()
        self.valves.wait_until_done(timeout=20)
        return self.ai.read(number_of_samples_per_channel=self.acquisition_length * self.sample_rate)
