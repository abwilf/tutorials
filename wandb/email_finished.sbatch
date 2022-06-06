#!/bin/bash
#SBATCH -p cpu_low
#SBATCH --mem 1GB 
#SBATCH --time 1-00:00
#SBATCH --exclude=compute-0-19
#SBATCH --mail-type=ALL
#SBATCH --mail-user=dummyblah123@gmail.com # TODO
#SBATCH --chdir=/work/awilf/wandb_example/ # TODO
#SBATCH --output=/work/awilf/wandb_example/logs/%j.out # TODO
#SBATCH --error=/work/awilf/wandb_example/logs/%j.err # TODO

python email_checker.py 3
