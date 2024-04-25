#!/usr/bin/python3

# -*- coding: latin-1 -*-

__version__= "1.0.0"
__author__ = "Joshua Dentoyan<schabbesgoy@gmx.net>"
__about =  "cello module, version %s,\nwritten by %s, August, 2013" % (__version__, __author__)

"""
cello.py - program to construct a series of cellular automata

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

import sys, re, string, os, filecmp, bmp.bmp 
from optparse import OptionParser
from cellular.automat import CA


VERSION = "%prog - version " + __version__
USAGE = "usage: %prog [parameter]"

def Parser():
    parser = OptionParser(version=VERSION, usage=USAGE)
    parser.add_option("-x", dest="x", default=25, help="width")
    parser.add_option("-y", dest="y", help="height")
    parser.add_option("-b", "--breed", dest="b", default=7, 
		    help="breed on lower neighbors")
    parser.add_option("-d", "--death", dest="d", default=6, 
		    help="max neighbors")
    parser.add_option("-a", "--about", dest= 'about', action="store_true", 
                    help="about the program")
    return parser


def ExportBmp(co, no):
  name = "bitmaps/cello_%dx%d-b%dd%d_%d" % \
    (co.X, co.Y, co.Db, co.Dd, no)
  cy = co.Y
  cx = co.X
  bm = bmp.bmp.BitMap(cx * 10, cy * 10, bmp.bmp.Color.WHITE)
  bm.setPenColor(bmp.bmp.Color.BLUE)
  for y in range(cy):
    for x in range(cx):
      if co.v[co.idx(x, y)]:
        bm.drawSquare(x * 10, y * 10, 10, True)
  tfile = name + ".tmp"
  bfile = name + ".bmp"
  bm.saveFile(tfile)
  if ExistingFile(tfile):
    os.remove(tfile)
    return False
  else:
    os.rename(tfile, bfile)
    return True
    
def ExistingFile(tfile):
  for r,d,f in os.walk("bitmaps"):
      for files in f:
        if files.endswith(".bmp"):
            bfile = os.path.join(r,files)
            if filecmp.cmp(tfile, bfile, False):
                return True
  return False
             
def RemoveBitmaps():
  for r,d,f in os.walk("bitmaps"):
      for files in f:
        if files.endswith(".bmp"):
            bfile = os.path.join(r,files)
            os.remove(bfile)

             
def C1(ca):
  print("%d:%d" % (ca.X, ca.Y))
  s = ["=O=" for r in range(20)]
  sep = ''.join(s)
  print(sep)
  no = 0
  while ca.Cycle():
      #co.P()	
      no = no + 1
      if not ExportBmp(ca, no):
        return
      print(no)
  print(sep)

    
def main():
  parser = Parser()
  options, args = parser.parse_args()
  if options.about:
    print(__about)
    return 0
  x = int(options.x)
  y = int(options.y) if options.y else int(options.x)
  if x % 2 == 0:
    print("warning x is not odd")
  if y % 2 == 0:
    print("warning y is not odd")
  ca = CA(x, y, int(options.b), int(options.d))
  RemoveBitmaps()
  C1(ca)
    
    
if __name__ == "__main__":
  sys.exit(main())
    
    
    
    
    
    
    
    


