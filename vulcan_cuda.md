# Common Issues on Vulcan with Cuda
Written by Mengrou Shou <mshou@andrew.cmu.edu>

## Preface
This guide aims to provide troubleshooting steps for CUDA 11.6 and Nvidia driver 510.47.03 installed on the Vulcan machine.

## Checks and Solutions
### Verifying if CUDA is installed
```
nvcc -V
```

If this doesn’t work, it may be because PATH hasn’t been configured correctly. Check if the following lines are in the ./bashrc file (e.g. /home/<account name>/.bashrc for the Vulcan machine)
```
export PATH=/usr/local/cuda-11.6/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-11.6/lib64\ ${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

### Verifying if Nvidia driver is installed
Lists the installed driver revision and the version of the GNU C compiler used to build the Linux kernel module
cat /proc/driver/nvidia/version
Monitor the driver
nvidia-smi

### Show GPU hardware specs
```
sudo lshw -c display
```

### CUDA with Python
Check if CUDA is working with Python
python
import torch
print(torch.cuda.current_device()) # should not error out
torch.cuda.is_available() # should return true

Check which CUDA version Pytorch was built on (both work)
torch.version.cuda
print(torch.__version__)

## Errors
### Failed to initialize NVML: Driver/library version mismatch
Possible solutions:
1) Reboot
```
sudo reboot
sudo mount -o discard,defaults /dev/sdc1 /work
```
2) If 1 does not work, reinstall Nvidia driver
Uninstall Nvidia driver
```
sudo /usr/bin/nvidia-uninstall
```
Get CUDA runfile if you don’t have it
```
wget https://developer.download.nvidia.com/compute/cuda/11.6.2/local_installers/cuda_11.6.2_510.47.03_linux.run
```
Install Nvidia driver by running the runfile
```
sudo sh cuda_11.6.2_510.47.03_linux.run
```

