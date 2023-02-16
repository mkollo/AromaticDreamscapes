import nidaqmx

class FlowDataModel:
    def __init__(self, dev_name, ch_name):
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(dev_name+'/'+ch_name)
        self.flow_data = []

    def read_flow(self):
        voltage_data = self.task.read()
        flow_data = (voltage_data - 1.315) * 0.8949
        self.flow_data.append(flow_data)
        return flow_data

    def get_flow_history(self, num_samples):
        return self.flow_data[-num_samples:]

