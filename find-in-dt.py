#! /bin/python3

'''
This script supports both arm and arm64 architectures.

This script should run inside a valid Linux git (like the linux-toradex)

How to use:

tdx_find_in_dt.py text_file.dts search_string

The script will search for the search_string inside the text_file.dts and inside all the files included by this file recursively.

A file inclusion looks like this:
#include <dt-bindings/gpio/gpio.h>

or
#include "imx6dl.dtsi"

'''

#TODO: get dt-bindings includes from kernel/include/dt-bindings regardless of using "" or <> for these includes
import os
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
import re
from colorit import *
import sys

def get_all_includes(device_tree_filename, include_dir):

    device_tree_path = (device_tree_filename).resolve()

    device_tree_content = None

    if device_tree_path.exists() and device_tree_path.is_file():
        with open(device_tree_path) as dt:
            device_tree_content = dt.read()

    dts_path_list = []
    dts_file_list = []
    include_path_list = []
    include_file_list = []

    for f in re.findall('#include [<"](.+)[>"]', device_tree_content):
        if f[-1] == 'h':
            if not f in include_file_list:
                include_file_list.append(f)
                search = re.search("pinfunc", f, re.IGNORECASE)
                if search: # pinfunc headers are within the same folder as dts files
                    include_path_list.append(dts_path / f)
                else: # non pinfunc are in linux-kernel/include/dt-bindings
                    include_path_list.append(include_dir / f)

        else:
            if not f in dts_file_list:
                dts_file_list.append(f)
                dts_path_list.append(dts_path / f)


    #for include_filename, include_path in zip(include_file_list, include_path_list):
    #    print(include_filename, ' : ', include_path)

    #for f in re.findall('#include <(.+)>', device_tree_content):
    #    if f[-1] == 'h':
    #        if not f in include_file_list:
    #            include_file_list.append(f)
    #            include_path_list.append(include_dir / f)
    #    else:
    #        if not f in dts_file_list:
    #            dts_file_list.append(f)
    #            dts_path_list.append(include_dir / f)

    #for dt_filename, dt_path in zip(dts_file_list, dts_path_list):
    #    print(dt_filename, ' : ', dt_path)
    
    return dts_path_list, include_path_list

if __name__ == '__main__':

    linux_git_path = Path.cwd()

    arch = ''

    search = re.search(r'arch/([\w\d]+)',str(linux_git_path))
    if search:
        arch = search.group(1)
    else:
        print(f'\nYou are in {linux_git_path}, which doesn\'t define an architecture. Please cd into one of architecture folders.')
        exit(0);

    linux_toradex_git = None

    try:
        linux_toradex_git = Repo(linux_git_path)
        print('git at:',linux_git_path)
    except InvalidGitRepositoryError:
        try_level_above = True
        while try_level_above:
            linux_git_path = linux_git_path.parent
            try:
                linux_toradex_git = Repo(linux_git_path)
                try_level_above = False
                linux_git_path = linux_git_path.resolve()
                print('git found at:',linux_git_path.resolve())
            except InvalidGitRepositoryError:
                try_level_above = True
        
    include_dir = linux_git_path / 'include'
    dts_path = linux_git_path / 'arch' / arch / 'boot' / 'dts'

    if arch == 'arm64':
        dts_path = dts_path / 'freescale'

    active_branch = linux_toradex_git.active_branch

    print('active git branch:',color(active_branch, Colors.red), '\n')

    all_dts = []
    all_includes = []

    dt_end = sys.argv[1] # 'imx6dl-colibri-eval-v3.dts'
    dt_filepath = dts_path / dt_end

    if not dt_filepath.exists():
        print('device tree file does not exits:', dt_filepath)
        exit(0)

    search_string_list = sys.argv[2:] # ['gpio2', 'MX6QDL_PAD_SD1_DAT']

    try:
        more_dts, more_includes = get_all_includes(dt_filepath, include_dir)
    except:
        print('Error!')
        exit(0)

    all_dts = more_dts
    all_includes = more_includes

    for dts in all_dts:
        dts_s, include_s = get_all_includes(dts, include_dir)
        for d in dts_s:
            if d not in all_dts:
                all_dts.append(d)
        for i in include_s:
            if i not in all_includes:
                all_includes.append(i)

    all_dts.append(dt_filepath)

    print('searching in:')
    for file in [*all_dts, *all_includes]:
        print('\t{}/{}'.format(file.parents[0],color(file.name,Colors.green)))

    print()

    finds = {}
    for file in [*all_dts, *all_includes]:
        with open(file) as f:
            content_lines = f.readlines()
            
            finds[file] = []
            for idx, line in enumerate(content_lines):
                for ss in search_string_list:
                    #TODO: findall aqui? achar mais de uma vez a mesma coisa na mesma linha?!
                    search = re.search(ss, line, re.IGNORECASE)
                    if search:
                        finds[file].append((idx+1, line[:-1], search.span()))

    print('findings:')

    for f in finds:
        #if not finds[f] == []:
        if finds[f]:
            print(color(f,Colors.purple))
            for idx, line, span in finds[f]:
                if span[0] == 0:
                    print('\t',color(idx,Colors.red),' : ', color(line[span[0]:span[1]],Colors.green), line[span[1]:], sep='')
                elif span[1] == len(line):
                    print('\t',color(idx,Colors.red),' : ', line[0:span[0]], color(line[span[0]:span[1]],Colors.green), sep='')
                else:
                    print('\t',color(idx,Colors.red),' : ', line[0:span[0]], color(line[span[0]:span[1]],Colors.green), line[span[1]:], sep='')
            print()


#for file in [*dts_path_list, *include_file_list]:
#    with open(file) as f:

# property and value (has some dirty when multiple lines)
# (\S+)\s?=\s?([\s\S]+?);

# nodes
# (?:(\S+)\s?:\s?)?(\S+)\s+?\{
