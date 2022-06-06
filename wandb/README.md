# wandb
Note: `taro` is my local machine. Replace all instances of `taro` with yours, and all instances of `awilf` with your andrewid. Atlas is the name of our cluster; it can be any slurm based cluster.

## Motivation
`wandb` is an amazing tool to manage experiments and run hyperparameter searches.   Check out their [quickstart](https://docs.wandb.ai/quickstart) to see just how easy it is to get started.

Once you've gotten wandb working to manage experiments on your development machine, this repo will help you deploy your tests to Atlas with many `wandb agent`s running different parts of the grid search (which they call a sweep because wandb supports more tuning procedures than just grid search).

To do this, you'll only need three files: 
* `config.yaml`: defines the hyperparameter search
* `main.py`: is the entrypoint to your training code, which takes arguments from `stdin`
* `sweep.sbatch`: activates the environment and creates a `wandb` agent which executes part of the search

## Installing dependencies
For this example, install these dependencies:
```
torch, torchvision, wandb
```

## Deploying Grid Searches on Atlas
### Installing
On Atlas `clone` this repo into `/work/awilf/`
Create a conda env with `wandb` in it. I called mine `sweep`.

### To Run
1. On Taro (or Atlas) initialize the sweep
```
cd /work/awilf/wandb_example
conda activate sweep
wandb sweep config.yaml
```

2. Edit the `.sbatch` file describing what your worker nodes will do.  An example to get you started is in `sweep.sbatch`. 
The above command will print the full sweep name last.  Make this the last line of your `sweep.sbatch` script, e.g.
```
#!/bin/bash
#SBATCH...
...
singularity exec...
<entity/project/sweepid> # e.g. socialiq/wandb_example/yb5sssqu
```

You should also edit the other inputs to `sbatch`, e.g. `--output`...etc. 

If you edited this script on your local machine, make sure to pull from your local to update your script on Atlas.
```
rsync -av awilf@taro:/work/awilf/wandb_example /work/awilf/
```

3. Start the sweep
Paste this command as many times as nodes as you'd like to parallelize across.  Good practice for Atlas is to cap it at 8 so we don't flood the cluster.
```
sbatch sweep.sbatch
sbatch sweep.sbatch
sbatch sweep.sbatch
...
```

Check out the link on your wandb page to watch the sweep in action. 

<!-- This last part is optional, but I built a little service to email me when the full sweep is finished. After you've submitted the above commands, modify `email_finished.sbatch` with the number of workers you provisioned as the argument to `email_checker.py`, then submit
```
sbatch email_finished.sbatch
```

You can also change the `mail-type` of `sweep.sbatch` so those don't email you anymore, just the final one. -->

### To Debug
Do (1) and (2) but then provision an interactive node via `srun`
```
srun -p gpu_low --gres=gpu:1 --mem=10GB --pty bash
```

Once inside, make it a `wandb agent` child process.
```
singularity exec -B /work/awilf/ --nv /results/awilf/imgs/tvqa_graph.sif \
wandb agent <str/from/above/here>
```


## Acknowledgments
This tutorial comes mostly from [wandb_on_slurm](https://github.com/elyall/wandb_on_slurm).  I've trimmed their tutorial significantly and added singularity exec invocations to the examples.
