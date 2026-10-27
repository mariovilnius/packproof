from pathlib import Path
import cv2
import numpy as np
from app import DICTIONARY

ROOT = Path(__file__).parent
def scene(ids):
    image = np.full((600, 1100, 3), 245, np.uint8)
    cv2.putText(image, 'SYNTHETIC TEST SCENE - printed product labels', (25, 45), cv2.FONT_HERSHEY_SIMPLEX, .8, (30, 50, 60), 2)
    for j, marker_id in enumerate(ids):
        x = 55 + j * 260
        marker = cv2.aruco.generateImageMarker(DICTIONARY, marker_id, 180)
        image[180:360, x:x+180] = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
        cv2.putText(image, f'ID {marker_id}', (x, 410), cv2.FONT_HERSHEY_SIMPLEX, 1, (30, 50, 60), 2)
    return image

def generate():
    (ROOT/'samples').mkdir(exist_ok=True)
    (ROOT/'markers').mkdir(exist_ok=True)
    for name, ids in {'complete':[1,2,3], 'missing':[1,2], 'unexpected':[1,2,3,4]}.items():
        cv2.imwrite(str(ROOT/'samples'/f'{name}.png'), scene(ids))
    for i in [1,2,3,4]:
        marker = cv2.aruco.generateImageMarker(DICTIONARY, i, 400)
        cv2.imwrite(str(ROOT/'markers'/f'product-{i}.png'), cv2.copyMakeBorder(marker,60,60,60,60,cv2.BORDER_CONSTANT,value=255))

if __name__ == '__main__': generate()
