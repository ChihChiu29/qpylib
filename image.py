"""Helps with image manipulation."""
import base64
import io

from PIL import Image


def ConvertPNGToImage(png: bytes) -> Image:
  """Converts a PNG byte string to an image.

  PNG bytes returned by webdriver has this format.
  """
  return Image.open(io.BytesIO(png))


def EncodedPNGToImage(encoded_png: str) -> Image:
  """Converts a base64-encoded PNG string to on image.

  PNG string returned by chrome_driver (chrome debug protocol) has this format.
  """
  return Image.open(io.BytesIO(base64.b64decode(encoded_png)))
