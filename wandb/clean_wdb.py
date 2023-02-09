import sys; sys.path.append('/work/awilf/utils/'); from alex_utils import *
import wandb

# TODO: need to do this occassionally
api = wandb.Api(overrides={"project": 'wandb2', "entity": 'socialiq'})
for run in tqdm(api.runs()):
    # if 'sample_reg' in run.tags or 'debug' in run.tags:
    if True:
        run.delete()
exit()