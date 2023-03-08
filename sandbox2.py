import numpy as np
import nidaqmx as ni


def query_devices():
    local_system = ni.system.System.local()
    driver_version = local_system.driver_version

    print('DAQmx {0}.{1}.{2}'.format(driver_version.major_version, driver_version.minor_version,
                                    driver_version.update_version))

    for device in local_system.devices:
        print('Device Name: {0}, Product Category: {1}, Product Type: {2}'.format(
            device.name, device.product_category, device.product_type))

with nidaqmx.Task() as task:
   ai_channel = task.ai_channels.add_ai_thrmcpl_chan("cDAQ1Mod3/ai0")
   ai_channel.ai_adc_timing_mode = ADCTimingMode.HIGH_SPEED