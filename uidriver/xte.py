"""Helps operating with xte."""

import subprocess

from tool import t


class Xte:
  def __init__(
      self,
      pause_between_actions_sec: float = 0.2):
    self.pause_between_actions_sec = pause_between_actions_sec

  def Run(self, sequence: t.List[str]) -> None:
    """Runs a sequence of commands in xte."""
    sequence_with_pause = []
    for cmd in sequence:
      sequence_with_pause.append(cmd)
      sequence_with_pause.append('sleep %s' % self.pause_between_actions_sec)
    sequence_multiline = '\n'.join(sequence_with_pause).encode()
    process_with_pipe = subprocess.Popen(['xte'], stdin=subprocess.PIPE)
    process_with_pipe.communicate(input=sequence_multiline)


def HoldPressRelease(hold_key: str, press_key: str) -> t.List[str]:
  """Helps generate sequence for tasks like "ctrl-a"."""
  return [
    'keydown %s' % hold_key,
    'key %s' % press_key,
    'keyup %s' % hold_key,
  ]


def Test():
  xte = Xte()
  xte.Run([
    'keydown Alt_L',
    'key Tab',
    'keyup Alt_L',
  ])


if __name__ == '__main__':
  Test()
