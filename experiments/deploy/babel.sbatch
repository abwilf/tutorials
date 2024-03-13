#!/bin/bash
#SBATCH --partition general
#SBATCH --gres=gpu:A6000:1
#SBATCH --nodes=1
#SBATCH --mem 30GB
#SBATCH --cpus-per-task=2
#SBATCH --time 1-23:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=dummyblah123@gmail.com # TODO
#SBATCH --chdir=/home/awilf/code_sim/bigcode-evaluation-harness/magicoder
#SBATCH --output=/home/awilf/logs/%j.out # TODO
#SBATCH --error=/home/awilf/logs/%j.err # TODO

HF_CACHE="/data/tir/projects/tir7/user_data/awilf/hf_cache"
export WANDB__SERVICE_WAIT=600
singularity exec --nv --containall --cleanenv --env CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
    -B /home/awilf/:/home/awilf/ \
    -B /home/awilf/:/work/awilf/ \
    -B /data/tir/projects/tir7/user_data/awilf \
    --pwd /work/awilf/code_sim/bigcode-evaluation-harness \
    --env TRANSFORMERS_CACHE=${HF_CACHE} \
    --env HF_HOME=${HF_CACHE} \
    --env WANDB__SERVICE_WAIT=600 \
    /home/awilf/base_img.sif \
    /bin/bash -c '. /work/awilf/anaconda3/etc/profile.d/conda.sh && \
    conda activate magicoder && PYTHONPATH=${PYTHONPATH}:/work/awilf/code_sim/bigcode-evaluation-harness/magicoder/src  && \
    wandb agent blah