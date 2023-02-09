import sys; sys.path.append('/work/awilf/utils/'); from alex_utils import *
import wandb

# TODO: import any packages you need here

def main():
    global args
    
    arg_defaults = [
        ('--_tags', str, 'debug'), # NOTE: required if you use deploy_sweeps. please do not remove the _. Use 'debug' if you don't want wandb to sync.
        
        ('--seed', int, 42),
        ('--wdb_project', str, ''), # defaults to chdir, but will be overwritten if called as part of a sweep
        ('--wdb_entity', str, 'socialiq'),

        ## TODO: add any other arguments you'd like
        ('--hp1', int, -1),
        ('--hp2', int, -1),
        ('--hp3', int, -1),
        ('--hp4', int, -1),
    ]
    
    # TODO (optional): if there are any features of the argparse parser you want to add, initialize and pass in your parser here.
    parser = None
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--model_type", type=str, required=True, help="The model architecture",)
    args = process_defaults(arg_defaults, parser_in=parser)
    
    # TODO: copy set_seed() from alex_utils into this file if you'd like to use it (b/c of dependencies)
    # set_seed(args.seed)

    if 'debug' not in args._tags:
        wandb.init(
            project=args.wdb_project,
            entity=args.wdb_entity, 
            config=vars(args),
            tags=args._tags.split(','),
        )

    # TODO: your training here
    perfs = []
    for i in range(10):
        perfs.append(random.random())
        if 'debug' not in args._tags:
            wandb.log({'train_loss': perfs[-1]})
    
    # TODO: have some summary metrics here
    if 'debug' not in args._tags:
        wandb.summary['valid_loss'] = random.random()

if __name__=='__main__':
    main()