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


def main(_):
  last_path = sorted(glob.glob(os.path.join(FLAGS.foam_path, '????-??-??.md')))[-1]
  last_day = os.path.basename(os.path.splitext(last_path)[0])
  print(f'last day: {last_day}')

  today = datetime.date.today().strftime('%Y-%m-%d')
  today_path = os.path.join(FLAGS.foam_path, f'{today}.md')
  today_meetings_path = os.path.join(FLAGS.foam_path, f'meetings-{today}.md')

  if os.path.exists(today_path):
    print(f'File for {today} already exists, quitting.')
    return

  with open(last_path, 'r') as f:
    SEND_NEXT_STR = 'SEND_TO_NEXT_DAY'
    lines_to_add = [l.replace(SEND_NEXT_STR, '') for l in f.readlines() if SEND_NEXT_STR in l]

  with open(FLAGS.template_path, 'r') as f:
    template = f.read()

  with open(today_meetings_path, 'w') as f:
    f.write(f'# meetings-{today}\n\nbacklinks\n\n')

  with open(today_path, 'w') as f:
    contents = template.replace('{TODAY}', today).replace('{LAST_DAY}', last_day)
    contents += ' '.join(lines_to_add)
    f.write(contents)

  print(f'Preserving lines: {lines_to_add}')
  print('Done.')


if __name__ == '__main__':
  flags.mark_flag_as_required('foam_path')
  flags.mark_flag_as_required('template_path')
  app.run(main)

