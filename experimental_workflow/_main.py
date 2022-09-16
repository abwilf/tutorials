import sys; sys.path.append('/work/awilf/utils/'); from alex_utils import *
import wandb
# from args import defaults
defaults = [
    ("--out_dir", str, "results/hash1"), # REQUIRED - results will go here
    ("--rationale", float, 1.2), # other arguments
    ('--debug', int, 0),
]

def main(_gc):
    global gc; gc = _gc

    wandb.init(
        project=None, 
        entity=None,
        config=gc,
    )

    # ... do whatever ...
    for epoch in training:
        wandb.log({'loss': random()})

    wandb.summary['test_acc'] = 10

if __name__ == '__main__':
    main_wrapper(main,defaults,return_results=False)


