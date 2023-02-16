from model import DataModel
import time

if __name__ == '__main__':
    model = DataModel()
    model.start_acquisition()
    end_time = time.time() + 3  # Run for 10 seconds
    while time.time() < end_time:
        data = model.get_data()
        if data is not None:
            print(data)
    model.stop_acquisition()