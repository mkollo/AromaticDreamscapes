import nidaqmx
import numpy as np

class ValveModel:
    def __init__(self):
        self.counter_task = nidaqmx.Task()
        self.back_valves = nidaqmx.Task()
        self.front_valves = nidaqmx.Task()
        self.ai = nidaqmx.Task()
        self.ttl = nidaqmx.Task()

        self.front_valves.do_channels.add_do_chan("Front_valves/port0/line0:15")
        self.back_valves.do_channels.add_do_chan("Back_valves/port0/line0:23")
        self.ai.ai_channels.add_ai_voltage_chan("AI/ai0")
        self.ttl.do_channels.add_do_chan("Front_valves/port0/line16")
        
        self.configure_timing()
        self.set_default_valve_states()

    def __del__(self):
        self.counter_task.close()
        self.ttl.close()

    def configure_timing(self):
        clock_rate = 10000.0
        self.counter_task.co_channels.add_co_pulse_chan_freq("/cDAQ1/Ctr0", freq=clock_rate, duty_cycle=0.5)
        self.counter_task.timing.cfg_samp_clk_timing(source= rate=clock_rate, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=int(clock_rate*3.5))
        self.counter_task.export_signals.export_signal(nidaqmx.constants.Signal.SAMPLE_CLOCK, "/cDAQ1/PFI1")
        self.counter_task.export_signals.export_signal(nidaqmx.constants.Signal.SAMPLE_CLOCK, "/cDAQ1/PFI1")
        self.counter_task.start()
        
        # sample_clock_source0 = "/cDAQ1/PFI0"
        # sample_clock_source1 = "/cDAQ1/PFI1"
        start_trigger_source = "/cDAQ1/ai/StartTrigger"

        self.ai.timing.cfg_samp_clk_timing(clock_rate, source=sample_clock_source0)
        self.front_valves.timing.cfg_samp_clk_timing(clock_rate, source=sample_clock_source0)
        self.front_valves.triggers.start_trigger.cfg_dig_edge_start_trig(start_trigger_source)
        self.back_valves.timing.cfg_samp_clk_timing(clock_rate, source=sample_clock_source1)
        self.back_valves.triggers.start_trigger.cfg_dig_edge_start_trig(start_trigger_source)

    def set_default_valve_states(self):
        self.set_valve_states([1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], [0] * 16)        

    def set_valve_states(self, front_valve_states, back_valve_states):
        with self.ai, self.front_valves, self.back_valves:
            num_samples = int(self.ai.timing.samp_clk_rate * 1.0)
            self.ai.start()
            trace_start = self.ai.read(num_samples)
            self.front_valves.write([int(x) for x in front_valve_states], auto_start=True)
            # self.back_valves.write([int(x) for x in back_valve_states], auto_start=True)
            num_samples = int(self.ai.timing.samp_clk_rate * 2.0)
            self.ai.wait_until_done()
            trace_end = self.ai.read(num_samples)            
            trace = np.concatenate([trace_start, trace_end])
            return trace
