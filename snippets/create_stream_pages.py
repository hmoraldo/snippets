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

# Create pages for Foam work streams (https://foambubble.github.io/foam/).
from absl import app
from absl import flags

import datetime
import json
import os.path

flags.DEFINE_string('foam_path', None, 'Foam path.')
flags.DEFINE_string('stream_data_path', None, 'Where to write stream data to.')
FLAGS = flags.FLAGS


def generate_file(file_name, streams, related_pages=[]):
  streams_one_date, streams_more_dates, obsolete_streams = [], [], []
  for stream in streams:
    if stream['obsolete']:
      obsolete_streams.append(stream)
    elif len(stream['dates']) == 1:
      streams_one_date.append(stream)
    elif len(stream['dates']) > 1:
      streams_more_dates.append(stream)

  WARNING_STRING = '**THIS FILE IS AUTO GENERATED - DO NOT EDIT** - Edit streams in [[all-streams]] instead.\n\n'
  last_date_key = lambda d: d['last_date']
  with open(os.path.join(FLAGS.foam_path, f'{file_name}.md'), 'w') as f:
    f.write(f'# {file_name}\n\n{WARNING_STRING}')

    if related_pages:
      f.write(f'Related pages:\n\n')
      for related_page in related_pages:
        f.write(f'* {related_page}: [[{related_page}]]\n')
      f.write(f'\n{WARNING_STRING}')

    if streams_more_dates:
      f.write('Streams with double dates:\n\n')
      for stream in sorted(streams_more_dates, key=last_date_key):
        f.write(f'* {stream["last_date"]}: {stream["text"]}\n')
      f.write(f'\n{WARNING_STRING}')

    if streams_one_date:
      f.write('Streams with single dates:\n\n')
      for stream in sorted(streams_one_date, key=last_date_key, reverse=True):
        f.write(f'* {stream["last_date"]}: {stream["text"]}\n')
      f.write(f'\n{WARNING_STRING}')

    if obsolete_streams:
      f.write('Obsolete streams:\n\n')
      for stream in sorted(obsolete_streams, key=last_date_key, reverse=True):
        f.write(f'* {stream["last_date"]}: {stream["text"]}\n')
      f.write(f'\n{WARNING_STRING}')


def main(_):
  with open(FLAGS.stream_data_path, 'rb') as f:
    data = json.loads(f.read())

  projects, streams = data['projects'], data['streams']

  generate_file('all-streams-generated', streams)
  for p in projects:
      # The third dash before generated ensures the hierarchy is sorted correctly in the fs.
      generate_file(
        f'all-streams--{p}---generated',
        [s for s in streams if (p in s['tags'])], related_pages=[p])

  QUICK_LINKS_FILE_NAME = '000-quick-links'
  QUICK_LINKS_WARNING = '**THIS FILE IS AUTO GENERATED - DO NOT EDIT**\n'
  with open(os.path.join(FLAGS.foam_path, f'{QUICK_LINKS_FILE_NAME}.md'), 'w') as f:
    today = datetime.date.today().strftime('%Y-%m-%d')
    f.write(f'# {QUICK_LINKS_FILE_NAME}\n\n{QUICK_LINKS_WARNING}\n')
    f.write(f'* today: [[{today}]]\n')
    f.write(f'* today meetings: [[meetings-{today}]]\n')
    f.write(f'* future meetings: [[future-meetings]]\n')
    f.write(f'* all-streams (editable): [[all-streams]]\n')
    f.write(f'* all-streams-generated: [[all-streams-generated]]\n')
    f.write(f'* all-stream-projects-generated: [[all-stream-projects-generated]]\n')
    f.write(f'* startup page: [[000-startup]]\n')
    f.write(f'\n{QUICK_LINKS_WARNING}')

  print('Done.')


if __name__ == '__main__':
  flags.mark_flag_as_required('foam_path')
  flags.mark_flag_as_required('stream_data_path')
  app.run(main)
