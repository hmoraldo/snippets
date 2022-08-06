# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Create project hierarchy for Foam work streams (https://foambubble.github.io/foam/).
from absl import app
from absl import flags

import collections
import json
import os.path
import re

flags.DEFINE_string('foam_path', None, 'Foam path.')
flags.DEFINE_string('stream_data_path', None, 'Where to get stream data from.')
FLAGS = flags.FLAGS


def remove_prefix(s, prefix):
  # in python 3.9 start using removeprefix instead
  return re.sub(f'^{prefix}', '', s)


def prepare_project_hierarchy(projects):
  hierarchy = collections.defaultdict(list)
  for parent in projects:
    for child in projects:
      ending = remove_prefix(child, parent)
      if ending.startswith('--') and ending.count('--') == 1:
        hierarchy[parent].append(child)

  return hierarchy


def main(_):
  with open(FLAGS.stream_data_path, 'rb') as f:
    data = json.loads(f.read())

  streams = data['streams']
  projects = ['proj']
  for stream in streams:
    for tag in stream['tags']:
      if tag.startswith('proj--'):
        projects.append(tag)

  hierarchy = prepare_project_hierarchy(set(projects))

  FILE_NAME = 'all-stream-projects-generated'
  WARNING = '**THIS FILE IS AUTO GENERATED - DO NOT EDIT**\n'
  with open(os.path.join(FLAGS.foam_path, f'{FILE_NAME}.md'), 'w') as f:
    f.write(f'# {FILE_NAME}\n\n{WARNING}\n')
    for parent in sorted(hierarchy.keys()):
      children = hierarchy[parent]
      f.write(f'## Subelements of {parent}\n\n')
      if parent != 'proj':
        f.write(f'Subelements of [[all-streams--{parent}---generated]]:\n\n')
      for child in children:
        f.write(f'* {child}: [[all-streams--{child}---generated]]\n')
      f.write(f'\n{WARNING}\n')

  print('Done.')


if __name__ == '__main__':
  flags.mark_flag_as_required('foam_path')
  flags.mark_flag_as_required('stream_data_path')
  app.run(main)
