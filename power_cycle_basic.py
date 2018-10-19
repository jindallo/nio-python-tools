import can
import shutil
from airbender import Airbender
from can import interface, Message
from os import mkdir


# First begin sending necessary can signals
bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)
keep_alive = can.Message(arbitration_id=0x505, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], extended_id=False)
driver_present = can.Message(arbitration_id=0x2c3, data=[0x10, 0x00], extended_id=False)
x505 = bus.send_periodic(keep_alive, 0.64)
x2c3 = bus.send_periodic(driver_present, 0.02)

with Airbender() as dut:
    loopAmount = input('Loop: ')
    test_count = 0
    while test_count < loopAmount:
        log_folder = 'logs_iteration_' + str(test_count + 1)
        if os.path.exists(log_folder):
            shutil.rmtree(log_folder)
        os.mkdir(log_folder)

        # Reset airbender
        dut.reset()

        # Get MCU status
        with open(log_folder+'/mcu_logs.txt', 'w') as mcu_logs:
            mcu_logs.write(dut.MCU.execute_command('status'))

        # Get QNX logs
        with open(log_folder+'/qnx_logs.txt', 'w') as qnx_logs:
            qnx_logs.write(dut.QNX.execute_command('slog2info'))

        # Get Linux logs
        dut.Linux.login()
        with open(log_folder+'/linux_logs.txt', 'w') as linux_logs:
            linux_logs.write(dut.Linux.execute_command('dmesg'))

        # Get Android logs
        with open(log_folder+'/android_logs.txt', 'w') as android_logs:
            android_logs.write(dut.Linux.execute_command('logcat', timeout=30))

        test_count += 1
