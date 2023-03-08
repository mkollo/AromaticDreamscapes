import numpy as np
import nidaqmx

def valve_pattern(pattern, sample_rate=1000, duration=3):

    num_samples = int(sample_rate * duration)
    
    pre_samples = int(sample_rate * 0.5)
    post_samples = pre_samples
    
    ai_data = np.zeros((num_samples + pre_samples + post_samples, 2))
    
    # front_valve_chan = self.front_valves.do_channels.get_channel("Front_valves/port0/line0:15")
    # back_valve_chan = self.back_valves.do_channels.get_channel("Back_valves/port0/line0:23")
    
    time_vector = np.arange(num_samples + pre_samples + post_samples) / sample_rate
    
    pfi_line = "/Dev1/PFI0"
    
    ctr_task = nidaqmx.Task()
    ctr_task.co_channels.add_co_pulse_chan_freq("/cDAQ1/Ctr0", "InternalClock", freq=1000, duty_cycle=0.5)

    ctr_task.start()

    front_valve_task = nidaqmx.Task()
    front_valve_task.do_channels.add_do_chan("Front_valves/port0/line0:15")
    front_valve_task.timing.cfg_samp_clk_timing(sample_rate, source=pfi_line,
                                                samps_per_chan=num_samples,
                                                sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
    back_valve_task = nidaqmx.Task()
    back_valve_task.do_channels.add_do_chan("Back_valves/port0/line0:23")
    back_valve_task.timing.cfg_samp_clk_timing(sample_rate, source=pfi_line,
                                               samps_per_chan=num_samples,
                                               sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
    

    ai_task = nidaqmx.Task()
    ai_task.ai_channels.add_ai_voltage_chan("AI/ai0:1")
    ai_task.timing.cfg_samp_clk_timing(sample_rate, source=pfi_line,
                                        samps_per_chan=num_samples,
                                        sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
    
    for row in pattern:
        front_valve_task.write(row[:16], auto_start=False)
        back_valve_task.write(row[16:], auto_start=False)
        
        front_valve_task.start()
        back_valve_task.start()
        
        front_valve_task.wait_until_done()
        back_valve_task.wait_until_done()
        
    # front_valve_task.write(np.ones(16), auto_start=False)
    # back_valve_task.write(np.zeros(24), auto_start=False)
    
    # front_valve_task.start()
    # back_valve_task.start()
    
    # front_valve_task.wait_until_done()
    # back_valve_task.wait_until_done()
    
    ai_chan = ai_task.ai_channels.get_channel("AI/ai0:1")
    ai_task.start()
    
    ai_task.wait_until_done()
    
    for i in range(num_samples + pre_samples + post_samples):
        ai_data[i] = ai_chan.read()
        
    
    ai_task.stop()
    
    return ai_data[pre_samples:num_samples+pre_samples, :]

valve_pattern(pattern, sample_rate=1000, duration=3)
