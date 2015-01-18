import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

text = (("The quick brown", (255, 0, 0)), (" fox jumps over", (0, 255, 0)), (" the lazy dog.", (0, 0, 255)))

class TextWriter(object):
	def __init__(self, fontfile, fontsize, imagefile):
		self._font = ImageFont.truetype(fontfile, fontsize)
		self._imagefile = imagefile
	
	def set_font(self, fontfile, fontsize):
		self._font = ImageFont.truetype(fontfile, fontsize)
	
	def set_imagefile(self, imagefile):
		self._imagefile = imagefile
	
	def write_texts(self, text, y_offset=0):
		all_text = ""
		for text_color_pair in text:
			t = text_color_pair[0]
			all_text = all_text + t
		 
		width, ignore = self._font.getsize(all_text)

		im = Image.new("RGB", (width + 100, 16), "black")
		draw = ImageDraw.Draw(im)
		 
		x = 0
		for text_color_pair in text:
			t = text_color_pair[0]
			c = text_color_pair[1]
			draw.text((x, y_offset), t, c, font=self._font)
			x = x + self._font.getsize(t)[0]
		 
		im.save(self._imagefile)

	def write_text(self, text, color, y_offset=0):
		self.write_texts(((text, color),), y_offset)
