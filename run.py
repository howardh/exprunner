#!/usr/bin/python3
import subprocess
import sys
import os
import re
import itertools
import collections

current_working_directory = os.getcwd()
print('Working directory: %s' % current_working_directory)

command = sys.argv[1:]
print('Command: %s' % command)

"""
- Save hash of all modified files
- Add hashes to tree
- Commit tree
    - Parent is currently checked out tree
    - Commit message should contain reference to previous execution
"""

changed_files = subprocess.check_output('git diff --name-only'.split(' '))
changed_files = changed_files.strip()
if len(changed_files) == 0:
    changed_files = []
else:
    changed_files = changed_files.split(b'\n')
print('Changed files: %s' % changed_files)
new_files = subprocess.check_output('git diff --name-only --cached'.split(' '))
new_files = new_files.strip()
if len(new_files) == 0:
    new_files = []
else:
    new_files = new_files.split(b'\n')
print('New files: %s' % new_files)

# Create hash for each file
for file_name in itertools.chain.from_iterable([changed_files, new_files]):
    file_hash = subprocess.check_output('git hash-object -w {file_name}'
            .format(file_name=file_name.decode('ascii'))
            .split(' ')).strip()
    print('Hash %s: %s' % (file_name, file_hash))
# Stage files
subprocess.check_output('git ls-files --stage'.split(' '))
# Write tree
tree_hash = subprocess.check_output('git write-tree'.split(' '))
tree_hash = tree_hash.strip().decode('ascii')
print('Tree Hash: %s' % tree_hash)

# Commit
first_execution = False
try:
    last_exec_ref = subprocess.check_output('git show-ref refs/exprunner/lastexecution'.split(' '))
except subprocess.CalledProcessError:
    first_execution = True
if first_execution:
    print('first execution')
    message = 'Execution #1'
    commit_hash = subprocess.check_output(['git','commit-tree',tree_hash,'-p','HEAD','-m',message])
else:
    print('not first execution')
    # Get the commit message of the last execution
    last_exec_ref = last_exec_ref.strip().decode('ascii')
    if len(last_exec_ref) != 0:
        message = subprocess.check_output('git log --oneline -n 1 refs/exprunner/lastexecution'.split(' '))
        message = message.decode('ascii')
        message = ' '.join(message.split(' ')[1:])
        print('message: %s' % message)
    # Increment count
    match = re.search('^(.*) #(\d+)$', message)
    text = match.group(1)
    num = match.group(2)
    next_num = int(num)+1
    print('Text: %s, Num: %s' % (text, num))
    # Create new commit message with new count
    new_message = '%s #%d' % (text, next_num)
    print('New message: %s' % new_message)
    # Commit
    commit_hash = subprocess.check_output(['git','commit-tree',tree_hash,'-p','HEAD','-p','refs/exprunner/lastexecution','-m',new_message])
commit_hash = commit_hash.decode('ascii').strip()
print('Commit hash: %s' % commit_hash)

# Update refs
subprocess.check_output('git update-ref refs/exprunner/lastexecution {commit_hash}'
        .format(commit_hash=commit_hash)
        .split(' '))

"""
Tests:
- First execution without a commit
- First execution with a commit
- Execution (not first) with no change since last commit
- Execution (not first) with changes since last commit
"""

"""
Execution log:
    git log --graph --notes='*' --grep='Execution #' --pretty refs/exprunner/lastexecution
Modify notes:
    git notes edit <execution commit hash>
View notes:
    git notes show <execution commit hash>
"""
