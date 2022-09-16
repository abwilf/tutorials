'''
## wdb.py ##
author: awilf

A common workflow when using wandb is to do the following:
1. Develop on taro, running little runs to test things
2. Create a grid search and deploy quickly to atlas

To do the first, I just need to create a debug flag and only wandb.init or wandb.log when I'm not debugging

To do the second, I need to:
1. Create / modify a config file to define the sweep
2. Create the sweep (e.g. wandb sweep config1.yml)
3. Create an sbatch file with the resulting `wandb agent socialiq/...` command
4. rsync everything over to atlas
5. Submit the sbatches on atlas
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
'''
import sys; sys.path.append('/work/awilf/utils/'); from alex_utils import *
import wandb
import yaml

os.environ['WANDB_AGENT_DISABLE_FLAPPING'] = 'true'
os.environ['WANDB_AGENT_MAX_INITIAL_FAILURES']='1000'

# TODO: need to do this occassionally if you want to clear out a lot of dev runs
# api = wandb.Api(overrides={"project": 'AANG', "entity": 'socialiq'})
# for run in api.runs():
#     if 'sweep' not in run.name:
#         run.delete()
        
defaults = [
    ('--out_dir', str, ''),
    ('--c', str, ''), # config path
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

def main(_gc):    
    global gc; gc=_gc
    assert gc['c'] != '', '--c must be set to config path'
    if gc['project'] == '':
        gc['project'] = os.getcwd().split('/')[-1]

    d = yaml.load(read_txt(gc['c']), Loader=yaml.Loader)
    
    print(f'\n## Processing Config {gc["c"]} ##')
    
    with Capturing() as output: # modify printing format
        sweep_id = wandb.sweep(d,entity=gc['entity'], project=gc['project'])
    # print(output[0]) # Create sweep with ID...
    print('Sweep URL and Atlas Command:')
    # print(output[1].strip().split(' ')[-1])
    sbatch = read_txt(gc['base_sb'])
    
    prefix = sbatch.split('wandb agent')[0]
    postfix = f'wandb agent {gc["entity"]}/{gc["project"]}/{sweep_id}'
    sbatch = f'{prefix}{postfix}'
    sbatch_file = gc['c'].replace('config', 'sweep').replace('.yml', '.sbatch')

    # print(f'\n# Writing sbatch file to {sbatch_file}')
    write_txt(sbatch_file, sbatch)

    # print(f'# Executing rsync command')
    os.popen(gc['rsa'])

    # print(f'\n## Run this Command on Atlas ##')
    print(f'sbatch {join(os.getcwd(), sbatch_file)}')
    # print(postfix)

    print(os.popen(f'cat {join(os.getcwd(), sbatch_file)} | tail -2').read().replace('\\', '').replace('\n', ''))
    print(output[1].strip().split(' ')[-1])

    

if __name__ == '__main__':
    main_wrapper(main, defaults, results=False, runtime=False)
