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

import datetime
import glob
import os.path
import re

flags.DEFINE_string('foam_path', None, 'Foam path.')

FLAGS = flags.FLAGS


UPLOAD_TAG = 'UPLOAD_TO_DASHBOARD'


def is_tag_present(tag, s):
  return (f'[[{UPLOAD_TAG}]]' in s) or (f'#{UPLOAD_TAG}' in s) or f'#[[{UPLOAD_TAG}]]' in s


def remove_tag(tag, s):
  return s.replace(f'#[[{UPLOAD_TAG}]]', '').replace(f'[[{UPLOAD_TAG}]]', '').replace(f'#{UPLOAD_TAG}', '')


def main(_):
  # Create generated file.
  with open(os.path.join(FLAGS.foam_path, 'all-streams.md'), 'r') as f:
    raw_lines = f.readlines()

  active_streams = [remove_tag(UPLOAD_TAG, l) for l in raw_lines if is_tag_present(UPLOAD_TAG, l)]

  streams_one_date = []
  streams_more_dates = []
  for stream in active_streams:
    dates = re.findall('\[\[(\d\d\d\d-\d\d-\d\d)\]\]', stream)
    if not dates:
      raise ValueError(f'Stream with no dates: {stream}')

    d = {'raw_text': stream,
         # in python 3.9 start using removeprefix instead
         'text': re.sub('^\*', '', stream.strip()).strip(),
         'dates': dates,
         'last_date': sorted(dates)[-1]}
    if len(dates) == 1:
      streams_one_date.append(d)
    elif len(dates) > 1:
      streams_more_dates.append(d)

  GENERATED_FILE_NAME = 'all-streams-generated'
  WARNING_STRING = '**THIS FILE IS AUTO GENERATED - DO NOT EDIT** - Edit streams in [[all-streams]] instead.\n\n'
  last_date_key = lambda d: d['last_date']

  with open(os.path.join(FLAGS.foam_path, f'{GENERATED_FILE_NAME}.md'), 'w') as f:
    f.write(f'# {GENERATED_FILE_NAME}\n\n')
    f.write(WARNING_STRING)
    f.write('Streams with double dates:\n\n')
    for stream in sorted(streams_more_dates, key=last_date_key):
      f.write(f'* {stream["last_date"]}: {stream["text"]}\n')
    f.write('\n')
    f.write(WARNING_STRING)
    f.write('Streams with single dates:\n\n')
    for stream in sorted(streams_one_date, key=last_date_key):
      f.write(f'* {stream["last_date"]}: {stream["text"]}\n')

    f.write('\n')
    f.write(WARNING_STRING)

  # Create quick links page.
  QUICK_LINKS_FILE_NAME = '000-quick-links'
  QUICK_LINKS_WARNING = '**THIS FILE IS AUTO GENERATED - DO NOT EDIT**\n'
  with open(os.path.join(FLAGS.foam_path, f'{QUICK_LINKS_FILE_NAME}.md'), 'w') as f:
    today = datetime.date.today().strftime('%Y-%m-%d')

    f.write(f'# {QUICK_LINKS_FILE_NAME}\n\n')
    f.write(QUICK_LINKS_WARNING)
    f.write('\n')
    f.write(f'* today: [[{today}]]\n')
    f.write(f'* today meetings: [[meetings-{today}]]\n')
    f.write(f'* future meetings: [[future-meetings]]\n')
    f.write(f'* all-streams (editable): [[all-streams]]\n')
    f.write(f'* all-streams-generated: [[all-streams-generated]]\n')
    f.write(f'* startup page: [[000-startup]]\n')
    f.write('\n')
    f.write(QUICK_LINKS_WARNING)

  print('Done.')


if __name__ == '__main__':
  flags.mark_flag_as_required('foam_path')
  app.run(main)
