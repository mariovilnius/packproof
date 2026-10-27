"""PackProof: minimal, marker-based order verification prototype."""
import base64
from collections import Counter
from pathlib import Path
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template_string

ROOT = Path(__file__).parent
PRODUCTS = {1: 'White bottle', 2: 'Dropper bottle', 3: 'Cream jar'}
DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

def verify(image):
    corners, ids, _ = cv2.aruco.ArucoDetector(DICTIONARY).detectMarkers(image)
    counts = Counter([] if ids is None else ids.flatten().tolist())
    rows = [{'name': name, 'expected': 1, 'detected': counts[i]} for i, name in PRODUCTS.items()]
    unknown = {str(i): n for i, n in counts.items() if i not in PRODUCTS}
    passed = all(row['detected'] == 1 for row in rows) and not unknown
    annotated = image.copy()
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(annotated, corners, ids)
    ok, encoded = cv2.imencode('.jpg', annotated)
    if not ok:
        raise ValueError('Cannot encode image')
    return {'verified': passed, 'items': rows, 'unexpected': unknown,
            'message': 'Order verified' if passed else 'Check missing, extra or unexpected items; reposition labels and check again.',
            'image': base64.b64encode(encoded).decode()}

@app.get('/')
def home():
    return render_template_string(PAGE)

@app.post('/verify')
def inspect():
    sample = request.form.get('sample')
    if sample:
        if sample not in {'complete', 'missing', 'unexpected'}:
            return jsonify(error='Unknown sample'), 400
        data = (ROOT / 'samples' / (sample + '.png')).read_bytes()
    else:
        upload = request.files.get('image')
        if not upload:
            return jsonify(error='Select an image'), 400
        data = upload.read()
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR) if data else None
    if image is None:
        return jsonify(error='Invalid image'), 400
    if image.shape[0] * image.shape[1] > 20_000_000:
        return jsonify(error='Image too large; use at most 20 megapixels'), 400
    return jsonify(verify(image))

PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PackProof prototype</title><style>body{font:17px system-ui;background:#10263d;color:#edf7fa;max-width:1100px;margin:40px auto;padding:20px}h1{font-size:48px;margin-bottom:0;color:#22d4bd}button,input{padding:13px;margin:8px 8px 8px 0}button{background:#22d4bd;border:0;border-radius:8px;cursor:pointer}section{background:#19364e;padding:24px;border-radius:16px;margin:20px 0}img{max-width:100%;border-radius:12px}table{width:100%;text-align:left}td,th{padding:12px;border-bottom:1px solid #426077}.note{color:#b5cbd8}#status{font-size:24px}</style>
<h1>PackProof</h1><p>Check every order before the box is sealed.</p><p class="note">Working marker-based prototype · OpenCV 4.13 · Local processing · AWS not deployed</p>
<section><h2>Order #1042</h2><p>Expected: 1 white bottle, 1 dropper bottle, 1 cream jar.</p><p>Attach ArUco labels 1, 2 and 3 to the corresponding products. Keep all labels visible in one photograph.</p>
<form id="upload"><input type="file" name="image" accept="image/*" required><button>Check image</button></form>
<p>Synthetic test scenes:</p><button onclick="sample('complete')">Complete order</button><button onclick="sample('missing')">Missing item</button><button onclick="sample('unexpected')">Unexpected item</button></section>
<section aria-live="polite"><h2 id="status">Ready to check</h2><div id="results"></div><img id="preview" alt="Annotated detection result" hidden></section>
<p class="note">This demo detects printed markers, not product appearance. A hidden or unreadable label may appear missing. It does not track packing over time or prove physical contents.</p>
<script>async function run(data){let s=document.getElementById('status');s.textContent='Checking…';try{let response=await fetch('/verify',{method:'POST',body:data});let r=await response.json();if(!response.ok)throw Error(r.error||'Request failed');s.textContent=r.message;s.style.color=r.verified?'#22d4bd':'#ffca70';let box=document.getElementById('results');box.replaceChildren();let table=document.createElement('table');for(let row of [['Product','Expected','Detected'],...r.items.map(x=>[x.name,x.expected,x.detected])]){let tr=document.createElement('tr');for(let value of row){let td=document.createElement('td');td.textContent=value;tr.append(td)}table.append(tr)}box.append(table);if(Object.keys(r.unexpected).length){let p=document.createElement('p');p.textContent='Unexpected marker counts: '+JSON.stringify(r.unexpected);box.append(p)}let img=document.getElementById('preview');img.src='data:image/jpeg;base64,'+r.image;img.hidden=false}catch(e){s.textContent=e.message}}document.getElementById('upload').onsubmit=e=>{e.preventDefault();run(new FormData(e.target))};function sample(name){let d=new FormData();d.set('sample',name);run(d)}</script></html>'''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
