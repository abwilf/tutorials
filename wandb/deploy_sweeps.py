'''
## wdb.py ##
author: awilf

R:
    see arg_defaults below

M/E:
    1. Creates and prints sweep id and url
    2. Writes resulting sweep sbatch file in {config_name}.sbatch
    3. Runs rsync command
    4. Prints the command to deploy on atlas
'''

import sys; sys.path.append('/work/awilf/utils/'); from alex_utils import *
import wandb, yaml

os.environ['WANDB_AGENT_DISABLE_FLAPPING'] = 'true'
os.environ['WANDB_AGENT_MAX_INITIAL_FAILURES']='1000'
        
arg_defaults = [
    ('--c', str, 'gpt_gh.yml'), # config path describing grid search
    ('--test_time', float, 1), # how many hours does each run take? 1 is default
    ('--v', int, 0), # verbosity: if 0, will only print sweep links and sbatch commands; if 1, will print singularity commands too
    ('--base_sb', str, 'base.sbatch'), # base sbatch path: this program will use this and replace the wandb agent line
    ('--entity', str, 'socialiq'), # TODO: change wandb entity name.
    ('--project', str, ''), # TODO: change wandb project name, if nothing defaults to name of cwd()
    ('--singularity_prefix', str, srep('''\
    export WANDB_API_KEY=239e23a9f93922a29983e91684b0a026946715f0 && \
    export TRANSFORMERS_CACHE='/work/awilf/.cache/transformers_cache' && \
    export HF_HOME='/work/awilf/.cache/hf_home' && \
    export XDG_CACHE_HOME='/work/awilf/.cache/xdg_cache' && \
    singularity exec --nv -B /work/awilf/ rlhf.sif''')),
    
    # TODO: if you're planning to deploy your tests on atlas, you'll want to add a line here that syncs your updated code, data, 
    # and maybe dependencies over to atlas every time you initiate a new test e.g.
    # rsync -av /work/awilf/anaconda3/envs/gpt awilf@atlas:/work/awilf/anaconda3/envs
    ('--rsa', str, f'''\
    rsync -av --exclude wandb --exclude models --exclude .git --exclude __pycache__ {os.getcwd()} awilf@atlas:/work/awilf/ && rsync -av /work/awilf/utils/alex_utils.py awilf@atlas:/work/awilf/utils
    '''
    ),
]
def create_sweep(this_yml, tags, trial):
    tags = f'_{tags}' if tags != '' else ''
    
    # add "value" and "values" as required by wandb
    def get_v(v):
        if isinstance(v, list):
            return {'values': v} 
        elif isinstance(v, dict):
            return v
        else: # single element
            return {'value': v}

    this_yml['parameters'] = {k: get_v(v) for k,v in this_yml['parameters'].items()}
    args['num_runs'] += np.product(list({k: 1 if 'value' in v else len(v['values']) for k,v in this_yml['parameters'].items()}.values())) * args['num_trials']

    with Capturing() as output: # modify printing format
        sweep_id = wandb.sweep(this_yml, entity=args['entity'], project=args['project'])
    
    if args['v']:
        print(f'\n\n{output[0]}') # Create sweep with ID...
        print('Sweep URL and Atlas Command:')
    sweep_url = output[1].strip().split(' ')[-1] # sweep url
    args['sweep_urls'].append(sweep_url)

    # Modify sbatch
    sbatch = read_txt(args['base_sb'])
    prefix = sbatch.split('wandb agent')[0]
    postfix = f'wandb agent {args["entity"]}/{args["project"]}/{sweep_id}'
    sbatch = f'{prefix}{postfix}'
    sbatch_file = f"{args['c'].replace('.yml', '').replace('.yaml', '')}{tags}_{trial}.sbatch"
    args['postfixes'].append(postfix)

    if args['v']:
        print(f'Writing sbatch file to {sbatch_file}')
    write_txt(sbatch_file, sbatch)

    args['sbatch_commands'].append(f'sbatch {join(os.getcwd(), sbatch_file)}')

    if args['v']:
        print(os.popen(f'cat {join(os.getcwd(), sbatch_file)} | tail -2').read().replace('\\', '').replace('\n', ''))

def main():    
    global args
    args = vars(process_defaults(arg_defaults, parser_in=None))
    assert args['c'] != '', '--c must be set to config path'
    
    # so I can lazy tab complete my test name and even when it stalls out b/c of .yml/.batch I don't have t otype .yml
    args['c'] = f"{args['c']}.yml" if '.' not in args['c'] else args['c']

    if args['project'] == '':
        args['project'] = os.getcwd().split('/')[-1]

    d = yaml.load(read_txt(args['c']), Loader=yaml.Loader)

    args['postfixes'] = []
    if args['v']:
        print(f'\nExecuting rsync command')
    os.popen(args['rsa'])

    args = {
        **args,
        'sweep_urls': [],
        'sbatch_commands': [],
        'num_nodes': [], # how many times to print out each command; if not included = 1
        'num_runs': 0
    }
    
    assert 'parameters' in d and 'subtests' in d['parameters'], 'The yaml must contain parameters and subtests underneath'

    if args['v']:
        print('This is a composite sweep!\n')

    # write new yamls with same name but append _<tagname>, _<tagname>...etc
    base_obj = copy.deepcopy(d)
    del base_obj['parameters']['subtests']

    for tags,v in d['parameters']['subtests'].items():
        this_yml = copy.deepcopy(base_obj)
        this_yml['parameters'] = {
            **this_yml['parameters'],
            **v,
            '_tags': {'value': tags},
        }
        this_yml['name'] = tags
        
        if '_num_trials' in this_yml['parameters']:
            args['num_trials'] = this_yml['parameters']['_num_trials']
            del this_yml['parameters']['_num_trials']
        else:
            args['num_trials'] =  1
            
        for trial in range(args['num_trials']):
            if '_num_nodes' in this_yml['parameters']:
                args['num_nodes'].append(this_yml['parameters']['_num_nodes'])
                del this_yml['parameters']['_num_nodes']
            else:
                args['num_nodes'].append(1)

            create_sweep(this_yml, tags, trial)
    
    print('num runs:', args['num_runs'])
    if args['test_time'] != -1:
        print('total gpu hours:', int(args['num_runs']*args['test_time']))
    
    print('\n'.join(args['sweep_urls']),'\n')
    for sbatch_command, num_nodes in zip(args['sbatch_commands'], args['num_nodes']):
        for _ in range(num_nodes):
            print(sbatch_command)

    if args['v']:
        print(f'\nExecuting rsync command')
    os.popen(args['rsa'])

    print('\n'.join(lmap(lambda elt: f"{args['singularity_prefix']} {elt}", args['postfixes'])))

if __name__ == '__main__':
    main()
