#!/usr/bin/env python

import sys
import time
from Tkinter import *

from multiprocessing import Process, Queue
from datetime import datetime
import time
import sys

def sized_frame(master, height, width):
   F = Frame(master, height=height, width=width)
   F.pack_propagate(0)
   return F

class OverlayView(Canvas):
  def __init__(self, parent, mgr, mask, version):
    Canvas.__init__(self, parent)

    self.parent = parent
    self.root = parent
    self.mgr = mgr
    self.mask = mask
    self.version = version

    self.mgr.setBlackScore(7)
    self.mgr.setWhiteScore(12)

    self.init_ui()

  def init_ui(self):
    self.parent.title("TimeShark Scores")
    self.pack(fill=BOTH, expand=1)

    self.w = self.root.winfo_screenwidth()
    self.h = self.root.winfo_screenheight()

    self.refresh = 100
    self.t = 0
    def draw(self):
      self.delete(ALL)
      if self.mask:
        self.clear(fill="#000000")
      else:
        self.clear(fill="#054a91")
      self.render()
      self.update()
      self.t += 10
      self.mgr.setGameClock(self.t)
      self.after(self.refresh, lambda : draw(self))
    self.after(1, lambda : draw(self))

  def clear(self, fill):
    self.create_rectangle((0, 0, self.w, self.h), fill=fill)

  def round_rectangle(self, bbox, radius, fill):
    x1, y1, x2, y2 = bbox
    self.create_oval((x1 - radius, y1, x1 + radius, y2), fill=fill, outline=fill)
    self.create_oval((x2 - radius, y1, x2 + radius, y2), fill=fill, outline=fill)
    self.create_rectangle(bbox, fill=fill, outline=fill)

  def render(self):
    {
      "center" : self.render_top_center
    }.get(self.version, self.render_top_center)()

  def color(self, name):
    if self.mask:
      return "#000000" if name == "bg" else "#ffffff"

    return {
      "border" : "#ffffff",
      "fill" : "#2e96ff",
      "fill_text" : "#ffffff",
      "black_fill" : "#000000",
      "black_text" : "#2e96ff",
      "white_fill" : "#ffffff",
      "white_text" : "#2e96ff"
    }.get(name, "#ff0000")

  def render_top_center(self):
    # Bounding box (except for ellipses)
    overall_width = 320
    overall_height = 40

    # Top left coords
    x1 = self.w / 2 - overall_width / 2
    y1 = overall_height / 2 + 10
    x2 = x1 + overall_width
    y2 = y1 + overall_height

    score_width = 50

    inset = 30
    radius = 15
    wing_size = 200
    outset = 2
    font=("Menlo", 30)
    logo_font=("Menlo", 30)
    time_font=("Menlo", 30)

    # Border
    self.round_rectangle(bbox=(x1 - wing_size - outset, y1 - outset,
                              x2 + wing_size + outset, y2 + outset),
                         radius=radius, fill=self.color("border"))

    # Middle Section
    self.create_rectangle((x1, y1, x2, y2), fill=self.color("fill"),
                          outline=self.color("fill"))

    # Left Wing
    self.round_rectangle(bbox=(x1 - wing_size, y1, x1, y2),
                         radius=radius, fill=self.color("fill"))

    # Right Wing
    self.round_rectangle(bbox=(x2, y1, x2 + wing_size, y2),
                         radius=radius, fill=self.color("fill"))

    # White Score
    self.round_rectangle(bbox=(x1, y1, x1 + score_width, y1 + overall_height),
                         radius=radius, fill=self.color("white_fill"))
    # Black Score
    self.round_rectangle(bbox=(x2 - score_width, y1, x2, y1 + overall_height),
                         radius=radius, fill=self.color("black_fill"))

    if not self.mask:
      # White Score Text
      white_score = self.mgr.whiteScore()
      w_score="%d" % (white_score,)
      self.create_text((x1 + score_width / 2, y1 + overall_height / 2),
                       text=w_score, fill=self.color("white_text"),
                       font=font)

      # Black Score Text
      black_score = self.mgr.blackScore()
      b_score="%d" % (black_score,)
      self.create_text((x2 - score_width / 2, y1 + overall_height / 2),
                       text=b_score, fill=self.color("black_text"),
                       font=font)

      # Logo
      wall_time = int(round(time.time() * 1000))
      logo_text = "Timeshark"
      self.create_text((x1 + overall_width / 2, y1 + overall_height / 2),
                      text=logo_text, fill=self.color("fill_text"),
                      font=logo_font)

      # Game State Text
      state_text="1st Half"
      self.create_text((x1 - wing_size / 2, y1 + overall_height / 2),
                      text=state_text, fill=self.color("fill_text"), font=font)

      # Game Clock Text
      clock_time = self.mgr.gameClock()
      clock_text = "%2d:%02d" % (clock_time // 60, clock_time % 60)
      self.create_text((x2 + wing_size / 2, y1 + overall_height / 2),
                      text=clock_text, fill=self.color("fill_text"), font=time_font)

def Overlay(mgr, mask, version):
  root = Tk()
  ov = OverlayView(root, mgr, mask, version)
  # make it cover the entire screen
  w, h = root.winfo_screenwidth(), root.winfo_screenheight()
  root.geometry("%dx%d-0+0" % (w, h))
  root.attributes('-fullscreen', True)
  return ov
