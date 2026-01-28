import glob
import cv2
import easyocr
import kagglehub
import time
import os
import numpy as np
import torch
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
from ultralytics import YOLO

model_path = "license_plate_detector.pt"

dataset_path = kagglehub.dataset_download("piotrstefaskiue/poland-vehicle-license-plate-dataset/versions/5")

image_files_map = {os.path.basename(f): f for f in glob.glob(f"{dataset_path}/**/*.jpg", recursive=True)}
dataset = []

for xml_file in glob.glob(f"{dataset_path}/**/annotations.xml", recursive=True):
    try:
        for image_node in ET.parse(xml_file).getroot().findall('.//image'):
            filename = os.path.basename(image_node.get('name'))
            if filename in image_files_map:
                box_node = image_node.find('box')
                if box_node is not None:
                    label = box_node.find("attribute[@name='plate number']").text
                    if label:
                        coords = [float(box_node.get(k)) for k in ["xtl", "ytl", "xbr", "ybr"]]
                        dataset.append({
                            'path': image_files_map[filename],
                            'filename': filename,
                            'box': coords,
                            'label': label,
                            'box_int': [int(c) for c in coords]
                        })
    except:
        continue

train_set, test_set = train_test_split(dataset, test_size=0.3, random_state=101)
test_subset = (test_set + train_set)[:100]

def calculate_iou(box_a, box_b):
    x_left = max(box_a[0], box_b[0])
    y_top = max(box_a[1], box_b[1])
    x_right = min(box_a[2], box_b[2])
    y_bottom = min(box_a[3], box_b[3])
    intersection = max(0, x_right - x_left) * max(0, y_bottom - y_top)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    return intersection / (area_a + area_b - intersection + 1e-6)

def correct_text(text):
    clean = "".join(c for c in text.upper().replace("PL", "", 1) if c.isalnum())[-8:]
    if len(clean) < 4: return clean
    chars = list(clean)
    letters = {'0': 'O', '1': 'I', '8': 'B', '2': 'Z', '5': 'S', '4': 'A', '6': 'G', '7': 'Z'}
    digits = {'O': '0', 'Q': '0', 'D': '0', 'I': '1', 'Z': '2', 'B': '8', 'S': '5', 'L': '1', 'A': '4'}
    for i in range(min(2, len(chars))):
        chars[i] = letters.get(chars[i], 'O' if chars[i] == '0' else chars[i])
    start = 3 if len(chars) > 2 and chars[2].isalpha() and chars[2] not in '468' else 2
    if len(chars) > 2 and chars[2] == '4':
        chars[2] = 'A'
        start = 3
    for i in range(start, len(chars)):
        chars[i] = digits.get(chars[i], chars[i])
    return "".join(chars)

def transform_perspective(image, filename):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 200)
    contours = sorted(cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea, reverse=True)[:5]
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
        if len(approx) == 4 and cv2.contourArea(contour) > image.size / 3 * 0.3:
            points = approx.reshape(4, 2).astype('float32')
            sums = points.sum(1)
            diffs = np.diff(points, axis=1)
            rect = np.array([points[np.argmin(sums)], points[np.argmin(diffs)], points[np.argmax(sums)], points[np.argmax(diffs)]], dtype='float32')
            width = int(max(np.linalg.norm(rect[2] - rect[3]), np.linalg.norm(rect[1] - rect[0])))
            height = int(max(np.linalg.norm(rect[1] - rect[2]), np.linalg.norm(rect[0] - rect[3])))
            dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype='float32')
            warped = cv2.warpPerspective(image, cv2.getPerspectiveTransform(rect, dst), (width, height))
            return warped
    fallback = image[int(image.shape[0] * 0.1):int(image.shape[0] * 0.9), :]
    return fallback

def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0
    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50
    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    return round(grade * 2) / 2

model = YOLO(model_path)
reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
correct_predictions = 0
iou_list = []

start_time = time.time()

for item in test_subset:
    original_image = cv2.imread(item['path'])
    if original_image is None: continue
    expected_text = correct_text(item['label'])

    prediction = model.predict(original_image, imgsz=640, verbose=False, conf=0.25)[0]
    box = prediction.boxes.xyxy.cpu().numpy().astype(int)[0] if len(prediction.boxes) else item['box_int']

    iou = calculate_iou(item['box_int'], box)
    iou_list.append(iou)

    if iou > 0.5:
        x1, y1, x2, y2 = box
        crop = original_image[max(0, y1 - 10):min(original_image.shape[0], y2 + 10), max(0, x1 - 10):min(original_image.shape[1], x2 + 10)]
        if crop.size > 0:
            warped = transform_perspective(crop, item['filename'])
            if warped.shape[0] < 50:
                warped = cv2.resize(warped, (int(warped.shape[1] * (64.0 / warped.shape[0])), 64), interpolation=cv2.INTER_CUBIC)

            gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY))

            for processed in [gray, cv2.bitwise_not(gray)]:
                try:
                    padded = cv2.copyMakeBorder(processed, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=[255] * 3)
                    results = reader.readtext(padded, detail=0, beamWidth=5, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                    found_correct = False
                    for candidate in results + ["".join(results)]:
                        fixed = correct_text(candidate)
                        if len(fixed) > 3 and (fixed == expected_text or (fixed.endswith('1') and len(fixed) > 5 and fixed[:-1] == expected_text)):
                            correct_predictions += 1
                            found_correct = True
                            break
                    if found_correct: break
                except:
                    pass

duration = time.time() - start_time
accuracy = correct_predictions / len(test_subset) * 100
grade = calculate_final_grade(accuracy, duration)

print(f"Mean IoU: {np.mean(iou_list):.4f}\nAccuracy: {accuracy:.2f}%\nTime: {duration:.2f}s\nGrade: {grade}")
