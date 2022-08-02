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

# Organize work streams in Foam (https://foambubble.github.io/foam/).

from absl import app
from absl import flags

import json
import os.path
import re

flags.DEFINE_string('foam_path', None, 'Foam path.')
flags.DEFINE_string('stream_data_path', None, 'Where to write stream data to.')

FLAGS = flags.FLAGS


UPLOAD_TAG = 'UPLOAD_TO_DASHBOARD'
OBSOLETE_TAG = 'OBSOLETE_STREAM'


def expand_project_tags(tag):
  tags = set([tag])
  if tag.startswith('proj--'):
    parts = tag.split('--')
    for i in range(1, len(parts) - 1):
      tags.add('--'.join(parts[:i+1]))
  return sorted(list(tags), key=len, reverse=True)


def find_all_tags(s):
  # Finds all tags and expands them as needed.
  m = re.findall(r'\[\[(.+?)\]\]|#([a-zA-Z0-9\-_]+?)\b', s)
  tags = []
  for g in m:
    g = [e for e in g if e]
    if len(g) != 1:
      raise ValueError(f'Invalid match: {g} for {s=}')
    tags += expand_project_tags(g[0])
  return tags


def remove_tag(tag, s):
  s = s.replace(f'#[[{tag}]]', '').replace(f'[[{tag}]]', '')
  return re.sub(fr'#{tag}\b', '', s)


def main(_):
  with open(os.path.join(FLAGS.foam_path, 'all-streams.md'), 'r') as f:
    raw_lines = f.readlines()

  projects = set()
  streams = []
  for raw_line in raw_lines:
    tags = find_all_tags(raw_line)
    for t in tags:
      if t.startswith('proj--'):
        projects.add(t)

    if (UPLOAD_TAG not in tags) and (OBSOLETE_TAG not in tags):
      continue
    stream = remove_tag(OBSOLETE_TAG, remove_tag(UPLOAD_TAG, raw_line))

    dates = [t for t in tags if re.fullmatch(r'\d\d\d\d-\d\d-\d\d', t)]
    if not dates:
      raise ValueError(f'Stream with no dates: {stream}')

    streams.append({
      'raw_text': stream,
      # in python 3.9 start using removeprefix instead
      'text': re.sub(r'^\*', '', stream.strip()).strip(),
      'dates': dates,
      'last_date': sorted(dates)[-1],
      'tags': tags,
      'obsolete': (OBSOLETE_TAG in tags)})

  with open(FLAGS.stream_data_path, 'w') as f:
    f.write(json.dumps(
      {'projects': list(projects), 'streams': streams}))
  print(f'Finished writing to {FLAGS.stream_data_path}')


if __name__ == '__main__':
  flags.mark_flag_as_required('foam_path')
  flags.mark_flag_as_required('stream_data_path')
  app.run(main)
