import binascii
import argparse
import numpy as np
import os
import progressbar
from PIL import Image
from storage import colors

parser = argparse.ArgumentParser(description="Converts PNG files from or to CMI files.",
   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("src", help="Source file to convert", type=str)
parser.add_argument("--output", help="Output path (with filename), makes a default name in the directory of the original file if not provided", required=False, type=str)
parser.add_argument("--size", help="Determines the max resolution of a outputted cmi file. Will determine a size from the image if none is given. (1 = 1020x1020 max, 2 = 64516x64516 max, 3 = 16387064x16387064 max. Image will be automatically resized if it doesn't fit the maximum size)", choices=[1, 2], required=False, type=int)

args = parser.parse_args()

contype = 'cmi'
if os.path.splitext(os.path.basename(args.src))[1] == '.cmi':
  contype = 'png'

# making sure all arguments are valid

if not os.path.exists(args.src):
  raise SyntaxError('File provided is not a file.')

if not (os.path.splitext(os.path.basename(args.src))[1] == '.png' or os.path.splitext(os.path.basename(args.src))[1] == '.cmi'):
  raise SyntaxError('File must me a CMI or a PNG file.')

if contype == 'png' and args.size is not None:
  raise SyntaxError('Argument "size" is not required when converting to png.')

# progress bar stuff

widgets = [
    ' [', progressbar.Timer(), '] ',
    progressbar.Bar(marker='█', left='[', right=']'), ' [',
    progressbar.Percentage(), ', ', progressbar.SimpleProgress(), ']'
]

# functions

def closest_color(color):
  colorlist = np.array(colors)
  color = np.array(color)
  distances = np.sqrt(np.sum((colors-color)**2,axis=1))
  index_of_smallest = np.where(distances==np.amin(distances))
  smallest_distance = colorlist[index_of_smallest]
  return smallest_distance 

# actual conversion

if contype == 'cmi':
  print('Initializing')
  imgName = os.path.splitext(os.path.basename(args.src))[0]
  originalImage = Image.open(args.src)
  originalImage = originalImage.convert('RGB')
  owidth, oheight = originalImage.size
  maximums = [1020, 64516, 16387064]

  sizetype = 0
  if args.size is None:
    if owidth <= 1020 or oheight <= 1020:
      sizetype = 1
    elif owidth <= 64516 or oheight <= 64516:
      sizetype = 2
    else:
      sizetype = 3
  else:
    sizetype = args.size
  
  if owidth > maximums[sizetype-1]:
    originalImage.thumbnail((maximums[sizetype-1], maximums[sizetype-1]))
    owidth, oheight = originalImage.size

  if oheight > maximums[sizetype-1]:
    originalImage.thumbnail((maximums[sizetype-1], maximums[sizetype-1]))
    owidth, oheight = originalImage.size
  
  width = int(np.ceil(owidth / 4))
  height = int(np.ceil(oheight / 4))
  
  originalImage.thumbnail((width, height))
  
  bar = progressbar.ProgressBar(maxval=width*height, widgets=widgets)
  bar.start()
  idx = 0

  filename = imgName + '.cmi'
  if args.output is not None:
    filename = args.output
  
  with open(filename, 'wb') as image:
    data = b'cmi'
    data += sizetype.to_bytes(1, byteorder='big') + width.to_bytes(sizetype, byteorder='big') + height.to_bytes(sizetype, byteorder='big') + b'\x00'
  
    pixels = originalImage.load()
    for y in range(height):
      for x in range(width):
        color = np.array([[0, 0, 0]])
        try:
          color = closest_color(pixels[x, y])
        except IndexError:
          pass
        val = colors.index(color.tolist()[0])
        data += bytes.fromhex(format(val + 1, '02x'))
        idx += 1
        if idx < width*height:
          bar.update(idx)

    bar.update(width*height)
    image.write(data)
    print(f'\nFinshed, wrote to {filename}')
      
elif contype == 'png':
  imgName = os.path.splitext(os.path.basename(args.src))[0]
  data = b''

  with open(args.src, 'rb') as image:
    data = image.read()

  chunks = data.rsplit(b'\x00', 1)

  if chunks[0][0:3] == b'cmi': # checks for the signature to ensure it's reading a real cmi file
    sizetype = chunks[0][3]
    print(sizetype*2+5)
    width = int.from_bytes(chunks[0][4:sizetype+4], byteorder='big')
    height = int.from_bytes(chunks[0][sizetype+4:sizetype*2+4], byteorder='big')
    print(width, height)
    pngImage = Image.new('RGB', (width, height), color = (0, 0, 0))

    bar = progressbar.ProgressBar(maxval=width*height, widgets=widgets)
    bar.start()
    idx = 0
    
    pngImageData = pngImage.load()
    for i in range(len(chunks[1])):
      y = np.floor(i / width)
      x = i - (y * width)
      pixel = tuple(colors[chunks[1][i]-1])
      pngImageData[x, y] = pixel

      idx += 1
      bar.update(idx)

    bar.update(width*height)
    pngImage = pngImage.resize((width * 4, height * 4), Image.Resampling.BICUBIC)
    if args.output is None:
      pngImage.save(imgName + '-converted.png')
      print(f'\nFinshed, wrote to {imgName}-converted.png')
    else:
      pngImage.save(args.output)
      print(f'\nFinshed, wrote to {args.output}')
  else:
    raise UnicodeDecodeError("CMI file signature is invalid, this could mean the file is corrupted.")
