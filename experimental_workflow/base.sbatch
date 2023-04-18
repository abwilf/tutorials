#!/bin/bash
#SBATCH -p gpu_highmem
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem 35GB 
#SBATCH --time 2-23:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=dummyblah123@gmail.com # TODO
#SBATCH --chdir=/work/awilf/<repo_name>
#SBATCH --output=/work/awilf/<repo_name>/logs/%j.out # TODO
#SBATCH --error=/work/awilf/<repo_name>/logs/%j.err # TODO

CONDA_ENV='trl' # TODO: replace this with your conda environment name
CONDA_PROFILE='/work/awilf/anaconda3/etc/profile.d/conda.sh'

singularity exec -B /work/awilf/ --nv /work/awilf/utils/container.sif \
bash $CONDA_PROFILE && source activate $CONDA_ENV && \
wandb agent socialiq/debias/cz8w7a7w
