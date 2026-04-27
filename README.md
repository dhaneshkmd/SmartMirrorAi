# Smart Mirror - Beauty & Style Assistant

Version 1.0 prototype based on the software development report dated 27 April 2026.

This is a runnable Python prototype of the Smart Mirror software architecture. It keeps the heavy computer vision and virtual try-on models behind module boundaries, while providing working demo flows for:

- face scan and makeup plan
- cosmetic product scanning
- dress match percentage and styling suggestions
- outfit history storage
- mirror-style web dashboard

The server uses only the Python standard library so it can run in simple student/project environments. A production version can replace `smart_mirror/server.py` with Flask while keeping the modules intact.

## Project Structure

```text
smart_mirror/
  database.py                 SQLite storage and seed data
  server.py                   HTTP API and static file server
  modules/
    face_analysis.py          Face attribute model and demo analyzer
    makeup_recommendation.py  Rule-based makeup plan generator
    product_scanner.py        Barcode/OCR product lookup
    virtual_try_on.py         Outfit matching and styling engine
static/
  index.html                  Kiosk dashboard
  styles.css                  Mirror UI styles
  app.js                      Frontend API calls
api/
  face/analyze.js             Vercel face scan endpoint with Gemini support
run.py                        App launcher
requirements.txt              Optional production dependencies
```

## Run

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

If Python is not on your PATH, install Python 3.10+ first.

## Deploy on Vercel

The project includes a root `index.html`, so Vercel can display the dashboard at `/`.

For a simple upload deployment, include these paths:

```text
index.html
vercel.json
static/
api/
```

Set this Vercel environment variable for Gemini-powered scan suggestions:

```text
Smart_Mirror_API_Key
```

The camera runs in the browser with `getUserMedia`. Gemini calls run only from the Vercel API route so the key is not exposed in frontend JavaScript. The local Python backend remains available when you run `python run.py` on your computer.

## Demo API

Face analysis:

```bash
curl -X POST http://127.0.0.1:5000/api/face/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"skin_tone\":\"medium\",\"undertone\":\"warm\",\"face_shape\":\"round\"}"
```

Product scan:

```bash
curl -X POST http://127.0.0.1:5000/api/product/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"barcode\":\"8901030970001\"}"
```

Dress matching:

```bash
curl -X POST http://127.0.0.1:5000/api/try-on/match ^
  -H "Content-Type: application/json" ^
  -d "{\"dominant_color\":\"coral\",\"occasion\":\"party\",\"dress_cut\":\"a-line\"}"
```

## Production Upgrade Notes

- Replace demo face attributes with OpenCV + MediaPipe Face Mesh outputs.
- Replace product seed data with Open Beauty Facts and Barcode Lookup API calls.
- Replace static dress scoring with garment parsing and CP-VTON+/cloud VTON output.
- Add authentication and encrypted image transfer before enabling cloud processing.
