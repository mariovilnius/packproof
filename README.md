# PackProof

A minimal working prototype for checking packed orders from a photograph using printed ArUco product labels and OpenCV.

## Status and limitations

Implemented: image upload, real marker detection, quantity comparison, annotated results, complete/missing/unexpected synthetic samples, printable markers, automated tests.

This is **marker-based verification**, not appearance-based AI product recognition. All labels must be visible in a single image. Markers identify labels, not independently confirmed physical products. There is no video tracking, model training, confidence calibration or production validation.

**Uses OpenCV 4.13, not OpenCV 5. AWS is not integrated or deployed. Therefore this source does not yet satisfy the competition's OpenCV 5 and meaningful AWS requirements.** Concept gallery visuals are separate from this working prototype.

## Run (Python 3.12 recommended)

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python generate_samples.py
python app.py
```

Open http://127.0.0.1:5000. This is a local development server, not a production deployment.

## Test

```sh
python -m unittest -v
```

Click Complete order: all three products must show 1 and the order must pass. Click Missing item: cream jar must show 0 and the order must fail. Click Unexpected item: unknown marker 4 must be reported and the order must fail. Upload samples or your own photograph of printed labels from `markers/`.

Order #1042 expects marker 1 (white bottle), marker 2 (dropper bottle), marker 3 (cream jar), one of each. Repeated visible markers count as multiple items. Keep labels separate, flat and adequately lit. Unknown valid markers fail verification. Unreadable objects cannot be identified and may not be reported as unexpected.

## Architecture

Browser upload -> Flask endpoint -> OpenCV ArUco detector (DICT_4X4_50) -> count labels -> compare expected quantities -> JSON and annotated JPEG -> browser.

Images are processed in memory and not retained. Maximum upload is 8 MB. Run only locally; production hardening, authentication and stricter image resource limits remain future work.

## Next steps

Validate OpenCV 5 compatibility, add opt-in AWS S3 evidence storage and deploy a meaningful processing component on AWS; collect real packing images; evaluate occlusion and lighting; consider product appearance recognition.

Detector reference: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
