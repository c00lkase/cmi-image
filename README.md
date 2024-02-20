# cmi-image

## What is this?
This is a an file type that aims to be much smaller than other image formats *(sometimes 75% smaller!)*. The code provided in this repository provides a converter that can convert between [PNG files](https://en.wikipedia.org/wiki/PNG) and CMI files.

## How do I use it?
1. Firstly, you need [Python](https://www.python.org/downloads/), *(Python 3.12 was used to test this)*
2. Secondly, you need to set the current directory to wherever you downloaded this, and run
`pip install -r requirements.txt`
.
4. Now, you can actually convert with it, here's all of the arguments you can use:

positional arguments (required):
	  src              Source file to convert

options:
	  -h, --help       show this help message
	  --output Output path (with filename), makes a default name in the directory of the original file if not
	                   provided (default: None)
	  --size {1,2,3}     Determines the max resolution of a outputted cmi file. Will determine a size from the image if none
	                   is given. (1 = 1020x1020 max, 2 = 64516x64516 max, 3 = 16387064x16387064 max. Image will be
	                   automatically resized if it doesn't fit the maximum size) (default: None)

## What does it look like?
Its not the *best* quality, it locks the color palette to 255 colors, and saves a quarter of the original image in the file *(it still converts it to the correct size when converting back)*

For example, heres a color spectrum with all colors besides grayscale colors:
<br><br><img src="https://i.postimg.cc/wjyW5sG4/colorscale.png" alt="colorscale.png" width="350"> 

Now, I will run 
`cmi.py colorscale.png`
, and get a CMI file in return, now lets see what it saved by doing the reverse, `cmi.py colorscale.cmi`
I get this image in return:

<img src="https://i.postimg.cc/Jz59HXHw/rainbowres-converted.png" alt="colorscale-converted.png" width="350"> 

Its obviously not the best image format, but it works. Now lets add more arguments to get more specific results.

### Adding optional arguments
I will start with `--output` because it's easy to understand, it lets you pick a filename and location, an example is `cmi.py colorscale.png --output=C:\why-here.png`

Now, a more fun argument is size, it modifies `0x00000003` in the file which determines the maximum size of said image *(i explain more on how the format works later)* For example, lets use the color scale image we've been using and set it's size to 1.
`cmi.py colorscale.png --size=1`
We get a cmi file, noticeably smaller than the last one, now lets convert it to a png.
`cmi.py colorscale.cmi`

<img src="https://i.postimg.cc/wxPVFBY1/rainbowres-converted.png" alt="colorscale-converted.png" width="350"> 

It's noticeably smaller as well. Lets move on to the last section that explains how the file itself works

## How does it work?
I adopted most of the ways a PNG file works because of [this video](https://www.youtube.com/watch?v=-Rdo8KAHgoE) which inspired me to make this image format. Anyways, the file is encoded and decoded in [hexadecimal](https://en.wikipedia.org/wiki/Hexadecimal), split into 2 chunks by a end-of-chunk byte of `0x00` *(this is why there are 255 possible colors to decode and not 256)*. The first chunk contains the [file signature](https://en.wikipedia.org/wiki/File_signature) *(a form of verification)* the SizeType *(explained before)*, the width, and the height of the image. The next chunk is the image data, it contains the color index of every pixel *(list of possible colors is in **storage.py**)* which extends to the end of the file. 
Here is a visual example of `colorscale.cmi` *(which I converted last)* with labels for each chunk & sub-chunk:

![visual example depicting each chunk & sub-chunk](https://i.postimg.cc/gjw15B08/Untitled.png) -- will fix image soon <br>
*(please note that the length of the width & height sub-chunk can vary dependent on the SizeType)*

## Plans for the Future
A list:

 - [ ] Add quantization to allow better-looking images
 - [ ] Reduce CMI file size by having a color index then length of said color
 - [ ] Add an actual checksum

Well that's all, hope you enjoyed this.
