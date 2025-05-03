# Trail Tracer Automated Test Procedure
## Setting Up a Fresh RPi5
SSH into `ttpi_xxx@ttpi.loocal` the RPi and run the following commands:
```
sudo apt update
sudo apt full-upgrade
sudo reboot
python3 -mvenv atp-venv
sudo apt install git
source atp-venv/bin/activate
pip install esptool
pip install git+https://bitbucket.org/subinitial/subinitial-automation.git
deactivate
```

## RPi Connect
```
cd ~
sudo apt install rpi-connect-lite
rpi-connect on
loginctl enable-linger
rpi-connect signin
```

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
git clone --depth 1 --branch v0.12.0 https://github.com/openocd-org/openocd.git
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

Openocd ttatp setup
```
cd ~
mkdir ttatp
cd ttatp
mkdir tx
mkdir rx
cd rx
mkdir stm32
mkdir esp32
cd ..
cd tx
mkdir stm32
mkdir esp32
cd ..
```

 Configure Rx STM32 OpenOCD
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
`sudo nano /boot/firmware/config.txt`

At the end, add `dtoverlay=uartx` where 'x' is the port number { 2 | 3 | 4 }  
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
