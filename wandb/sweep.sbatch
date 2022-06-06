#!/bin/bash
#SBATCH -p gpu_low
#SBATCH --gres=gpu:1
#SBATCH --mem 10GB 
#SBATCH --time 1-00:00
#SBATCH --exclude=compute-0-19
#SBATCH --mail-type=ALL
#SBATCH --mail-user=dummyblah123@gmail.com # TODO
#SBATCH --chdir=/work/awilf/wandb_example/ # TODO
#SBATCH --output=/work/awilf/wandb_example/logs/%j.out # TODO
#SBATCH --error=/work/awilf/wandb_example/logs/%j.err # TODO

singularity exec -B /work/awilf/ --nv /results/awilf/imgs/tvqa_graph.sif \
wandb agent socialiq/emtvqa/ijutr0h0
echo "a" >> email_log.txt
