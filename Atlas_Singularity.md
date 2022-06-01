# Singularity Environments on Atlas

## Notes
These are reproducible steps from scratch for getting an arbitrary conda environment from your personal machine working on atlas
Replace all instances of awilf and taro in this tutorial with your andrewid and personal workstation name.

## Requirements
On both atlas and taro have this anaconda installed in /work/awilf/
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
```

Your personal workstation should have ubuntu20.04 installed (or if not, change the VM version you use)

Your personal workstation should have singularity3.x installed.  I use 3.6.3; atlas uses singularity3.8.7.  I haven't run into any compatibility issues so far.

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
# -B binds /work/awilf/ and everything under it to be accessible by your sandbox, including the conda envs you'll send over
# --nv passes nvidia drivers, which you'll need to access GPU
singularity shell -B /work/awilf/ --nv base_sandbox

__conda_setup="$('/work/awilf/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/work/awilf/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/work/awilf/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/work/awilf/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup

conda activate tvqa_graph

python -c "import torch; print(torch.cuda.is_available(), torch.__version__); import torch_scatter; import torch_sparse; import torch_geometric"
```

## Clean up dependencies
On taro: get rid of .local.  Sometimes packages can be hiding here.  We need all packages to be in /work/awilf/anaconda3.
    mv ~/.local/lib/python3.7 ~/.local/lib/python3.7_bak

Rerun the above test. If this breaks, then find all the packages installed in .local, uninstall them, and reinstall them in anaconda using lines like this

```
pip uninstall -y pandas && pip install --no-cache-dir pandas==0.1.2
```

## Get working on atlas
### Sync over all anaconda envs (this can take a long time the first time)
```
rsync -av /work/awilf/anaconda3 awilf@atlas:/work/awilf/
```

### Create and transfer .sif file (shouldn't take long b/c no packages are stored)
```
rm tvqa_graph.sif
sudo singularity build tvqa_graph.sif base_sandbox
rsync tvqa_graph.sif awilf@atlas:/results/awilf/imgs
```

### Run on atlas
```
cd /results/awilf/awilf/imgs
singularity shell -B /work/awilf/ --nv tvqa_graph.sif

source ~/.bashrc # or if this doesn't work, use the __conda_setup block above
conda activate tvqa_graph
python -c "import torch; print(torch.cuda.is_available(), torch.__version__); import torch_scatter; import torch_sparse; import torch_geometric"
```

## Modifying and creating new sandboxes
This should be a general solution, but if you need to change anything about the sandbox you can do so with this command
```
sudo singularity shell --writable base_sandbox
```
