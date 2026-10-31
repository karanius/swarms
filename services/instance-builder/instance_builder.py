#!/usr/bin/env python3
"""Local guided instance builder: start/resume and capture intent only."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from uuid import uuid4
import sys

# Use the service environment even when launched with the user's system Python.
if __name__ == '__main__':
    executable = Path(__file__).parent / '.venv' / 'bin' / 'python'
    if executable.exists() and Path(sys.prefix).resolve() != executable.parent.parent.resolve():
        os.execv(str(executable), [str(executable), str(Path(__file__).resolve()), *sys.argv[1:]])

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console(highlight=False)


def heading(step):
    console.print()
    console.print('[bold bright_cyan]  INSTANCE[/]  [dim]/  guided builder[/]')
    console.print('  Turn an intention into a system.', style='dim')
    console.print()
    track = Text('  ')
    track.append('01  Start or resume', style='bold bright_cyan' if step == 1 else 'green')
    track.append('     ───     ', style='bright_black')
    track.append('02  Describe outcome', style='bold bright_cyan' if step == 2 else 'dim')
    console.print(track)
    console.print()


def card(title, body, style='cyan'):
    console.print(Panel(body, title=title, title_align='left', border_style=style,
                        padding=(1, 2), box=box.ROUNDED, width=min(console.width, 92)))



def save(root, instance):
    root.mkdir(parents=True, exist_ok=True)
    target = root / (instance['id'] + '.json')
    fd, temporary = tempfile.mkstemp(prefix='.instance-', dir=root)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(instance, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return target


def load_instances(root):
    result = []
    if root.exists():
        for path in root.glob('*.json'):
            record = json.loads(path.read_text())
            if record.get('schema_version') != 1 or record.get('id') != path.stem:
                raise ValueError('An instance file has an unsupported or inconsistent format: ' + path.name)
            result.append(record)
    return sorted(result, key=lambda record: record['updated_at'], reverse=True)


class Back(Exception):
    pass


class Quit(Exception):
    pass


def ask(prompt, choices=None, back=False):
    while True:
        console.print(prompt, end='', style='bold bright_cyan', markup=False)
        answer = input().strip()
        if answer.lower() == '/quit' or (choices and answer.lower() == 'q'):
            raise Quit
        if back and (answer.lower() == '/back' or (choices and answer.lower() == 'b')):
            raise Back
        if answer and (choices is None or answer in choices):
            return answer
        console.print('  Choose a listed option, or use the navigation below.' if choices else '  Describe your outcome, or use /back to return.', style='yellow')


def navigation(back=True, text=False):
    console.print()
    console.print(('  /back  Back     /quit  Save & exit' if text else '  B  Back     Q  Save & exit') if back else '  Q  Save & exit', style='dim')
    console.print()


def run(root):
    last = None
    try:
        while True:
            heading(1)
            instances = load_instances(root)
            menu = Table.grid(padding=(0, 3))
            menu.add_column(style='bold bright_cyan')
            menu.add_column()
            menu.add_row('1', 'Create an instance')
            menu.add_row('', Text('Describe a new outcome.', style='dim'))
            if instances:
                menu.add_row('2', f'Resume an instance · {len(instances)} saved')
                menu.add_row('', Text('Continue an unfinished description or review a saved one.', style='dim'))
            card(' WORKSPACE ', menu)
            navigation(False)
            choice = ask('  Choose  ›  ', {'1', '2'} if instances else {'1'})
            if choice == '2':
                table = Table(box=box.SIMPLE, expand=True, show_edge=False, padding=(0, 1))
                table.add_column('#', style='bright_cyan', width=3)
                table.add_column('DESIRED OUTCOME', ratio=4)
                table.add_column('STATUS', ratio=1)
                for index, record in enumerate(instances, 1):
                    table.add_row(str(index), Text(record.get('outcome') or 'Untitled draft · description needed'),
                                  Text('Saved' if record.get('outcome') else 'Draft', style='green' if record.get('outcome') else 'yellow'))
                card(' WORKSPACE / RESUME ', table)
                navigation()
                try:
                    selected = ask('  Instance  ›  ', {str(i) for i in range(1, len(instances) + 1)}, back=True)
                except Back:
                    continue
                instance = instances[int(selected) - 1]
            else:
                instance = None
            try:
                while True:
                    if instance is None or not instance.get('outcome'):
                        heading(2)
                        card(' WORKSPACE / OUTCOME ', Group(
                            Text('What should this instance accomplish?', style='bold white'), Text(''),
                            Text('Describe the result you want, in your own words.', style='dim'),
                            Text('Example: Turn a real estate referral program into a profitable venture.', style='italic cyan')))
                        console.print('  Enter saves your description. /back returns to the workspace.', style='dim')
                        navigation(text=True)
                        outcome = ask('  Outcome  ›  ', back=True)
                        if instance is None:
                            now = datetime.now(timezone.utc).isoformat()
                            instance = {'schema_version':1, 'id':str(uuid4()), 'created_at':now}
                        instance.update(outcome=outcome, stage='outcome_captured', updated_at=datetime.now(timezone.utc).isoformat())
                        save(root, instance)
                    last = instance
                    card(' WORKSPACE / REVIEW · SAVED ', Group(Text(instance['outcome'], style='bold white'), Text(''),
                        Text('01  Instance ready     02  Outcome captured', style='green')), 'green')
                    console.print('  C  Continue discovery     E  Edit outcome     M  Model setup', style='cyan')
                    console.print('  B  Workspace     Q  Save & exit', style='dim')
                    console.print('  Pi loads this instance’s records fresh each session.', style='dim')
                    action = ask('  Next  ›  ', {'e', 'E','c','C','m','M'}, back=True)
                    if action.lower() == 'm':
                        import pi_adapter
                        try:
                            pi_adapter.setup()
                            console.print('  API Proxy is ready.',style='green')
                        except pi_adapter.PiError as error:
                            card(' MODEL CONNECTION ',Text(str(error)),'yellow')
                        continue
                    if action.lower() == 'c':
                        import discovery
                        import pi_adapter
                        try:
                            discovery.run(root, instance, sys.modules[__name__])
                        except (Back, pi_adapter.PiError) as error:
                            if isinstance(error, pi_adapter.PiError):
                                card(' DISCOVERY ',Text(str(error)),'yellow')
                        continue
                    if action.lower() == 'e':
                        card(' EDIT OUTCOME ', Text(instance['outcome']))
                        console.print('  Enter a replacement. /back keeps the saved description.', style='dim')
                        navigation(text=True)
                        try:
                            outcome = ask('  New outcome  ›  ', back=True)
                        except Back:
                            continue
                        instance.update(outcome=outcome, updated_at=datetime.now(timezone.utc).isoformat())
                        save(root, instance)
            except Back:
                continue
    except Quit:
        console.print('\n  Saved work is safe. See you next time.\n', style='green')
        return last


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).parent / '.instances',
                        help='Directory for persisted instances')
    args = parser.parse_args()
    try:
        run(args.workspace.expanduser().resolve())
    except (EOFError, KeyboardInterrupt):
        console.print('\n  Paused · Your completed steps are saved.\n', style='cyan')
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'Unable to open or save this workspace: {error}\n')


if __name__ == '__main__':
    main()
