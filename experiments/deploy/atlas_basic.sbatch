#!/bin/bash
#SBATCH -p low
#SBATCH --gres=gpu:1
#SBATCH --mem 40GB
#SBATCH --exclude atlas-2-9,atlas-1-13
#SBATCH --time 6-23:00
#SBATCH --chdir=/work/awilf/tutorials/experiments
#SBATCH --output=/work/awilf/logs/%j.out # TODO
#SBATCH --error=/work/awilf/logs/%j.err # TODO

mkdir -p /work/awilf/logs

singularity exec --nv --containall --cleanenv --env CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
    -B /home/awilf/ \
    -B /work/awilf/ \
    --pwd /work/awilf/tutorials/experiments \
    /work/awilf/base_img.sif \
    /bin/bash -c '. /work/awilf/anaconda3/etc/profile.d/conda.sh && conda activate example_env && \
    wandb agent socialiq/tutorials-experiments_deploy/uif1epbj # TODO: modify here
    '\