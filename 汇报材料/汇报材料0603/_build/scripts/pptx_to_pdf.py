"""Convert pptx to PDF via PowerPoint COM (Windows-only)."""
from __future__ import annotations
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
PPTX = BUILD.parent / "20260603_项目进展汇报_v2.pptx"
PDF = BUILD.parent / "20260603_项目进展汇报_v2.pdf"

if not PPTX.exists():
    print(f"[ERR] pptx not found: {PPTX}")
    sys.exit(1)

if PDF.exists():
    try:
        PDF.unlink()
    except Exception as e:
        print(f"[ERR] cannot remove existing PDF: {e}")
        sys.exit(1)

# Use pywin32 to drive PowerPoint
try:
    import win32com.client as win32
    import pythoncom
except Exception as e:
    print(f"[ERR] pywin32 import failed: {e}")
    sys.exit(1)

pythoncom.CoInitialize()
ppt = None
deck = None
try:
    ppt = win32.DispatchEx("PowerPoint.Application")
    # Cannot set Visible=False reliably on all PowerPoint versions; use MsoTriStateTrue
    try:
        ppt.Visible = 1
    except Exception:
        pass
    deck = ppt.Presentations.Open(str(PPTX), WithWindow=False)
    # 32 = ppSaveAsPDF
    deck.SaveAs(str(PDF), 32)
    time.sleep(1.0)
    deck.Close()
    ppt.Quit()
    print(f"[OK] wrote {PDF}")
except Exception as e:
    print(f"[ERR] PowerPoint conversion failed: {e}")
    try:
        if deck is not None:
            deck.Close()
        if ppt is not None:
            ppt.Quit()
    except Exception:
        pass
    sys.exit(2)
finally:
    pythoncom.CoUninitialize()
