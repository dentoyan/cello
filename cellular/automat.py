# -*- coding: utf-8 -*-

__version__= "1.0.0"
__author__ = "Joshua Dentoyan<schabbesgoy@gmx.net>"
__about =  "cello module, version %s,\nwritten by %s, August, 2013" % (__version__, __author__)

"""
automat.py - module for constructing simple cellular automata

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

import copy, string

class CA(object):
    ''' Cellular Automata '''

    def __init__(self, x, y, breed=6, death=4):
      assert(x and y)
      self.X = x
      self.Y = y
      self.Db = breed
      self.Dd = death
      self.v = [0 for x in range(self.X * self.Y)]
      self.n = copy.copy(self.v)
      self.o = copy.copy(self.v)
      for i in range(-1,2):
	self.v[self.idx(self.X / 2 + i, self.Y / 2)] = 1
	self.v[self.idx(self.X / 2, self.Y / 2 + i)] = 1

    def idx(self, x, y): 
      return y * self.X + x

    def N(self):
      for x in range(self.X):
        for y in range(self.Y):
          self.n[self.idx(x, y)] = 0
          for i in range(-1, 2):
	    for j in range(-1, 2):
	      if x+i>=0 and x+i<self.X and y+j>=0 and \
	        y+j<self.Y and not (i==0 and j == 0):
		  if self.v[self.idx(x+i, y+j)]:
		    self.n[self.idx(x, y)] += 1

    def B(self):
      self.N()
      for x in range(self.X):
        for y in range(self.Y):
	  idx = self.idx(x, y)
          if not self.v[idx]:
            if self.n[idx] > 1 and self.n[idx] < self.Db:
              self.v[idx] = 1
                     
    def D(self):
      self.N()
      for x in range(self.X):
        for y in range(self.Y):
	  idx = self.idx(x, y)
          if self.v[idx]:
            if self.n[idx] > self.Dd:
              self.v[idx] = 0

    def P(self):
      s = [ '-'  for r in range(self.X)]
      print string.join(s)
      for y in range(self.Y):
        op = [ ' '  for r in range(self.X)]
	idx = self.idx(0, y)
        for x in range(self.X):
          if vi[idx + x]:
            op[x] = "*"
        print string.join(op)

    def C(self):	
      r = self.v == self.o 
      self.o = copy.copy(self.v)
      return not r

    def Cycle(self):
      self.B()
      self.D()
      return self.C()


