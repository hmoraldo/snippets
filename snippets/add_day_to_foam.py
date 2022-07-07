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

# Add a day note to Foam (https://foambubble.github.io/foam/).
from absl import app
from absl import flags

import datetime
import glob
import os.path

flags.DEFINE_string('foam_path', None, 'Foam path.')
flags.DEFINE_string('template_path', None, 'Template path.')

FLAGS = flags.FLAGS


def path_to_date(path):
  return os.path.basename(os.path.splitext(path)[0])


def main(_):
  today = datetime.date.today().strftime('%Y-%m-%d')
  today_path = os.path.join(FLAGS.foam_path, f'{today}.md')
  today_meetings_path = os.path.join(FLAGS.foam_path, f'meetings-{today}.md')

  # Find last_day, usually yesterday.
  last_paths = sorted(glob.glob(os.path.join(FLAGS.foam_path, '????-??-??.md')))
  last_paths = [p for p in last_paths if path_to_date(p) <= today]
  last_path = last_paths[-1]
  last_day = path_to_date(last_path)
  print(f'last day: {last_day}')

  if os.path.exists(today_path):
    print(f'File for {today} already exists, quitting.')
    return

  with open(last_path, 'r') as f:
    # Lines marked with this tag aren't sent to next day, even if they contain
    # SEND_NEXT_STR or KEEP_NEXT_STR strings.
    AUTO_REMOVE_STR = 'AUTO_REMOVE'
    # Lines marked with this tag are sent to the next day.
    SEND_NEXT_STR = 'SEND_TO_NEXT_DAY'
    # Lines marked with this tag are sent to all next days, not just the next one.
    KEEP_NEXT_STR = 'KEEP_ALL_NEXT_DAYS'

    raw_lines = f.readlines()
    lines_to_add = [l.replace(SEND_NEXT_STR, '') for l in raw_lines if SEND_NEXT_STR in l]
    lines_to_add += [l for l in raw_lines if KEEP_NEXT_STR in l]
    lines_to_add = [l.rstrip() for l in lines_to_add if AUTO_REMOVE_STR not in l]

  with open(FLAGS.template_path, 'r') as f:
    template = f.read()

  with open(today_meetings_path, 'w') as f:
    f.write(f'# meetings-{today}\n\nlast meeting notes: [[meetings-{last_day}]]\n\nbacklinks\n\n')

  with open(today_path, 'w') as f:
    contents = template.replace('{TODAY}', today).replace('{LAST_DAY}', last_day)
    contents += '\n'.join(lines_to_add) + '\n'
    f.write(contents)

  print(f'Preserving lines: {lines_to_add}')
  print('Done.')


if __name__ == '__main__':
  flags.mark_flag_as_required('foam_path')
  flags.mark_flag_as_required('template_path')
  app.run(main)
