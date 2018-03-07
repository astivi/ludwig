import os
import sys

from git import RemoteProgress, Repo
from yaml import Dumper, Loader, dump, load


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')


Dumper.add_representer(type(None), represent_none)

composed = {
    'version': '3',
    'services': dict(),
    'volumes': dict(),
    'networks': dict(),
}


class ProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(f"\rProgress: {(cur_count / (max_count or 100.0))*100:4.4}%     ", end='', flush=True)


def git_clone(git_repo: str, dir_name: str) -> None:
    if not os.path.exists(dir_name):
        print(f'Cloning {git_repo}#master into {dir_name}...', flush=True)
        repo = Repo(os.path.curdir)
        repo.clone_from(git_repo, dir_name, branch='master', progress=ProgressPrinter())
        print('', flush=True)
    else:
        print(f'{dir_name} already exists, skipping...', flush=True)


def load_yml_file(file_name: str) -> dict:
    return load(open(file_name, 'r'), Loader=Loader)


def save_yml_file(file_name: str, contents: dict) -> None:
    dump(contents, open(file_name, 'w'), Dumper=Dumper, default_flow_style=False)


def create_directory(dir_name: str) -> None:
    if not os.path.exists(dir_name):
        print(f'Creating directory {dir_name}...', flush=True)
        os.makedirs(dir_name)


def get_current_dir(entry_name: str, acc: list) -> str:
    return f'{"/".join(acc)}{"/" if acc else ""}{entry_name}'


def normalize_context_paths(docker_compose: dict, path: str):
    for service in docker_compose['services']:
        if 'build' in docker_compose['services'][service]:
            build = docker_compose['services'][service]['build']
            if type(build) is str:
                docker_compose['services'][service]['build'] = path;
            else:
                docker_compose['services'][service]['build']['context'] = path;


def merge_docker_compose(path: str):
    if os.path.exists(f"{path}/docker-compose.yml"):
        print(f'Merging {path} contents...')
        docker_compose = load_yml_file(f"{path}/docker-compose.yml")
        normalize_context_paths(docker_compose, path)
        for key in ['services', 'volumes', 'networks']:
            if key in docker_compose:
                composed[key].update(docker_compose[key])
    else:
        print(f'Compose file not found at {path}, skipping...')


def handle_entry(data: dict, entry_name: str, acc: list) -> None:
    current_dir = get_current_dir(entry_name, acc)
    current_dict = data[entry_name]
    create_directory(current_dir)
    for value in current_dict:
        if type(current_dict[value]) is str:
            git_clone(current_dict[value], f'{current_dir}/{value}')
            merge_docker_compose(f'{current_dir}/{value}')
        else:
            handle_entry(current_dict, value, acc + [entry_name])


print("""
            _           _          _
           | |_   _  __| |_      _(_) __ _
           | | | | |/ _` \ \ /\ / / |/ _` |
           | | |_| | (_| |\ V  V /| | (_| |
           |_|\__,_|\__,_| \_/\_/ |_|\__, |
                                     |___/ 
""")

if len(sys.argv) != 2:
    print('Usage: python ludwig.py {filename}')
else:
    parsed_yml = load_yml_file(sys.argv[1])
    for values in parsed_yml:
        handle_entry(parsed_yml, values, [])

    save_yml_file('docker-compose.yml', composed)
