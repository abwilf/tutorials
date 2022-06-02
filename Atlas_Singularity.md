# Singularity Environments on Atlas

## Motivation and Some High Level Notes
These are reproducible steps from scratch for getting an arbitrary conda environment from your personal machine working on Atlas (or any other cluster). Find and replace all instances of awilf and taro in this tutorial with your andrewid and personal workstation name.

A common approach to creating containers that can reproduce code between your personal machine and another system is this:
1. On your personal machine, create a container with the same OS as your personal machine
2. Install all the packages within it exactly as you installed them on your personal machine
3. Copy all the data and code to the container
4. Package it up, send it out, and run the code wherever

I have found problems with this approach.  Step (1) works fine, but step (2) can run into unforseen difficulties that can be very hard to debug, especially with conda environments with complex dependencies or `.whl` files.  Step (3) can be very costly in terms of space, and step (4) can take a long time because the container is large; this step also becomes increasingly expensive as the number of edits you make to the code grows.  If you edit the code on your local machine then have to repackage and resend the container each time, it will be very inefficient.

Instead, the approach I take here is slightly different:
1. On your personal machine, install all packages into a `conda` environment in some path that exists on both your remote and local machines, e.g. `/work/awilf/anaconda3` and get the code working how you'd like
2. Create a container with the same OS as your personal machine
3. Activate the container, binding the `conda` env paths within it (so the container can access those files by reference). Create an environment script to initialize conda in this new shell from wherever conda is stored, `conda activate` the environment, and set any other environment variables you'd like.  Then all you need to do to run the code on your personal machine is bind the paths referencing the code and data so you can see them (by reference) from within the container.
4. In essence, the container then just needs to store your OS and the steps for activating the environment. So next you'll package it up and send it, but this should be very lightweight and will likely only need to happen once (unless you change your conda environment name).
5. Send over your code, data ,and *whole* conda folder (I do this for ease, as it only needs to happen once but you may be able to do this with just part by only sending e.g. `/work/awilf/anaconda3/envs/env_name` – though I haven't tested this).  I like to make sure they're in the same absolute paths, so your code doesn't have to change - e.g. if you have your code in `/work/awilf/code.py` and your data in `/work/awilf/data`, then the runscript will be the same between your local and remote machines: e.g. `python /work/awilf/code.py /work/awilf/data` or `singularity exec -B /work/awilf/ --nv container.sif python /work/awilf/code.py /work/awilf/data`. This will be time consuming, but only needs to happen once at the beginning (not whenever you update).  Whenever you update the data, you can send only what was updated with rsync which will not take long – e.g. `rsync -av /work/awilf/anaconda3 awilf@atlas:/work/awilf/`.
6. To run the code on Atlas, simply prepend a command that pulls the code from your local machine and then runs the command, e.g. `rsync -av --exclude data awilf@taro:/work/awilf/code_dir /work/awilf/ && singularity exec -B /work/awilf/ --nv container.sif /work/awilf/code.py`

To sum up, then.  
1. *Once, at the beginning of the project*: you'll need to create the environment, get the code working on your local machine, create the container, send the container, conda env, data, and code over to atlas and get it running.
2. *Whenever you make updates*: if updates are just to the code, you can prepend a line that pulls code very quickly from your local machine.  If updates are to data or environments, it might take longer but only has to happen once whenever you make the update.

In the rest of this tutorial, I will describe detailed steps for doing this.

## Requirements
On both atlas and taro have this anaconda installed in /work/awilf/ (NOT /home/awilf, because atlas has limited space there)
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
```

Your personal workstation should have ubuntu20.04 (or if not, change the VM version you use in the `docker:` command below) and singularity3.x installed.  I use 3.6.3; atlas uses singularity3.8.7.  I haven't run into any compatibility issues so far.

## Building the base environment from scratch [OPTIONAL: once you've done this once, you can cp -R base_sandbox my_new_sandbox_name]
```
singularity build --sandbox base_sandbox docker://nvidia/cuda:11.1-cudnn8-devel-ubuntu20.04

sudo singularity shell --writable base_sandbox
apt update
apt-get install -y wget vim
exit
```

## Sanity check: use this to run an existing environment to make sure the dependencies work on your local machine
Open a singularity shell with this sandbox, initialize conda (copied from ~/.bashrc), test dependencies. Replace `tvqa_graph` with an environment you'd like to test, and postfix to the `python -c` line with whatever dependencies you'd like to test.

```
# -B binds /work/awilf/ and everything under it to be accessible by your sandbox, including the conda envs you'll send over.  I would recommend creating a /work/andrew_id folder on your local machine to store conda because that is how it will be on atlas.

# --nv passes nvidia drivers, which you'll need to access GPU
singularity shell -B /work/awilf/ --nv base_sandbox

. /work/awilf/anaconda3/etc/profile.d/conda.sh
conda activate tvqa_graph

python -c "import torch; print(torch.cuda.is_available(), torch.__version__); import torch_scatter; import torch_sparse; import torch_geometric"
```

## Clean up dependencies
On taro: get rid of .local.  Sometimes packages can be hiding here.  We need all packages to be in /work/awilf/anaconda3.
```
mv ~/.local/lib/python3.7 ~/.local/lib/python3.7_bak
```

Rerun the above test. If this breaks, then find all the packages installed in .local, uninstall them, and reinstall them in anaconda using lines like this

```
pip uninstall -y pandas && pip install --no-cache-dir pandas==0.1.2
```

## Get working on atlas
### Sync over all anaconda envs (this can take a long time the first time)
```
rsync -av /work/awilf/anaconda3 awilf@atlas:/work/awilf/
```

### Change environment preprocessing
If you want to add some environment code to run before singularity runs the container (e.g. in `singularity exec`), you can put it in the file `base_sandbox/environment`.

For this use case, it's necessary to initialize conda within the container. You can do this by putting these lines in `base_sandbox/environment` before building.

```
#!/bin/sh
# Custom environment shell code should follow

. /work/awilf/anaconda3/etc/profile.d/conda.sh
conda activate tvqa_graph
```


### Create and transfer .sif file (shouldn't take long b/c no packages are stored)
```
rm tvqa_graph.sif
sudo singularity build tvqa_graph.sif base_sandbox
rsync tvqa_graph.sif awilf@atlas:/results/awilf/imgs
```

### Run on atlas
Or for shell
```
singularity exec -B /work/awilf/ --nv /results/awilf/awilf/imgs/tvqa_graph.sif python -c "import torch; print(torch.cuda.is_available(), torch.__version__); import torch_scatter; import torch_sparse; import torch_geometric"
```

```
singularity shell -B /work/awilf/ --nv /results/awilf/awilf/imgs/tvqa_graph.sif
python -c "import torch; print(torch.cuda.is_available(), torch.__version__); import torch_scatter; import torch_sparse; import torch_geometric"
```


## Modifying and creating new sandboxes
This should be a general solution, but if you need to change anything about the sandbox you can do so with this command
```
sudo singularity shell --writable base_sandbox
```


## TODO: get this working directly from .def files so it's cleaner
