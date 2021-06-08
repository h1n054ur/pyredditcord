# indent = tab
# tab-size = 4

# Copyright 2019 Joni Larsen-Haikarainen (jonilh@gmail.com)

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from PIL import Image, ImageDraw, ImageFont

class Spreadsheet:
    def __init__(self, path='tmp.png', xpad=5, ypad=5, sx=5, sy=5):
        self.content    = []
        #self.width      = 0
        self.cwidth     = []
        self.height     = 0
        self.path       = path
        self.xpad       = xpad
        self.ypad       = ypad
        self.sx         = sx
        self.sy         = sy

    def addrow(self, row, fontpath, fontsize, fontcolor=(255,255,255)):
        if not type(row) is tuple and not type(row) is list:
            raise TypeError("row must be a tuple or list.")
        if not type(fontpath) is str:    raise TypeError("fontpath must be a str.")
        if not type(fontsize) is int:    raise TypeError("fontsize must be a int.")
        if not type(fontcolor) is tuple: raise TypeError("fontcolor must be a tuple.")

        crow = {'fontpath':fontpath, 'fontsize':fontsize, 'fontcolor':fontcolor}
        rowfont = ImageFont.truetype(crow['fontpath'], crow['fontsize'])
        self.height += rowfont.getsize("TEST")[1] + self.ypad

        for index, word in enumerate(row):
            try:
                if self.cwidth[index] < rowfont.getsize(word)[0] + self.xpad:
                    self.cwidth[index] = rowfont.getsize(word)[0] + self.xpad
            except:
                self.cwidth.append(rowfont.getsize(word)[0] + self.xpad)

        crow['row'] = row
        self.content.append(crow)

    def makeimg(self, color = (0, 0, 0, 25), lines=True):
        if len(self.content) == 0:
            raise Exception("Can not make a Spreadsheet without any content.")

        final_width =  sum(self.cwidth) + (len(self.cwidth) * self.xpad) + self.sx
        final_height = self.height + self.sy
        img = Image.new('RGBA', (final_width, final_height), color)

        d = ImageDraw.Draw(img)
        y = self.sy
        if lines: d.line([0,self.sy/2 , img.size[0],self.sy/2], fill=0)
        for line in self.content:
            x = self.sx

            rowfont = ImageFont.truetype(line['fontpath'], line['fontsize'])
            for index, word in enumerate(line['row']):
                d.text((x,y), word, fill=line['fontcolor'], font=rowfont)
                x += self.cwidth[index] + self.xpad
            y += rowfont.getsize("TEST")[1] + self.ypad
            if lines: d.line([0,y-(self.ypad/2) , img.size[0],y-(self.ypad/2)], fill=0)

        img.save(self.path)
        return self.path
