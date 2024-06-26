# -*- coding: utf-8 -*-
"""
bmp.py - module for constructing simple BMP graphics files

 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
 the following conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
__version__ = "0.3"
__about =  "bmp module, version %s, written by Paul McGuire, October, 2003, updated by Margus Laak, September, 2009" % __version__ 

from math import ceil, hypot

'''
a= 100
a.to_bytes(6, "big")
int.from_bytes(input_data[0:3],'big',signed=True)
'''

def shortToByteArray(i):
  return i.to_bytes(2, "little")  

def longToByteArray(i):
  return i.to_bytes(4, "little")  

def long24ToByteArray(i):
  return i.to_bytes(3, "little")  

def byteArrayToLong(input_ba, offset):
  return int.from_bytes(input_ba[0:4], 'little', signed=False)

def byteArrayToLong24(input_string, offset):
  return int.from_bytes(input_ba[0:3], 'little', signed=False)



class Color(object):
  """class for specifying colors while drawing BitMap elements"""
  __slots__ = [ 'red', 'grn', 'blu' ]
  __shade = 32
  
  def __init__( self, r=0, g=0, b=0 ):
    self.red = r
    self.grn = g
    self.blu = b

  def __setattr__(self, name, value):
    if hasattr(self, name):
      raise AttributeError("Color is immutable")
    else:
      object.__setattr__(self, name, value)

  def __str__( self ):
    return "R:%d G:%d B:%d" % (self.red, self.grn, self.blu )
    
  def __hash__( self ):
    return ( ( int(self.blu) ) + 
              ( int(self.grn) <<  8 ) + 
              ( int(self.red) << 16 ) )
  
  def __eq__( self, other ):
    return (self is other) or (self.toLong == other.toLong)

  def lighten( self ):
    return Color( 
      min( self.red + Color.__shade, 255), 
      min( self.grn + Color.__shade, 255), 
      min( self.blu + Color.__shade, 255)  
      )
  
  def darken( self ):
    return Color( 
      max( self.red - Color.__shade, 0), 
      max( self.grn - Color.__shade, 0), 
      max( self.blu - Color.__shade, 0)  
      )
       
  def toLong( self ):
    return self.__hash__()
    
  def fromLong( l ):
    b = l & 0xff
    l = l >> 8
    g = l & 0xff
    l = l >> 8
    r = l & 0xff
    return Color( r, g, b )
  fromLong = staticmethod(fromLong)

# define class constants for common colors
Color.BLACK    = Color(   0,   0,   0 )
Color.RED      = Color( 255,   0,   0 )
Color.GREEN    = Color(   0, 255,   0 )
Color.BLUE     = Color(   0,   0, 255 )
Color.CYAN     = Color(   0, 255, 255 )
Color.MAGENTA  = Color( 255,   0, 255 )
Color.YELLOW   = Color( 255, 255,   0 )
Color.WHITE    = Color( 255, 255, 255 )
Color.DKRED    = Color( 128,   0,   0 )
Color.DKGREEN  = Color(   0, 128,   0 )
Color.DKBLUE   = Color(   0,   0, 128 )
Color.TEAL     = Color(   0, 128, 128 )
Color.PURPLE   = Color( 128,   0, 128 )
Color.BROWN    = Color( 128, 128,   0 )
Color.GRAY     = Color( 128, 128, 128 )


class BitMap(object):
  """class for drawing and saving simple Windows bitmap files"""
  
  LINE_SOLID  = 0
  LINE_DASHED = 1
  LINE_DOTTED = 2
  LINE_DOT_DASH=3
  _DASH_LEN = 12.0
  _DOT_LEN = 6.0
  _DOT_DASH_LEN = _DOT_LEN + _DASH_LEN
  
  def __init__( self, width, height, 
                 bkgd = Color.WHITE, frgd = Color.BLACK ):
    self.wd = int( ceil(width) )
    self.ht = int( ceil(height) )
    self.bgcolor = 0
    self.fgcolor = 1
    self.palette = []
    self.palette.append( bkgd.toLong() )
    self.palette.append( frgd.toLong() )
    self.setDefaultPenColor()

    tmparray = [ self.bgcolor ] * self.wd
    self.bitarray = [ tmparray[:] for i in range( self.ht ) ]
    self.currentPen = 1
    self.fontName = "%s-%d-%s" % ( "none", 0, "none" )
    
  def setDefaultPenColor( self ):
    self.currentPen = self.fgcolor
    
  def setPenColor( self, pcolor ):
    oldColor = self.currentPen
    # look for c in palette
    pcolornum = pcolor.toLong()
    try:
      self.currentPen = self.palette.index( pcolornum )
    except ValueError:
      if len( self.palette ) < 256 :
        self.palette.append( pcolornum )
        self.currentPen = len( self.palette ) - 1
      else:
        self.currentPen = self.fgcolor
    
    return Color.fromLong( self.palette[oldColor] )
    
  def getPenColor( self ):
    return Color.fromLong( self.palette[self.currentPen] )

  def plotPoint( self, x, y ):
    if ( 0 <= x < self.wd and 0 <= y < self.ht ):
      x = int(x)
      y = int(y)
      self.bitarray[y][x] = self.currentPen
      
  def drawRect( self, x, y, wid, ht, fill=False ):
    x = int(x)
    y = int(y)
    cury = y

    # subtract one for line width
    wid -= 1
    ht -= 1
    
    self.drawLine( x, y, x+wid, y )
    if fill:
      cury = y
      while cury < y+ht:
        self.drawLine( x, cury, x+wid, cury )
        cury += 1
    else:
      self.drawLine( x, y, x, y+ht )
      self.drawLine( x+wid, y, x+wid, y+ht )
    self.drawLine( x, y+ht, x+wid, y+ht )
    
  def drawSquare( self, x, y, wid, fill=False ):
    self.drawRect( x, y, wid, wid, fill )

  def bresLine(x,y,x2,y2):
    """Bresenham line algorithm"""
    steep = 0
    coords = []
    dx = int(abs(x2 - x)+0.5)
    if (x2 - x) > 0: 
      sx = 1
    else: 
      sx = -1
    dy = int(abs(y2 - y)+0.5)
    if (y2 - y) > 0: 
      sy = 1
    else: 
      sy = -1
    if dy > dx:
      steep = 1
      x,y = y,x
      dx,dy = dy,dx
      sx,sy = sy,sx
    dx2 = dx*2
    dy2 = dy*2
    d = dy2 - dx
    for i in range(0,dx):
      coords.append( (x,y) )
      while d >= 0:
        y += sy
        d -= dx2
      x += sx
      d += dy2

    if steep: #transpose x's and y's
      coords = [ (c[1],c[0]) for c in coords ]
    
    coords.append( (x2,y2) )
      
    return coords
  bresLine = staticmethod( bresLine )

  def _drawLine( self, x1, y1, x2, y2 ):
    # special checks for vert and horiz lines
    if ( x1 == x2 ):
      if 0 <= x1 < self.wd:
        if ( y2 < y1 ): 
          y1,y2 = y2,y1
        cury = max( y1, 0 )
        maxy = min( y2, self.ht-1 )
        while cury <= maxy :
          self.plotPoint( x1, cury )
          cury += 1
      return
      
    if ( y1 == y2 ):
      if ( 0 <= y1 < self.ht ):
        if ( x2 < x1 ):
          x1,x2 = x2,x1
        curx = max( x1, 0 )
        maxx = min( x2, self.wd-1 )
        while curx <= maxx:
          self.plotPoint( curx, y1 )
          curx += 1
      return

    for pt in BitMap.bresLine(x1, y1, x2, y2):
      self.plotPoint( pt[0], pt[1] )
  
  def _drawLines( self, lineSegs ):
    for x1,y1,x2,y2 in lineSegs:
      self._drawLine( x1, y1, x2, y2 )

  def drawLine( self, x1, y1, x2, y2, type=LINE_SOLID ):
    if type == BitMap.LINE_SOLID:
      self._drawLine( x1, y1, x2, y2 )
    elif type == BitMap.LINE_DASHED:
      # how many segs?
      len = hypot( x2-x1, y2-y1 )
      numsegs = len / BitMap._DASH_LEN
      dx = ( x2 - x1 ) / numsegs
      dy = ( y2 - y1 ) / numsegs
      dx2 = dx / 2.0
      dy2 = dy / 2.0
      if ( x2 < x1 ):
        x1,x2 = x2,x1
        y1,y2 = y2,y1
      segs = []
      curx = x1
      cury = y1
      for i in range( int(numsegs) ):
        segs.append( ( curx, cury, curx + dx2, cury + dy2 ) )
        curx += dx
        cury += dy
      if curx + dx2 > x2:
        segs.append( ( curx, cury, x2, y2 ) )
      else:
        segs.append( ( curx, cury, curx + dx2, cury + dy2 ) )
      self._drawLines( segs )
    elif type == BitMap.LINE_DOTTED:
      len = hypot( x2-x1, y2-y1 )
      numsegs = len / BitMap._DOT_LEN
      dx = ( x2 - x1 ) / numsegs
      dy = ( y2 - y1 ) / numsegs
      dx2 = dx / 2.0
      dy2 = dy / 2.0
      if ( x2 < x1 ):
        x1,x2 = x2,x1
        y1,y2 = y2,y1
      segs = []
      curx = x1
      cury = y1
      for i in range( int(numsegs) ):
        segs.append( ( curx, cury, curx + dx2, cury + dy2 ) )
        curx += dx
        cury += dy
      if curx + dx2 > x2:
        segs.append( ( curx, cury, x2, y2 ) )
      else:
        segs.append( ( curx, cury, curx + dx2, cury + dy2 ) )
      self._drawLines( segs )
    elif type == BitMap.LINE_DOT_DASH:
      len = hypot( x2-x1, y2-y1 )
      numsegs = len / BitMap._DOT_DASH_LEN
      dx = ( x2 - x1 ) / numsegs
      dy = ( y2 - y1 ) / numsegs
      dx3 = dx / 3.0
      dy3 = dy / 3.0
      dx23 = 0.62*dx
      dy23 = 0.62*dy
      dx56 = 0.78*dx
      dy56 = 0.78*dy
      if ( x2 < x1 ):
        x1,x2 = x2,x1
        y1,y2 = y2,y1
      segs = []
      curx = x1
      cury = y1
      for i in range( int(numsegs) ):
        segs.append( ( curx, cury, curx + dx3, cury + dy3 ) )
        segs.append( ( curx + dx23, cury + dy23, curx + dx56, cury + dy56  ) )
        curx += dx
        cury += dy
      if curx + dx3 > x2:
        segs.append( ( curx, cury, x2, y2 ) )
      else:
        segs.append( ( curx, cury, curx + dx3, cury + dy3 ) )
        if curx + dx23 < x2:
          if curx + dx56 > x2:
            segs.append( ( curx + dx23, cury + dy23, x2, y2 ) )
          else:
            segs.append( ( curx + dx23, cury + dy23, curx + dx56, cury + dy56  ) )
        else:
          pass #segs.append( ( curx, cury, curx + dx3, cury + dy3 ) )
      segs.append( ( curx, cury, x2, y2 ) )
      self._drawLines( segs )

  def drawCircle( self, cx, cy, r, fill=False ):
    x = 0
    y = r
    d = 1 - r
    
    self.plotPoint(cx, cy + y)
    self.plotPoint(cx, cy - y)
    if fill:
      self.drawLine(cx - y, cy, cx + y, cy)
    else:
      self.plotPoint(cx + y, cy)
      self.plotPoint(cx - y, cy)
    
    while( y > x ):
      if ( d < 0 ):
        d += ( 2*x + 3 )
      else:
        d += ( 2*(x-y) + 5 )
        y -= 1
      x += 1
      
      if fill:
        self.drawLine(cx + x - 1, cy + y, cx - x + 1, cy + y)
        self.drawLine(cx - x + 1, cy - y, cx + x - 1, cy - y)
        self.drawLine(cx + y - 1, cy + x, cx - y + 1, cy + x)
        self.drawLine(cx - y + 1, cy - x, cx + y - 1, cy - x)
      else:
        self.plotPoint(cx + x, cy + y)
        self.plotPoint(cx + y, cy + x)
        self.plotPoint(cx - x, cy - y)
        self.plotPoint(cx - y, cy - x)
        self.plotPoint(cx + x, cy - y)
        self.plotPoint(cx - y, cy + x)
        self.plotPoint(cx - x, cy + y)
        self.plotPoint(cx + y, cy - x)

  def _saveBitMapNoCompression( self ):
    line_padding = (4 - (self.wd % 4)) % 4
    
    # write bitmap header
    _bitmap = bytearray(b"BM")
    _bitmap += longToByteArray( 54 + self.ht*(self.wd*3 + line_padding) )   # DWORD size in bytes of the file
    _bitmap += longToByteArray( 0 )    # DWORD 0
    _bitmap += longToByteArray( 54  )
    _bitmap += longToByteArray( 40 )    # DWORD header size = 40
    _bitmap += longToByteArray( self.wd )    # DWORD image width
    _bitmap += longToByteArray( self.ht )    # DWORD image height
    _bitmap += shortToByteArray( 1 )    # WORD planes = 1
    _bitmap += shortToByteArray( 24 )    # WORD bits per pixel = 8
    _bitmap += longToByteArray( 0 )    # DWORD compression = 0
    _bitmap += longToByteArray( self.ht * (self.wd * 3 + line_padding) )    # DWORD sizeimage = size in bytes of the bitmap = width * height
    _bitmap += longToByteArray( 0 )    # DWORD horiz pixels per meter (?)
    _bitmap += longToByteArray( 0 )    # DWORD ver pixels per meter (?)
    _bitmap += longToByteArray( 0 )    # DWORD number of colors used = 256
    _bitmap += longToByteArray( 0 )    # DWORD number of "import colors = len( self.palette )

    # write pixels
    self.bitarray.reverse()
    for row in self.bitarray:
      for pixel in row:
        c = self.palette[pixel]
        _bitmap += long24ToByteArray(c)
      for i in range(line_padding):
        _bitmap += b"\x00"

    return _bitmap

    """
    f = file( filename, "wb" )
    
    line_padding = (4 - (self.wd % 4)) % 4
    
    # write bitmap header
    f.write( "BM" )
    #f.write( longToByteArray( 54 + 256*4 + self.ht*self.wd ) )   # DWORD size in bytes of the file
    f.write( longToByteArray( 54 + self.ht*(self.wd*3 + line_padding) ) )   # DWORD size in bytes of the file
    f.write( longToByteArray( 0 ) )    # DWORD 0
    #f.write( longToByteArray( 54 + 256*4 ) )    # DWORD offset to the data
    f.write( longToByteArray( 54  ) )
    f.write( longToByteArray( 40 ) )    # DWORD header size = 40
    f.write( longToByteArray( self.wd ) )    # DWORD image width
    f.write( longToByteArray( self.ht ) )    # DWORD image height
    f.write( shortToByteArray( 1 ) )    # WORD planes = 1
    f.write( shortToByteArray( 24 ) )    # WORD bits per pixel = 8
    f.write( longToByteArray( 0 ) )    # DWORD compression = 0
    f.write( longToByteArray( self.ht * (self.wd * 3 + line_padding) ) )    # DWORD sizeimage = size in bytes of the bitmap = width * height
    f.write( longToByteArray( 0 ) )    # DWORD horiz pixels per meter (?)
    f.write( longToByteArray( 0 ) )    # DWORD ver pixels per meter (?)
    f.write( longToByteArray( 0 ) )    # DWORD number of colors used = 256
    f.write( longToByteArray( 0 ) )    # DWORD number of "import colors = len( self.palette )

    # write pixels
    self.bitarray.reverse()
    for row in self.bitarray:
      print len(row)
      for pixel in row:
        c = self.palette[pixel]
        f.write( long24ToByteArray(c) )
      for i in range(line_padding):
        f.write( chr( 0 ) )
    
    # close file
    f.close()
    """
    
  def _saveBitMapWithCompression( self, filename ):
    """
    At the moment we don't support it
    """
    # open file
    f = file( filename, "wb" )
    
    # write bitmap header
    f.write( "BM" )
    f.write( longToByteArray( 54 + 256*4 + self.ht*self.wd ) )   # DWORD size in bytes of the file
    f.write( longToByteArray( 0 ) )    # DWORD 0
    f.write( longToByteArray( 54 + 256*4 ) )    # DWORD offset to the data
    f.write( longToByteArray( 40 ) )    # DWORD header size = 40
    f.write( longToByteArray( self.wd ) )    # DWORD image width
    f.write( longToByteArray( self.ht ) )    # DWORD image height
    f.write( shortToByteArray( 1 ) )    # WORD planes = 1
    f.write( shortToByteArray( 8 ) )    # WORD bits per pixel = 8
    f.write( longToByteArray( 1 ) )    # DWORD compression = 1=RLE8
    f.write( longToByteArray( self.wd * self.ht ) )    # DWORD sizeimage = size in bytes of the bitmap = width * height
    f.write( longToByteArray( 0 ) )    # DWORD horiz pixels per meter (?)
    f.write( longToByteArray( 0 ) )    # DWORD ver pixels per meter (?)
    f.write( longToByteArray( len(self.palette) ) )   # DWORD number of colors used = 256
    f.write( longToByteArray( len(self.palette) ) )    # DWORD number of "import colors = len( self.palette )

    # write bitmap palette 
    for clr in self.palette:
      f.write( longToByteArray( clr ) )
    for i in range( len(self.palette), 256 ):
      f.write( longToByteArray( 0 ) )
    
    # write pixels
    pixelBytes = 0
    self.bitarray.reverse()
    for row in self.bitarray:
      rleStart = 0
      curPixel = rleStart+1
      while curPixel < len(row):
        if row[curPixel] != row[rleStart] or curPixel-rleStart == 255:
          # write out from rleStart thru curPixel-1
          f.write( chr( curPixel-rleStart ) )
          f.write( chr( row[rleStart] ) )
          pixelBytes += 2
          rleStart = curPixel
        else:
          pass
        curPixel += 1
          
      # write out last run of colors
      f.write( chr( curPixel-rleStart ) )
      f.write( chr( row[rleStart] ) ) 
      pixelBytes += 2
      
      # end of line code
      f.write( chr(0) )
      f.write( chr(0) )
      pixelBytes += 2
    
    # end of bitmap code
    f.write( chr(0) )
    f.write( chr(1) )
    pixelBytes += 2

    # now fix sizes in header
    f.seek(2)
    f.write( longToByteArray( 54 + 256*4 + pixelBytes ) )   # DWORD size in bytes of the file
    f.seek(34)
    f.write( longToByteArray( pixelBytes ) )   # DWORD size in bytes of the file

    # close file
    f.close()
    
  def saveFile( self, filename, compress=False ):
    if compress:
      _b = self._saveBitMapWithCompression( filename )
    else:
      _b = self._saveBitMapNoCompression( )
    
    with open(filename, 'wb') as f:
        f.write(_b)
  
  def getBitmap(self, compress=False):
    _b = ''
    if  compress:
      print('Not yet implemented')
    else:
      _b = self._saveBitMapNoCompression()
    
    return _b


  def _drawFont(self, start_x, start_y, data):
    max_width = 0
    # empty font, like space
    if len(data) == 0:
      return (0, 0)

    start_y += data[0]
    for data_y in range(1, len(data)):
        
      # calculate maximum font width
      if len(data[data_y]) > max_width:
        max_width = len(data[data_y])
        
      for data_x in range(0, len(data[data_y])):
        #d_x = start_x * 3 + data_x * 3
        d_x = start_x + data_x
        if data[data_y][data_x] == '1':
          self.plotPoint(d_x, start_y + data_y)

    width = max_width
    height = len(data)

    return (width, height)

  def drawText(self, text, x, y):
    offset_x = 0
    offset_y = 0
    for idx in range(0, len(text)):
      (width, height) = self._drawFont(x + offset_x, y + offset_y, self.font[ord(text[idx])])
      offset_x += (width + 1)

  def setFont(self, font_data):
    self.font = font_data
  
  def loadImage(self, image):
    
    width = byteArrayToLong(image, 0x12)
    height = byteArrayToLong(image, 0x16)
    self.wd = width
    self.ht = height
    self.bgcolor = 0
    self.fgcolor = 0
    self.palette = []
    self.currentPen = 0
    
    bitarray = []
    bitarray.append([])
    
    row_idx = 0
    col_idx = 0
    idx_offset = byteArrayToLong(image, 0xa)
    idx = idx_offset
    line_padding = (4 - ( width % 4 ) ) % 4
    bytes_in_row = width*3 + line_padding
    
    while (idx+3) <= len(image):
      if col_idx >= width:
        # end of row, dismiss padding
        row_idx += 1
        idx += line_padding
        col_idx = 0
        if idx + 3 > len(image):
          break
        # add new row to image
        bitarray.append([])
       
      c = Color(ord(image[idx+2]), ord(image[idx+1]), ord(image[idx]))
      # register palette
      colorNum = c.toLong()
      try:
        self.currentPen = self.palette.index(colorNum)
      except ValueError:
        if len( self.palette ) < 256 :
          self.palette.append(colorNum)
          self.currentPen = len( self.palette ) - 1
        else:
          self.currentPen = self.fgcolor
      
      bitarray[row_idx].append(self.currentPen)
      idx += 3
      col_idx += 1
    
    # this is it
    bitarray.reverse()
    self.bitarray = bitarray
    
if __name__ == "__main__":
  
  # set test to run
  #  1 - line and shape drawing
  #  2 - text display
  test = 1
  if test == 1:
    """
    bmp.drawSquare( 0, 0, 400 )
    
    # draw variety of colors
    colors = [ Color.BLACK, Color.RED, Color.GREEN, Color.BLUE, \
               Color.CYAN, Color.MAGENTA, Color.YELLOW, Color.BLUE, \
               Color.DKRED, Color.DKGREEN, Color.DKBLUE, Color.TEAL, \
               Color.PURPLE, Color.BROWN, Color.GRAY ]
    for i,c in enumerate(colors):
      bmp.setPenColor( c )
      for j in range(8):
        bmp.drawRect( i*25, j*45, 25, 45, True )
        bmp.setPenColor( bmp.getPenColor().lighten() )
      bmp.setDefaultPenColor()
      bmp.drawRect( i*25, 0, 25, 360, False )
  
    # test drawing lines at various angles
    bmp.setPenColor( Color.WHITE )
    bmp.drawSquare( 10, 10, 380 )
    bmp.drawSquare(  9,  9, 382 )
    bmp.drawLine( 10, 10, 389, 389 )
    bmp.drawLine( 10, 10, 70, 389 )
    bmp.drawLine( 10, 10, 389, 70 )
    bmp.drawLine( 10, 389, 389, 10 )
    bmp.drawLine( 10, 389,  70, 10 )
    bmp.drawLine( 10, 70, 389, 10 )
  
    # test saving and restoring pen color
    saveColor = bmp.setPenColor( Color.DKGREEN )
    bmp.drawRect( 90, 100, 40, 30, fill=True )
    bmp.setPenColor( saveColor )
    bmp.drawRect( 95, 105, 30, 20, fill=True )
  
    # test drawing circles
    bmp.setPenColor( Color.DKRED )
    bmp.drawCircle( 250, 150, 40, fill=True )
    bmp.setPenColor( Color.WHITE )
    bmp.drawCircle( 250, 150, 25, fill=True )
    bmp.setPenColor( Color.BLUE )
    bmp.drawCircle( 250, 150, 20, fill=True )
    bmp.setPenColor( Color.WHITE )
    bmp.drawCircle( 250, 150, 18, fill=True )
    bmp.setPenColor( Color.BLUE )
    bmp.drawCircle( 250, 150, 8 )
    
    # test lines of different types
    bmp.setPenColor( Color.BLACK )
    bmp.drawLine( 10, 380, 389, 380, BitMap.LINE_DASHED )
    bmp.drawLine( 10, 373, 389, 373, BitMap.LINE_DOTTED )
    bmp.drawLine( 10, 365, 389, 365, BitMap.LINE_DOT_DASH )
    bmp.drawLine( 10, 358, 389, 325, BitMap.LINE_DASHED )
    bmp.drawLine( 10, 353, 389, 320, BitMap.LINE_DOTTED )
    bmp.drawLine( 10, 348, 389, 315, BitMap.LINE_DOT_DASH )
  """
  
  import bmpfont_arial_12 as font
  bmp = BitMap( 500, 40, Color.WHITE )
  bmp.setFont(font.font_data)
  bmp.setPenColor( Color.BLUE )
  bmp.drawText('abcdefghijklmnoprstuvxyz1234567890ABCDEFGHIJKLMNOPRSTUVXYZ!@#$^%&^**()_}{\",.?<>', 10, 10)
  bmp.drawLine( 0, 0, 10, 10)
  
  bmp.saveFile( "test.bmp" )
  #bmp.saveFile( "C:\\temp\\test_nocompress.bmp", compress=False )
