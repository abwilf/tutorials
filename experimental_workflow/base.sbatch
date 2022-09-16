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

singularity exec -B /work/awilf/ --nv /work/awilf/<repo_name>/container.sif \
wandb agent socialiq/<repo_name>/j4dgyd0a # this line will be overwritten by wdb.py