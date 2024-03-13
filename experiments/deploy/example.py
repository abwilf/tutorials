import wandb
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--_tags", type=str, default="delete_test")
parser.add_argument("--arg1", type=int, default=0)
parser.add_argument("--arg2", type=int, default=0)
args = parser.parse_args()

wandb.init(
    project="delete_test",
    entity="awilf",
    tags=args._tags.split(',')
)

# Do stuff here
wandb.log({'accuracy': args.arg1+args.arg2})
