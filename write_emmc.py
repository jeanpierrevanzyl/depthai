# import blkinfo
from blkinfo.filters import BlkDiskInfo
import json
import os
import re
import subprocess
from time import sleep, time
import argparse
from pathlib import Path
import sys
# device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
# df = subprocess.check_output("lsusb")
# devices = []
# for i in df.split('\n'):
#     if i:
#         info = device_re.match(i)
#         if info:
#             dinfo = info.groupdict()
#             dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
#             devices.append(dinfo)
# print(devices)

parser = argparse.ArgumentParser()
parser.add_argument("-img", help="place the img file in the same directory as write_emmc.py and pass the filename here",
                    type=str)


curr_path = Path(__file__).parent.resolve()
args = parser.parse_args()
img_path = os.path.join(curr_path, args.img)
print(img_path)
img_file = Path(img_path)
if not img_file.exists():
    print("file does not exist. please input right image file")
    sys.exit(1)

home = str(Path.home())
boot_pth = home + "/usbboot/rpiboot"
boot_file = Path(boot_pth)
if not boot_file.exists():
    print("Couldn't fild rpiboot file at {}. Please update it's location to be found at this path".format(boot_pth))
    sys.exit(1)



# install rpiboot first
def start_rpi_boot():
    boot_cmd = "sudo " + boot_pth
    response = os.system(boot_cmd)
    # and then check the response...
    if response == 0:
        eMMC_status = True
    else:
        eMMC_status = False

    return eMMC_status

print("Set jumper to enable on the board.")
print("Connect the device to a linux-pc using usb cable.")
print("Press \"enter\" when ready to start searching for the device")
print("After pressing \"enter\" connect the device to the power source")

input()
start_rpi_boot()
print("Search Complete....!")

sleep(2)

myblkd = BlkDiskInfo()
filters = {
        'name': "sd*"
    }
all_my_disks = myblkd.get_disks(filters)
json_output = json.dumps(all_my_disks)
print(json_output)
divident = 10**9

print("Image will be written to the drives shown below.")
for device_obj in all_my_disks:
    disk_size = int(device_obj["size"]) / divident
    print(disk_size)
    if disk_size < 33 and disk_size > 14: 
        print("Device name: {0}  size:{1}".format(device_obj["name"], disk_size))

print("Press Enter key to continue writing the OS. [ctrl + c to abort]")
input()

response_status = []
start = time()


for item in all_my_disks:
    # print(int(item["size"]))
    disk_size = int(item["size"]) / divident
    print(disk_size)
    if disk_size < 33 and disk_size > 14: 
        test_cmd = "sudo dd if=" + img_path + " of=/dev/" + item["name"] + " bs=4M conv=fsync status=progress"
        print(test_cmd)
        p = subprocess.Popen(test_cmd, shell=True, preexec_fn=os.setsid)
        response_status.append(p)

is_finished = False 
while not is_finished:
    temp_status = True
    for proc in response_status:
        if proc.poll() is None:
            temp_status = False
    
    is_finished = temp_status

end = time()
print(end - start)

print("Finishing writing to eMMC")








