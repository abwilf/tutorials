'''
## wdb.py ##
author: awilf

A common workflow when using wandb is to do the following:
1. Develop on taro, running little runs to test things
2. Create a grid search and deploy quickly to atlas

To do this, we need to: 
1. Create / modify a config file to define the sweep
2. Create the sweep (e.g. wandb sweep config1.yml)
3. Create an sbatch file with the resulting `wandb agent socialiq/...` command
4. rsync everything over to atlas
5. Submit the sbatches on atlas, however many we want to parallelize across
6. Note the url that defines the sweep, check it to make sure it's working

This script automates this process.  Here is the RME.

R:
    c: the config file
        A wandb sweep config file of form {config_name}.yml.
    base_sb: the "base sbatch" file
        This should be a complete sbatch file (i.e. with a wandb agent line at the bottom).  
        It doesn't matter if the wandb command is correct (i.e. the right entity and project name).  It will be overwritten.

    entity: wandb entity
    project: wandb project name, or defaults to current dir name
    rsa: rsync command (I would recommend modifying this file instead of passing this in so you can do things like os.cwd())
M/E:
    Creates and prints sweep id and url
    Writes resulting sweep sbatch file in {config_name}.sbatch
    Runs rsync command
    Prints the command to deploy on atlas


One extra functionality: I like running many experiments with a single config, where sometimes the parameters aren't always shared.
For example, imagine I wanted to run 
    "experiment1" which uses hyperparameters (a: [1,2], b: [3,4], c: [5], d: [6]) and 
    "experiment2": (a: [8,9,10], b:[11], c: [5], d: [6])
I would have to create two different yaml files.  This gets annoying if you're trying many different experiments with different hyperparameter searches.
Ideally, we'd like to be able to incorporate these "subtests" into a single yaml file and create multiple sweeps, one for each subtest, with some shared and some
unshared parameters.

I've implemented this as well; in the "parameters" section, if you have a subsection called "subtests", I'll create new yaml's for each of the subtests 
(along with the rest of the shared parameters) and fill in the "tags" parameter with the name of the subtest.

e.g. if you have your wandb init set up like this:
wandb.init(
    project=...,
    entity=...,
    config=...
    tags=args.tags.split(','),
)

Then you can formulate your yaml as this (the full yaml is in composite.yml)

parameters:
  subtests:
    rw_sig1,rw_sig2: # this will be the tags; separate with commas for multiple tags applied to this run
      rw_strat: # these are all the unshared hyperparams
        value: sig1
      rw_init_prim:
        values:
        - -1
        - 0
        - 1
      rw_init_aux:
        values:
        - -1
        - 0
    baseline: # this is the tag of the second test, with different parameters it's searching over
      gradient_accumulation_steps:
        values:
        - 5
      unroll_steps:
        values:
        - 1

  # the rest of the shared parameters go here like normal: each of the subtests above will inherit these params for its test
  prim-task-id:
    value: citation_intent
  train_data_file:
    value: datasets/citation_intent/train.jsonl

after running p wdb.py --c composite.yml, two sbatch files will be written corresponding to different sweeps. You can deploy each of these,
then in the wandb dashboard filter on tags.
    composite_rw_sig1,rw_sig2.sbatch
    composite_baseline.sbatch
'''
import sys; sys.path.append('/work/awilf/utils/'); from alex_utils import *
import wandb
import yaml

os.environ['WANDB_AGENT_DISABLE_FLAPPING'] = 'true'
os.environ['WANDB_AGENT_MAX_INITIAL_FAILURES']='1000'
        
defaults = [
    ('--out_dir', str, ''),
    ('--c', str, 'comp_test1.yml'), # config path
    ('--v', int, 0), # verbosity: if 0, will only print sweep links and sbatch commands; if 1, will print singularity commands too
    ('--base_sb', str, 'base.sbatch'), # base sbatch path: this program will use this and replace the wandb agent line
    ('--entity', str, 'socialiq'), # wandb entity
    ('--project', str, 'AANG'), # project name, if nothing defaults to name of cwd()
    ('--rsa', str, f'''\
    rsync -av \
    --exclude wandb \
    --exclude autoaux_outputs \
    --exclude .git \
    --exclude __pycache__ \
    {os.getcwd()} \
    awilf@atlas:/work/awilf/ \
    && \
    rsync -av \
    /work/awilf/utils/alex_utils.py \
    awilf@atlas:/work/awilf/utils \
    '''
    ),
]
def create_sweep(this_yml, tags):
    tags = f'_{tags}' if tags != '' else ''
    with Capturing() as output: # modify printing format
        sweep_id = wandb.sweep(this_yml, entity=gc['entity'], project=gc['project'])
    
    if gc['v']:
        print(f'\n\n{output[0]}') # Create sweep with ID...
        print('Sweep URL and Atlas Command:')
    sweep_url = output[1].strip().split(' ')[-1] # sweep url
    print(sweep_url)

    # Modify sbatch
    sbatch = read_txt(gc['base_sb'])
    prefix = sbatch.split('wandb agent')[0]
    postfix = f'wandb agent {gc["entity"]}/{gc["project"]}/{sweep_id}'
    sbatch = f'{prefix}{postfix}'
    sbatch_file = f"{gc['c'].replace('.yml', '').replace('.yaml', '')}{tags}.sbatch"

    if gc['v']:
        print(f'Writing sbatch file to {sbatch_file}')
    write_txt(sbatch_file, sbatch)

    print(f'sbatch {join(os.getcwd(), sbatch_file)}')

    if gc['v']:
        print(os.popen(f'cat {join(os.getcwd(), sbatch_file)} | tail -2').read().replace('\\', '').replace('\n', ''))

def main(_gc):    
    global gc; gc=_gc
    assert gc['c'] != '', '--c must be set to config path'
    if gc['project'] == '':
        gc['project'] = os.getcwd().split('/')[-1]

    d = yaml.load(read_txt(gc['c']), Loader=yaml.Loader)

    if 'parameters' in d and 'subtests' in d['parameters']:
        if gc['v']:
            print('This is a composite sweep!\n')
        
        # write new yamls with same name but append _<tagname>, _<tagname>...etc
        base_obj = copy.deepcopy(d)
        del base_obj['parameters']['subtests']

        for tags,v in d['parameters']['subtests'].items():
            this_yml = copy.deepcopy(base_obj)
            this_yml['parameters'] = {
                'tags': {'value': tags},
                **this_yml['parameters'],
                **v,
            }

            create_sweep(this_yml, tags)

    else:
        create_sweep(d, '')

    if gc['v']:
        print(f'\nExecuting rsync command')
    os.popen(gc['rsa'])


if __name__ == '__main__':
    main_wrapper(main, defaults, results=False, runtime=False)
