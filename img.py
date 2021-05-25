from tkinter import *

imagelist = {
  'im1': ['imgs\\1b.gif', None],
  'im2': ['imgs\\1bk.gif', None],
  'im3': ['imgs\\1h.gif', None],
  'im4': ['imgs\\1hk.gif', None]
    }


def get(name):
  if name in imagelist:
    if imagelist[name][1] is None:
      imagelist[name][1] = PhotoImage(file=imagelist[name][0])
    return imagelist[name][1]
  return None
