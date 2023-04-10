#! /usr/bin/python3

'''
This script supports both arm and arm64 architectures.
Dependencies:
- GitPython (https://gitpython.readthedocs.io/en/stable/intro.html) - python3 -m pip install
- Colorit (https://gitpython.readthedocs.io/en/stable/intro.html)

This script should run inside a valid Linux git (like the linux-toradex)

How to use:

tdx_find_in_dt.py text_file.dts search_string

The script will search for the search_string inside the text_file.dts and inside all the files included by this file recursively.

A file inclusion looks like this:
#include <dt-bindings/gpio/gpio.h>

or
#include "imx6dl.dtsi"

'''
import sys
import re
import warnings
from pathlib import Path
from typing import List, Union

from colorit import *
from git import Repo, InvalidGitRepositoryError


class MyRepository:
    def __init__(self, repo: Repo, arch: str = 'arm'):
        self._arch = arch
        self._repo = repo

    def arch(self):
        return self._arch

    def active_branch(self):
        return self._repo.active_branch


class SearchHit:
    def __init__(self, file_name: Path):  # , line_number:int, before_hit:str, hit:str, after_hit:str):
        self.file_name = file_name
        self.line_number = []
        self.before_hit = []
        self.hit = []
        self.after_hit = []
        self.hit_start = []
        self.hit_end = []

    def to_dict(self):
        return {'file_name': self.file_name,
                'hits': {line_number: [before, hit, after, hit_start, hit_end]
                         for line_number, before, hit, after, hit_start, hit_end
                         in
                         zip(self.line_number, self.before_hit, self.hit, self.after_hit, self.hit_start, self.hit_end)}
                }

    def append(self, line_number: int, before_hit: str, hit: str, after_hit: str, hit_start: int, hit_end: int):
        self.line_number.append(line_number)
        self.before_hit.append(before_hit)
        self.hit.append(hit)
        self.after_hit.append(after_hit)
        self.hit_start.append(hit_start)
        self.hit_end.append(hit_end)


def get_all_includes(dts_file_path, include_dir, dts_path):
    if not include_dir.exists() or not include_dir.is_dir():
        raise LookupError(f'Include directory {include_dir} doesn\'t exist or isn\'t a file!')

    dts_file_path = dts_file_path.resolve()
    dts_folder = dts_file_path.parent

    device_tree_content = None

    if dts_file_path.exists() and dts_file_path.is_file():
        with open(dts_file_path) as dt:
            device_tree_content = dt.read()
    else:
        raise LookupError(f'Device Tree file {dts_file_path} doesn\'t exist or isn\'t a file!')

    dts_path_list = []
    dts_file_list = []
    include_path_list = []
    include_file_list = []

    for f in re.findall('#include [<"](.+)[>"]', device_tree_content):
        if f[-1] == 'h':
            if not f in include_file_list:
                include_file_list.append(f)
                # search = re.search("pinfunc", f, re.IGNORECASE)
                # if search: # pinfunc headers are within the same folder as dts files
                #    include_path_list.append(dts_path / f)
                # else: # non pinfunc are in linux-kernel/include/dt-bindings
                #    include_path_list.append(include_dir / f)
                if (include_dir / f).exists():
                    include_path_list.append(include_dir / f)
                elif (dts_path / f).exists():
                    include_path_list.append(dts_path / f)
                elif dts_folder != include_dir and dts_folder != dts_path and (dts_folder / f).exists():
                    include_path_list.append(dts_folder / f)
                else:
                    raise LookupError()

        else:
            if not f in dts_file_list:
                dts_file_list.append(f)
                dts_path_list.append(dts_path / f)

    return dts_path_list, include_path_list


def get_repository(file: Path) -> Union[Repo, None]:
    '''

    :param file: path to a file or folder inside a git repository
    :type file: Path
    :return: a git repository object
    :rtype: Union[Repo, None]
    '''

    if file.is_file():
        path = file.parent.resolve()
    else:
        path = file.resolve()

    git:Union[Repo, None] = None

    while git == None:
        try:
            git = Repo(path)
        except InvalidGitRepositoryError:
            if str(path) == '/':
                warnings.warn(f'This {"file" if file.is_file() else "directory"} {path} does not belong to a Git repository.', UserWarning)
                break
            path = path.parent

    return git


def get_architecture(dts_file_path: Path):
    arch = ''
    search = re.search(r'arch/([\w\d]+)', str(dts_file_path))
    if search:
        arch = search.group(1)
    else:
        raise LookupError(
            f'\nYou are in {dts_file_path}, which doesn\'t define an architecture. Please cd into a dts folder.')

    return arch


def find_in_dt(dts_file_path: Path, search_string_list: List[str], search_in='all',
               returning='all'):  # -> tuple[MyRepository, List[SearchHit]]:
    '''

    :param dts_file_path: path to the device tree source (.dts) file
    :type dts_file_path: Path
    :param search_string_list: list of strings to search for
    :type search_string_list: List[str]
    :param search_in: where to search in. 'all' for everywhere, 'headers' t search only amongst headers, 'dts' to search only amonst dts and dtsi files
    :type search_in: str
    :param returning: what to be returned. 'all' to return everything (list of files and list of hits),  'only_matches' to return only the search hits and no file list, 'only_files' to return only the path to the files involved in given device tree (this option disregars the search_in option and disables the search)
    :type returning: str
    :return: depends on search_in and returning arguments, but can have list of SearchHits and list of all files involved in given device tree
    :rtype: Tuple[List[SearchHit], List[Path]]
    '''

    if not search_in in ["all", "only_headers", "only_dts"]:
        raise ValueError(f'ERROR: search_in should be "all", "only_headers", or "only_dts". Got "{search_in}" instead.')

    if not returning in ["all", "only_matches", "only_files"]:
        raise ValueError(
            f'ERROR: returning should be "all", "only_matches", or "only_files". Got "{returning}" instead.')

    linux_git = None

    if not dts_file_path.is_absolute():
        dts_file_path = dts_file_path.absolute()

    if not dts_file_path.exists():
        raise LookupError(f'File {dts_file_path} doesn\'t exists!')

    try:
        linux_git = get_repository(dts_file_path)
    except LookupError as e:
        raise e

    dts_folder = dts_file_path.parent

    try:
        arch = get_architecture(dts_file_path)
    except LookupError as e:
        raise e

    if not dts_file_path.exists():
        raise LookupError(f'device tree file does not exits: {dts_file_path}')

    repo = MyRepository(linux_git, arch)
    try:
        repo.active_branch()
    except TypeError as e:
        print('active git branch:', color("no branch found", Colors.red), '\n')
    except Exception as e:
        raise e

    include_dir = Path(linux_git.working_dir) / 'include'
    try:
        more_dts, more_headers = get_all_includes(dts_file_path, include_dir, dts_folder)
    except LookupError as e:
        raise e

    all_dts = more_dts
    all_headers = more_headers

    for dts in all_dts:
        dts_s, include_s = get_all_includes(dts, include_dir, dts_folder)
        for d in dts_s:
            if d not in all_dts:
                all_dts.append(d)
        for i in include_s:
            if i not in all_headers:
                all_headers.append(i)

    for header in all_headers:
        dts_s, include_s = get_all_includes(header, include_dir, dts_folder)
        for d in dts_s:
            if d not in all_dts:
                all_dts.append(d)
        for i in include_s:
            if i not in all_headers:
                all_headers.append(i)

    all_dts.append(dts_file_path)

    finds: List[SearchHit] = []

    all_files: List[Path] = [*all_headers, *all_dts]

    if search_in == 'only_headers':
        search_in_files:List[Path] = all_headers
    elif search_in == 'only_dts':
        search_in_files:List[Path] = all_dts
    elif search_in == 'all':
        search_in_files:List[Path] = all_files
    else:
        search_in_files:List[Path] = []

    if not returning == 'only_files':
        for file in search_in_files:
            with open(file) as f:
                content_lines = f.readlines()

                new_search_hit = SearchHit(file)
                something_found = False
                character_sum = 0
                for line_number, line_text in enumerate(content_lines):
                    for ss in search_string_list:
                        # TODO: findall aqui? achar mais de uma vez a mesma coisa na mesma linha?!
                        search = re.search(ss, line_text, re.IGNORECASE)
                        if search:
                            something_found = True
                            span = search.span()
                            new_search_hit.append(line_number + 1, line_text[0:span[0]], line_text[span[0]:span[1]],
                                                  line_text[span[1]:].rstrip(), character_sum + span[0],
                                                  character_sum + span[1])
                    character_sum += len(line_text)
                if something_found:
                    finds.append(new_search_hit)

    if returning == 'only_matches':
        search_in_files:List[Path] = []

    return finds, search_in_files


if __name__ == '__main__':

    print(Path.cwd())

    dt_file = sys.argv[1]  # 'imx6dl-colibri-eval-v3.dts'
    search_string_list = sys.argv[2:]  # ['gpio2', 'MX6QDL_PAD_SD1_DAT']

    #search_in = ['only_headers', 'only_dts', 'all']
    #returning = ['only_files', 'only_matches', 'all']
    search_in = ['all']
    returning = ['all']

    for si in search_in:
        for ret in returning:

            print(color(f'search_in: {si}, returning: {ret}', Colors.yellow))

            finds, searched_files = find_in_dt(Path(dt_file), search_string_list, search_in=si, returning=ret)

            print('searching in:')
            for file in searched_files:
                print('\t{}/{}'.format(file.parents[0], color(file.name, Colors.green)))

            print('findings:')

            for f in finds:
                print(color(f.file_name, Colors.purple))
                for line, [before, hit, after, hit_start, hit_end] in f.to_dict()['hits'].items():
                    print('\t', color(line, Colors.red), ' : ', before, color(hit, Colors.green), after, sep='')
                print()

            print(color(f'search_in: {si}, returning: {ret}', Colors.yellow))
            print('-'*100)

# for file in [*dts_path_list, *include_file_list]:
#    with open(file) as f:

# property and value (has some dirty when multiple lines)
# (\S+)\s?=\s?([\s\S]+?);

# nodes
# (?:(\S+)\s?:\s?)?(\S+)\s+?\{
