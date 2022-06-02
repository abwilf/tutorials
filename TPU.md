# TPU VM's
## Motivation and Background on TPU Research Cloud and TPU VM's
Recently, some large models have been published that require large memory GPU's to accelerate computation.  This can be achieved through a single large memory GPU (e.g. 3090Ti with 24GB), or by putting together many different GPU's in a shared memory architecture. If you have a single machine with 8 GPU's for example, this means that in the forward pass it sends batch size / 8 samples to each GPU, then in the backward pass it averages the gradient information from all 8 forward passes and uses that for optimization. TPU's offer this abstraction, but use a faster shared memory architecture and virtualize different "devices" with different cores of a single piece of hardware.  Because this hardware is optimized for deep learning, it is called a "Tensor Processing Unit".

Some models (e.g. MERLOT) are written in frameworks that are optimized for TPU's (e.g. jax).  We've been given access to free TPU's for 90 days.  The abstraction is that we spin up a virtual machine for each TPU piece of hardware. The structure of this environment is a linux VM with 85GB free in /home.  You will have sudo access (passwd 1234) and can do anything you'd like within this environment for research *only*. This is not a machine to be used for personal projects (else we'll have broken the terms and service of the grant and Google has been great to us so we very much don't want that). The only caveat is please ask me before using any gcloud commands. You shouldn't need these, and it could mess with the other TPU's in our network.

Below are some notes on getting started from your side (collaborator side) and from the admin side, as I plan to share this document with my labmates who are starting similar projects.

## Getting Started (Collaborator Side)
1. Send me your ssh public key.  On linux, you can find this in `~/.ssh/id_rsa.pub`.  It might be elsewhere on Windows. Your ssh key will end with a username, e.g. `...<username>@<machine>`.
2. I'll send you a confirmation email when you've been added.  In it I will include which TPU number you will use. Go to this link and get the external IP address for your assigned TPU – e.g. an external ip will look like this `34.121.133.146`.
[https://console.cloud.google.com/compute/tpus?project=social-intelligence-351218](https://console.cloud.google.com/compute/tpus?project=social-intelligence-351218)

3. To log in, add this to your `~/.ssh/config` (for linux; ssh config may be stored elsewhere on Windows).
```
Host tpu
    HostName [EXTERNAL_IP]
    User [<username> from ssh key]
    ForwardAgent yes
```

You can then ssh in like this
```
ssh <username>@tpu
```

Because VSCode and `rsync` piggyback on `ssh`, you'll have access to those to view and run code remotely and to transfer data without entering a password each time.

e.g.
```
rsync ./hi.txt <username>@tpu:/home/<username>
```

You can use `/home/<username>` for your project.  If you need more space, let me know and I think we may be able to add an external disk.

4. Occassionally Google will change around the external IP's. If you were able to log in but are now unable, check the console again and update your external ip in `~/.ssh/config`.
[https://console.cloud.google.com/compute/tpus?project=social-intelligence-351218](https://console.cloud.google.com/compute/tpus?project=social-intelligence-351218)

A few general notes: I would strongly recommend installing VSCode and setting up remote code editing and execution on the TPU.  This will be essential for you to be able to debug the code.  It may take a bit to get up and running, but it will pay off manyfold in efficiency and sanity over time.  For debugging and most development, I would run in VSCode so you can see exactly what's happening.  

For long running tasks (once you've debugged and implemented what you want to and need to do full tests), I would recommend `tmux`.  If you haven't used it before, the idea is that you open a screen with something like
```
tmux new -s myscreen
```

Then run your process within that, meaning you can break your ssh connection, come back, and attach to the screen without worrying that closing your computer will halt the process.

I would also recommend using a conda environment to manage dependencies, in case you ever need to swap between different versions of packages. You can install conda like this:
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh && bash Anaconda3-2021.11-Linux-x86_64.sh
```

## Getting Started (Admin Side)
**Collaborators: you don't need to read past here**.  These are notes for myself and other admins.

### Create a TPU VM
To create the first TPU VM, you first need to spin up another VM in the same region (e.g. `us-central-1f`) and do these commands from there.
```
name='tpu1' && zone='us-central1-f' && tpu_type='v2-8'
gcloud config set compute/zone ${zone}

gcloud alpha compute tpus tpu-vm create ${name} \
--zone ${zone} \
--accelerator-type ${tpu_type} \
--version tpu-vm-tf-2.8.0
```

You can then ssh into the TPU.  You should first add yourself as a user so you don't have to log in as root in the future.  See the section below for how to do that.
```
gcloud alpha compute tpus tpu-vm ssh ${name} --zone ${zone}
```

At this point, you should shut down and delete the initial VM.  You have to pay for that, whereas the TPU VM's are covered by the grant.  We also have to pay for the data disks, but that cost is negligible.

### Add a Data Disk to a TPU VM
You can add a data disk using the instructions [online](https://cloud.google.com/compute/docs/disks/add-persistent-disk).  To attach it to a TPU (read-only mode so it can be attached to multiple TPU's)
```
name='tpu1' && zone='us-central1-f' && tpu_type='v2-8'

gcloud alpha compute tpus tpu-vm attach-disk ${name} \
    --zone=us-central1-f \
    --disk=tvqa-disk \
    --mode=read-only

# mount disk
sudo lsblk
sudo mkdir -p /ssd
sudo mount -o discard,defaults /dev/sdb /ssd
sudo chmod a+w /ssd
```

You can also do the same thing but with `detach-disk` if you need to.


## Adding a Collaborator (Admin Side)
1. Ask for their ssh public key.
2. Add them as a `sudo` user to one of the TPU's.

```
# to ssh in from a google vm or another tpu
name='tpu5' && zone='us-central1-f' && tpu_type='v2-8'
gcloud alpha compute tpus tpu-vm ssh ${name} --zone ${zone}

# to ssh in from taro
ssh awilf@tpu5

# create user
sudo useradd -m -d /home/milo -s /bin/bash milo
sudo passwd milo
1234

# add to authorized keys
sudo mkdir -p /home/milo/.ssh/
sudo bash -c 'echo \
"\
PASTE_SSH_PUBLIC_KEY_HERE\
"\
> /home/milo/.ssh/authorized_keys'

# ensure the directory is owned by the new user
sudo chown -R milo /home/milo/.ssh
```

3. Send them an email with the external IP and which TPU number they are



