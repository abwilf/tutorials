# Singularity Environments on Atlas
For any conda environment on your development machine, seamlessly reproduce it on Atlas (or anywhere else) by doing the below.

## Preliminary Notes
Please replace all instances of the following in this tutorial to better match your use case
- `awilf` -> your username
- `my_env` -> the name of your conda environment
- the details of the `container.def` file in step 2 -> the details that match your dev environment
- `my_dir` -> whatever the directory with your code and data is for the project

I installed anaconda using this link, and installed into `/work/awilf/` (because on Atlas `/home/awilf/` is very limited).
```bash
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash Anaconda3-2021.11-Linux-x86_64.sh
```
NOTE: Steps 1-4 only have to happen once per machine.

## Tutorial

1. On your dev machine, make sure all packages are installed in `/work/awilf/anaconda3/envs/my_env` (not in pip cache!). You can use another path if you like, but this is best for Atlas. Get your program working in a conda environment on your dev machine, e.g.
```bash
conda activate my_env && python my_program.py
```
2. Create a `singularity` container `container.sif` to mimic your operating system and nvidia/cuda settings.
**container.def**
```
Bootstrap: docker
From: nvidia/cuda:11.1.1-cudnn8-devel-ubuntu20.04
```

On your dev machine, create the container file.
```bash
sudo singularity build container.sif container.def
```

Once you've done this, move it to an easy-to-remember path. I choose
```bash
mv container.sif /work/awilf/utils
```

3. Make sure you can run your program on your local machine within the container.
```bash
CONDA_ENV='my_env'
CONDA_PROFILE='/work/awilf/anaconda3/etc/profile.d/conda.sh' # replace with the path to your conda.sh script here
CONTAINER_PATH='/work/awilf/utils/container.sif'
singularity exec -B /work/awilf/ --nv $CONTAINER_PATH \
bash $CONDA_PROFILE && conda activate $CONDA_ENV && \
python my_program.py
```

4. Sync this over to the cluster.
```bash
rsync -av container.sif awilf@atlas:/work/awilf/utils
```

Note: the above only needs to happen once - any time you have a new environment, you can just do steps 5 and 6.

5. Now, on the cluster, when you're ready to run your program, just sync over your anaconda environment (any time it changes), and any files you want to run.
```bash
CONDA_ENV='my_env'
rsync -av /work/awilf/anaconda3/envs/$CONDA_ENV awilf@atlas:/work/awilf/anaconda3/envs
rsync -av /work/awilf/my_dir awilf@atlas:/work/awilf
```

6. Repeat the steps from (3), but this time on Atlas. I would recommend doing this first within an `srun` session to test it out, then within an sbatch when you distribute.
```bash
srun -p gpu_low --gres=gpu:1 --mem=56GB --pty bash
```


