"""Functions related to the running environment."""
import os

from tensorflow.python.client import device_lib

_CUDA_VISIBLE_DEVICES_KEY = 'CUDA_VISIBLE_DEVICES'


def ForceCpuForTheRun() -> None:
  """Sets to use only CPU for TF/Keras.

  Must be called before Keras/TF related functions. Once set, you cannot unset
  it for the the rest of the run. For example, calling
  `CheckAndForceGpuForTheRun` function later will return False.
  """
  os.environ[_CUDA_VISIBLE_DEVICES_KEY] = '-1'
  # Force TF to initialize, therefore there is no visible GPU for the rest of
  # the run.
  device_lib.list_local_devices()


def CheckAndForceGpuForTheRun() -> bool:
  """Initialize TF/Keras with GPU devices, if any.

  If there is a GPU, once this function is called GPU will be used for the
  rest of the run. If there is no GPU, CPU will be used.

  Returns:
     Whether there is a GPU.
  """
  for device in device_lib.list_local_devices():
    if 'GPU' in device.name:
      return True
  return False
