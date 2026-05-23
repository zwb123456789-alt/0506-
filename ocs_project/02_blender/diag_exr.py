# -*- coding: utf-8 -*-
"""诊断：检查 Normal EXR 实际像素值"""
import sys
import OpenEXR
import Imath
import numpy as np

path = sys.argv[1]
exr = OpenEXR.InputFile(path)
hdr = exr.header()
print("Channels:", list(hdr["channels"].keys()))
dw = hdr["dataWindow"]
w = dw.max.x - dw.min.x + 1
h = dw.max.y - dw.min.y + 1
print(f"Size: {w}x{h}")

for ch in hdr["channels"].keys():
    raw = exr.channel(ch, Imath.PixelType(Imath.PixelType.FLOAT))
    arr = np.frombuffer(raw, dtype=np.float32).reshape(h, w)
    print(f"  {ch}: min={arr.min():.4f} max={arr.max():.4f} mean={arr.mean():.4f} nonzero={np.sum(arr != 0)}/{arr.size}")
