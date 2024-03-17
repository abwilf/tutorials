'''
Deploy Sweeps, v2.0
by Alex Wilf

R:
- this script (deploy/deploy_sweeps.py)
- sbatch file(s) (e.g., deploy/atlas.sbatch): the important thing is that it has "wandb agent" in it -- this script will add wandb agent <sweep_id> and a ' to the end.
- A config yml (e.g. deploy/example.yml)
- A program (e.g., example.py) -- note: will usually be outside of deploy, just here for example

M/E:
1. Create sweep(s) from config
2. Sync to server(s)
3. Write sweeps to sbatch files
4. Print all this information to the console and deploy/tower.txt so you can just enter the sbatch commands

Todo: modify the todo in the below, modify base atlas and babel files
To run:
p deploy/deploy_sweeps.py example
'''

###### TODO: modify the below, as well as the base atlas and babel sbatch files ######
sweep_params = {
    'entity': 'socialiq',
    'project': 'codesim',
}
sbatch_files = {
    'atlas': './deploy/atlas.sbatch',
    'babel': './deploy/babel.sbatch'
}
data_paths = {
    'atlas': '/work',
    'babel': '/home',
}
rsync_cmd = '''
rsync -av /work/awilf/tutorials/experiments awilf@{server}:{data_path}/awilf/tutorials
rsync -av /work/awilf/anaconda3/envs/example_env awilf@{server}:{data_path}/awilf/anaconda3/envs
'''
output_file='./deploy/tower.txt' # where std output is written

##################################################

import argparse, wandb, yaml, subprocess, os, sys, copy, itertools, time, sys, threading, hashlib
from io import StringIO
from datetime import datetime

## Setup
os.environ['WANDB_AGENT_DISABLE_FLAPPING'] = 'true'
os.environ['WANDB_AGENT_MAX_INITIAL_FAILURES'] = '1000'
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

all_output = ''
def printo(to_print):
    print(to_print)
    global all_output
    all_output += to_print + '\n'

## Args
parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="config file yaml - will autocomplete if you forget the .yml extension. Expected to be in deploy/")
parser.add_argument("server", type=str, choices=['babel', 'atlas', 'babel,atlas', 'atlas,babel'], nargs='?', default='babel,atlas', 
        help='which server to sync with: supported servers are "atlas" and "babel", and both separated by commas')
args = parser.parse_args()

## Load and process the yml: get multiple ymls
if not args.config.endswith(".yml"):
    args.config += ".yml"

with open('deploy/' + args.config, 'r') as file:
    full_yml = yaml.safe_load(file)

all_ymls = []

base_yml = copy.deepcopy(full_yml)
del base_yml['parameters']['subtests']
if 'subtests' in full_yml['parameters']:
    for subtest in full_yml['parameters']['subtests']:
        yml = copy.deepcopy(base_yml)
        yml['parameters'] = {
            **base_yml['parameters'], 
            **full_yml['parameters']['subtests'][subtest],
            '_tags': subtest
        }
        yml['parameters'] = {k: ({'values': v} if isinstance(v, list) else {'value': v}) for k,v in yml['parameters'].items()}
        all_ymls.append(yml)
else:
    all_ymls.append(base_yml)

## Get sweeps
sweeps = []
for yml in all_ymls:
    # come up with two time based tags: one word, one hash
    current_time = datetime.now()
    time_tag_word = current_time.strftime("%b_%d")
    time_tag_hash = hashlib.sha256(current_time.strftime("%Y-%m-%d %H:%M:%S").encode('utf-8')).hexdigest()[:4]
    name = f"{args.config.replace('.yml', '').replace('.yaml', '')}_{time_tag_word}_{yml['parameters']['_tags']['value']}_{time_tag_hash}"

    with Capturing() as output: # modify printing format
        sweep_id = wandb.sweep({**yml, 'name': name}, **sweep_params)
    sweep_url = output[-1].strip().split(' ')[-1] # sweep url    

    sweeps.append({
        'sweep_id': sweep_id,
        'sweep_url': sweep_url,
        'name': name,
        'agent_cmd': f"wandb agent {sweep_params['entity']}/{sweep_params['project']}/{sweep_id}"
    })

## Write sweeps to sbatch files
servers = args.server.split(',')
all_sbatches = {}
for server in servers:
    all_sbatches[server] = []
    for sweep in sweeps:
        sweep_id = sweep['sweep_id']
        with open(sbatch_files[server], 'r') as sbatch_file:
            sbatch = sbatch_file.read()
        pre, _ = sbatch.split('wandb agent')
        sbatch = f"{pre}{sweep['agent_cmd']}'\n"
        sbatch_name = os.path.realpath(f"deploy/sbatches/{sweep['name']}_{server}.sbatch")
        with open(sbatch_name, 'w') as sbatch_file:
            sbatch_file.write(sbatch)
        all_sbatches[server].append(sbatch_name.replace('/work', data_paths[server]))

## Print information
printo(f"--- Agent Commands ---")
for sweep in sweeps:
    printo(f"{sweep['agent_cmd']}")

printo(f"\n--- Sweep URLs ---")
for sweep in sweeps:
    printo(sweep['sweep_url'])

for server in servers:
    printo(f"\n--- {server} ---")
    
    for sbatch_name in all_sbatches[server]:
        printo(f"sbatch {sbatch_name}")

def print_sync_status(server, done_event):
    spinner = itertools.cycle(['-', '\\', '|', '/'])  # simple spinner
    while not done_event.is_set():
        sys.stdout.write('\rSyncing to ' + server + ' ' + next(spinner))  # print next spinner frame
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rSyncing to ' + server + ' ' + '\033[92m' + '✓' + '\033[0m\n')  # print green check mark

## Write to tower file
print(f'\nWriting to {output_file}...')
with open(output_file, 'w') as file:
    file.write(all_output)

## Sync to servers
print(f'\n--- Syncing to {", ".join(servers)}... ---')
for server in servers:
    done_event = threading.Event()
    threading.Thread(target=print_sync_status, args=(server, done_event)).start()

    # TODO: remove
    print(rsync_cmd.format(server=server, data_path=data_paths[server]))

    result = subprocess.run(rsync_cmd.format(server=server, data_path=data_paths[server]), shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        printo("rsync Command failed!\n", result.stderr.decode())

    done_event.set()  # Signal that work is done

time.sleep(.5)

