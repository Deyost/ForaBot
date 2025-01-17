import time
import subprocess
import yaml

class PinStepper():
    def __init__(self, serial_num, position_dict):
        self.position_dict = position_dict
        self.serial_num = serial_num
        self.energize()
        self.exitSafeStart()
        self.home()

    @staticmethod
    def ticcmd(*args):
        return subprocess.check_output(['ticcmd'] + list(args))

    def pinMove(self, position):
        self.ticcmd('-d', self.serial_num,'--position', str(self.position_dict[position]))
        self.waitComplete('Current position', self.position_dict[position])

    def pinMoveHalf(self,position):
        self.ticcmd('-d', self.serial_num,'--position', str(self.position_dict[position]//2))
        self.waitComplete('Current position', self.position_dict[position]//2)

    def focalPlane(self, plane_num):
        #focal_pos = self.position_dict['imaging'] + plane_num
        focal_pos = self.position_dict['imaging'] + (32*72) - plane_num
        print(focal_pos)
        self.ticcmd('-d', self.serial_num, '--position', str(focal_pos))
        self.waitComplete('Current position', focal_pos)

    def home(self):
        self.ticcmd('--home', 'fwd', '-d', self.serial_num)
        self.waitComplete('Position uncertain', False)

    def energize(self):
        self.ticcmd('--energize', '-d', self.serial_num)

    def deenergize(self):
        print('deenergize')
        self.ticcmd('--deenergize', '-d', self.serial_num)

    def exitSafeStart(self):
        self.ticcmd('--exit-safe-start', '-d', self.serial_num)

    def waitComplete(self, check_key, check_expected_val):
        status = {check_key: None}
        num_checks = 0
        while status[check_key] != check_expected_val:
            if num_checks > 200:
                print(status)
                raise Exception('Status check not complete: {} did not equal {}'.format(check_key, check_expected_val))
            status = yaml.load(self.ticcmd('-s', '--full', '-d', self.serial_num), Loader=yaml.FullLoader)
            num_checks += 1
            time.sleep(0.1)
