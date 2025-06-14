## Raspberry Pi setup:

```
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
```

### Python 3.8 and pip installation (if you doesn't have Python installed)

```
wget https://www.python.org/ftp/python/3.8.8/Python-3.8.8.tgz
tar -xf Python-3.8.8.tgz
cd Python-3.8.8
./configure --enable-optimizations
sudo make altinstall
sudo apt install python3-pip
```

### Manipulator code

Download the program .zip-file

```
mkdir ~/manipulator
unzip ~/Downloads/yolov8_recognizer_manipulator.zip -d ~/manipulator
```

### Libraries installation

```
python3 -m venv --system-site-packages myenv
source myenv/bin/activate
sudo apt update
sudo apt install python3-opencv libopencv-dev
```

### Then execute commands below:
```
pip install -r yolov8_recognizer_manipulator/requirements/requirements.txt
```

### OR use:

```
pip install numpy==1.24.4
pip install pyserial==3.5
pip install cvzone==1.6.1
pip install ultralytics==8.2.0
pip install lapx==0.5.2
pip install picamera2==0.3.18
```

### Thonny installation (if you want and if Raspberry Pi doesn't contain it)

```
sudo pip install thonny
```

### VS Code installation (if you want, you can use VS Code instead of Thonny)

Download your version here (.deb for Ubuntu and Debian, .rpm for Red Head and Fedora):
https://code.visualstudio.com/ (code_1.85.1-1702462158_amd64.deb in my case)

```
sudo dpkg -i code_1.85.1-1702462158_amd64.deb
sudo apt-get install -f
code
```

Download the python package in VS Code and open the "yolov8_recognizer_manipulator" folder in it

Press Ctrl+Shift+P, choose "Select Interpreter", then choose environment

### Dotnet installation

Download the version of dotnet for your system to ~/Downloads: https://dotnet.microsoft.com/download/dotnet/8.0
(in my case Arm64 binaries (dotnet-sdk-8.0.201-linux-arm64.tar.gz))

```
mkdir ~/dotnet-core
tar zxf ~/Downloads/dotnet-sdk-3.1.426-linux-x64.tar.gz -C ~/dotnet-core
export PATH=$PATH:~/dotnet-core
source ~/.bashrc
dotnet --version
```

If the console prints the dotnet version, everything is fine

And then you can build and run your code

### Code execution

```
source myenv/bin/activate
cd ~/manipulator/yolov8_recognizer_manipulator
python3 yolov8_recognizer_manipulator.py
```

You can create a desktop icon by following these instructions:

1)
```
nano ~/Desktop/run_commands.sh
```
2) Inside this file enter:

```
#!/bin/bash
source myenv/bin/activate
cd ~/manipulator/yolov8_recognizer_manipulator
python3 yolov8_recognizer_manipulator.py
```

3) ```chmod +x ~/Desktop/run_commands.sh```
4) ```nano ~/Desktop/run_commands.desktop```
5) Inside this file enter:

```
[Desktop Entry]
Type=Application
Name=Run Commands
Icon=utilities-terminal
Exec=/path/to/run_commands.sh
Terminal=true
```

### Transferring data from the Raspberry Pi to your local device

```
scp path_from user_name@rpi_ip_address:path_to
```

### Connecting with VNC

```
ssh user@ip_address -> enter "yes"
sudo raspi-config -> Interface Options -> VNC -> yes
sudo raspi-config -> System options -> Boot / Auto login -> Desktop Autologin
Finish -> yes
```

### Camera rotation

```
sudo nano /boot/firmware/config.txt
dtoverlay=ov5647,rotation=180 # ov5647 is your camera's name
```
