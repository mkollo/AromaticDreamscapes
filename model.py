from matplotlib import pyplot as plt
import nidaqmx
import numpy as np

class ValveModel:
    def __init__(self):

        self.acquisition_length = 5000
        self.preacquistion_length = 500
        self.postacquistion_length = 500
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
        self.generate_valve_pattern([2,3], [0, 0, 0, 0])

    def __del__(self):
        self.valves.close()
        self.ai.close()
        self.ttl.close()

    def init_clock_and_trigger(self, task):
        task.timing.cfg_samp_clk_timing(1000, source="OnboardClock", samps_per_chan=self.acquisition_length, sample_mode=nidaqmx.constants.AcquisitionType.FINITE) 
        # task.triggers.start_trigger.cfg_dig_edge_start_trig("/cDAQ1/PFI0")

    def determine_clean_air_valve(self, odour_valve):
        if odour_valve in [2, 4, 6]:
            return 0
        elif odour_valve in [3, 5, 7]:
            return 1
        elif odour_valve in [10, 12, 14]:
            return 8
        elif odour_valve in [11, 13, 15]:
            return 9

    def generate_valve_pattern(self, odour_valves, duty_cycles):
        valves = np.vstack([np.ones((16, self.acquisition_length)),np.zeros((17, self.acquisition_length))])
        clean_air_valves = [self.determine_clean_air_valve(odour_valve) for odour_valve in odour_valves]
        valves[self.all_clean_air_valves, :self.preacquistion_length] = 0
        plt.imshow(valves, cmap='gray', aspect='auto')
        plt.show()

    def set_default_valve_states(self):
        front_valve_states = np.ones((16, self.acquisition_length))
        back_valve_states = np.zeros((16, self.acquisition_length))
        for i in [0, 1, 8, 9]:
            front_valve_states[i] = 0               
        front_valve_states = front_valve_states.astype(bool)
        back_valve_states = back_valve_states.astype(bool)
        return self.set_valve_states(front_valve_states, back_valve_states)

    def set_valve_states(self, front_valve_states, back_valve_states):
        self.valves.write(np.vstack([front_valve_states, back_valve_states]))
        self.valves.start()
        self.valves.wait_until_done(timeout=20)
        return self.ai.read(number_of_samples_per_channel=self.acquisition_length)