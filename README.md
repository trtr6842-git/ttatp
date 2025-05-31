# Trail Tracer Automated Test Procedure

# TODO
### Update from USB
* on boot, look for USB drive
    * check for folder
    * check for git repo copy
    * check for config file?
    * pull from copy of git repo

### atp.py
#### Flow control
* on boot, auto-start atp.py
    * must use `sudo .venv/bin/python atp.py` to have use file write permissions and still use .venv interpreter
    * add GPIO control for green button to start test
        * dtoverlay for 'ENTER' key press might be good enough, will need to check behavior mid-test
            * not great, holding button causes repeats and we really want edge only
    * add GPIO to control green button light

* handle various exceptions?

#### Reports
* pick folder naming convention
    * Local disk can probably just be 'reports'
    * USB drive/cloud folders must have serial no or UID

#### Auto-backup
    * switch to china-friendly cloud service
    * auto-update script
        * start on boot
        * attempt upload on boot (as a simple force upload)
        * attempt upload periodically in background
            * cron?

# Running ATP
To run from terminal, must use `sudo .venv/bin/python atp.py` for proper usb permissions


# RPi CM5 Setup
https://www.raspberrypi.com/documentation/computers/compute-module.html
## Write SSD Image
* open rpi-boot (program files (x86))  
* Add jumper to "disable EMMC boot"  
* Conenct 5V power leads to 40-pin GPIO pins p4 (+5V), p6 (GND)
* Press and hold the power button while turning on 5V
* Connect J11 USB-C to host computer
* Wait for rpi-boot to do its thing, then RPi CM5 should show up as UB drive.  
* run rpi-imager (program files (x86)) and write desired image
* ? press and hold power button to power off?
* Remove "disable EMMC boot jumper"
* Add jumper to "disable writing to EEPROM"
* Reboot


## Setting Up a Fresh RPi5
SSH into `atp@atp.loocal` the RPi and run the following commands:
```
sudo apt update
sudo apt full-upgrade
sudo reboot
sudo apt install git
git clone https://github.com/trtr6842-git/ttatp.git
mkdir ttatp_reports
mkdir media
cd ttatp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ~
```

## Adding new ssh key to rpi
On the computer you want to add, open a terminal and run
```
ssh-keygen -t rsa -b 4096 -C "TRPC25-RCTF_TT_ATS000"
```
where the quoted string after `-C` is a comment.  Hit enter three times to save the generated keys in the default location, which is usually \user\.ssh.

Open the id_rsa.pub file, this has the public SSH key.
Copy the public key and add it to `/.ssh/authroized_keys` on the rpi.  


## Using winscp for file transfer
Install and open winscp.  Create a new site using `atp@atp.local` as the hostname.  
Click `addvanced` settings and go to `SSH -> authorization` and select your ssh private key.  You may need to convert it to .ppk format.  Save the session and login.


## CM5 Poweroff Hangups
There are several issues that may cause a long pause when shutting down or rebooting, mostly due to the potential for missing WiFi or SD card detection when using certain CM5 configurations.

Didn't work for me...
https://forums.raspberrypi.com/viewtopic.php?t=383051

Also didn't work, maybe firmware update via raspi-config isn't up to date?
https://github.com/raspberrypi/linux/issues/6647

### Hacky but practical fix:
Use `sudo raspi-config` to change the boot order so NVMe is first (if being used).
Then add a dummy blank SD card.  Can be used for backup storage too!





## RPi Connect
```
cd ~
sudo apt install rpi-connect-lite
rpi-connect on
loginctl enable-linger
rpi-connect signin
```

## Remote code development vis VS Code
On remote development machine, open VS Code and install the 'Remote Development' Extension.
Use `CTR + SHIFT + P` and search for `Remotre SSH: COnnect current window to host`


## Handling USB drives
Create a dir to mount them to, then mount, then copy
```
cd ~
lsblk
mkdir edrv
sudo mount /dev/<drive partition name> edrv
cd edrv
cp <filename> <filepath>
sudo unmount /edrv
```

## OpenOCD on RPi5
according to https://github.com/raspberrypi/openocd/issues/93 with some edits
```
sudo apt install python3-libgpiod libgpiod-dev
sudo apt-get install git autoconf libtool make pkg-config libusb-1.0-0 libusb-1.0-0-dev
# git clone --depth 1 --branch v0.12.0 https://github.com/openocd-org/openocd.git
git clone https://github.com/raspberrypi/openocd.git
cd openocd
./bootstrap
export enable_linuxgpiod=yes
./configure --enable-linuxgpiod
make -j 4
sudo make install
sudo reboot
```
Interfaces  
`cd /usr/local/share/openocd/scripts/interface`  
Targets  
`cd /usr/local/share/openocd/scripts/target`  

OpenOCD RPi5 setup
```
cd /usr/local/share/openocd/scripts/interface
ls
sudo nano raspberrypi5-swd.cfg
```
Copy into raspberrypi5-swd.cfg
```
# match the pins used in the Pi Pico C/C++ manual
# GPIO25=swclk, GPIO24=swdio
# NOTE: trying to use GPIO8 for swdio failed
adapter driver linuxgpiod
adapter gpio swclk 25 -chip 4
adapter gpio swdio 24 -chip 4
```

configure Rx STM32 OpenOCD
```
cd rx/stm32
nano openocd.cfg
```
Copy this into file:
```
source [find interface/raspberrypi5-swd.cfg]
transport select swd

set CHIPNAME stm32g0x
source [find target/stm32g0x.cfg]

# did not yet manage to make a working setup using srst
#reset_config srst_only
reset_config  srst_nogate

adapter_nsrst_delay 100
adapter_nsrst_assert_width 100

init
targets
reset halt
program RCTF_TT_RX_REVA_G070CBx.elf verify
reset
shutdown
```
Then run
```
sudo openocd
```



## RPi5 UART
#### Enabling Hardware UART
`ls -l /dev/tty*` to list serial ports.  
`ttyAMAx` are hardware UART.  
`ttyACMx` are USB virtual COM ports.
`ttyAMA10` is on debug header, always active.

UART0 can be enabled via raspi-config.\
To enable more hardware UARTs, must manually edit config.txt.\
```
sudo nano /boot/firmware/config.txt
```
Then at the end add:
```
dtoverlay=uart2
dtoverlay=uart3
dtoverlay=uart4
```
Must reboot to take effect.

#### Serial Monitor
`python -m serial.tools.miniterm /dev/ttyAMA3 115200`

#### 40-pin header UARTS:
|/dev/tty* |UART#  |Tx/Rx Pins|GPIO Pins   |
|:--------:|:-----:|:--------:|:----------:|
|`ttyAMA0`|UART0|p8/p10|14/15|
|`ttyAMA2`|UART2|p7/p29|4/5|
|`ttyAMA3`|UART3|p24/p21|8/9|
|`ttyAMA4`|UART4|p32/p33|12/13|

## RPi5 Flashing STM32 via UART
Try stm32flash to flash directly via uart
```
git clone https://gitlab.com/stm32flash/stm32flash
cd stm32flash
make
sudo make install
cd ~/ttatp
stm32flash -b 230400 -w ~/ttatp/tx/stm32/RCTF_WFTX_REVA_STM32G030C8T6.bin /dev/ttyAMA3
```

## Get RPi serial number
```
cat /proc/cpuinfo | grep Serial
```
In Python:
```
os.popen('cat /proc/cpuinfo | grep Serial').read()
```

Then add to `config.csv` along with appropriate RCTF_ATS###

## Maybe hacky get STM32 UID
STM32 value line IC's don't have a guranteed unique UID, but it may be good enough for our use on the Tx.
On the STM32:
```
uint32_t uid[3];
uid[0] = HAL_GetUIDw0();
uid[1] = HAL_GetUIDw1();
uid[2] = HAL_GetUIDw2();
str_len = sprintf(pc_str, "UID: %lu%010lu%010lu\n\r", uid[0], uid[1], uid[2]);
HAL_UART_Transmit(&huart1, (uint8_t*)pc_str, str_len, 100);
```
On the ESP32 we can get the 64-bit MAC address:
```
Serial.prinf("ESP MAC: %llu", ESP.getEfuseMac())
```

On the RPi after parsing for the decimal number we can shorten it by encoding it to base 62 [0-9, a-z, A-Z]
```
import base62
base62.enocde(UID)
```

## GPIO dtoverlays
### Bind to key press
GPIO can be bound to key presses in the kernel  
https://forums.raspberrypi.com/viewtopic.php?t=255659
```
sudo nano /boot/firmware/config.txt
```
Adda t bottom:
```
dtoverlay=gpio-key,gpio=3,keycode=28
```

### Redirect disk status LED

## RCLONE setup OneDrive
Use Rclone to automatically sync results files to a cloud service
```
sudo -v ; curl https://rclone.org/install.sh | sudo bash
rclone config
```
Follow the instructions here:  
https://rclone.org/onedrive/

entries used:
```
n/s/q>n
name> ttatp_remote
Storage> onedrive
cliend_id>
client_secret>
region> global
tenant>
Edit Advanced Config? y/n> n
Use web browser...? y/n> n
```
On main PC, go to project stuff\RPi\rclone and open a terminal to run `"onedrive"`
```
config_toekn> <token from rclone authorize "onedrive" on main machine>
config_type> onedrive
config_driveid> <choose number for OneDrive (personal)>
Found drive "root" of type...
Y/n> y
Keep this remote? y/e/d> y
Quit config... > q
```

Usage:  
https://rclone.org/commands/
```
rclone copy ~/ttatp_reports ttatp_remote:atp_reports --ignore-existing
```

## Change Terminal Font
https://www.raspberrypi-spy.co.uk/2014/04/how-to-change-the-command-line-font-size/