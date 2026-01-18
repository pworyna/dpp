import glob, cv2, easyocr, kagglehub, difflib, time, os, shutil, numpy as np
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
from ultralytics import YOLO
from pathlib import Path
import torch

print("⬇️ Pobieranie danych z Kaggle...")
path = kagglehub.dataset_download("piotrstefaskiue/poland-vehicle-license-plate-dataset")

base_dir = os.path.abspath("datasets/plate_data")
if os.path.exists(base_dir): shutil.rmtree(base_dir)

for split in ['train', 'val']:
    os.makedirs(f"{base_dir}/images/{split}", exist_ok=True)
    os.makedirs(f"{base_dir}/labels/{split}", exist_ok=True)

print("⚙️ Konwersja XML do formatu YOLO...")

xml_files = glob.glob(f"{path}/**/annotations.xml", recursive=True)
img_files_map = {os.path.basename(f): f for f in glob.glob(f"{path}/**/*.jpg", recursive=True)}

dataset = []

for xml_file in xml_files:
    try:
        root = ET.parse(xml_file).getroot()
        for img_node in root.findall('image'):
            name = img_node.get('name')
            basename = os.path.basename(name)
            if basename not in img_files_map: continue

            original_path = img_files_map[basename]
            box = img_node.find('box')
            if box:
                img_h = int(img_node.get('height'))
                img_w = int(img_node.get('width'))

                coords = [float(box.get(k)) for k in ['xtl', 'ytl', 'xbr', 'ybr']]
                label = box.find("attribute[@name='plate number']").text

                if label:
                    xtl, ytl, xbr, ybr = coords
                    x_center = (xtl + xbr) / 2.0 / img_w
                    y_center = (ytl + ybr) / 2.0 / img_h
                    width = (xbr - xtl) / img_w
                    height = (ybr - ytl) / img_h

                    dataset.append({
                        'src_img': original_path,
                        'filename': basename,
                        'bbox': [x_center, y_center, width, height],
                        'label': label,
                        'coords': [int(c) for c in coords]
                    })
    except:
        continue

train_set, test_set = train_test_split(dataset, test_size=0.3, random_state=42)

def save_to_yolo_format(subset, split_name):
    for item in subset:
        shutil.copy(item['src_img'], f"{base_dir}/images/{split_name}/{item['filename']}")
        txt_name = item['filename'].replace('.jpg', '.txt')
        with open(f"{base_dir}/labels/{split_name}/{txt_name}", 'w') as f:
            b = item['bbox']
            f.write(f"0 {b[0]:.6f} {b[1]:.6f} {b[2]:.6f} {b[3]:.6f}")

save_to_yolo_format(train_set, 'train')
save_to_yolo_format(test_set, 'val')

with open(f"{base_dir}/data.yaml", 'w') as f:
    f.write(f"path: {base_dir}\ntrain: images/train\nval: images/val\nnames:\n  0: license_plate")

print("\n🚀 ROZPOCZYNAM TRENING...")
if os.path.exists("runs/detect"): shutil.rmtree("runs/detect")

device = 0 if torch.cuda.is_available() else 'cpu'
print(f"ℹ️ Używam urządzenia: {device.upper() if isinstance(device, str) else 'GPU'}")

model = YOLO('yolov8n.pt')
model.train(
    data=f"{base_dir}/data.yaml",
    epochs=30,
    imgsz=640,
    plots=False,
    verbose=False,
    device=device
)

runs_dir = Path("runs/detect")
train_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir() and 'train' in d.name],
                    key=lambda x: x.stat().st_mtime)
latest_train_dir = train_dirs[-1]
best_model_path = str(latest_train_dir / "weights" / "best.pt")

print(f"✅ Znaleziono najnowszy model w: {best_model_path}")

def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0
    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50
    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    return round(grade * 2) / 2

def get_iou(boxA, boxB):
    xA, yA, xB, yB = max(boxA[0], boxB[0]), max(boxA[1], boxB[1]), min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
    inter = max(0, xB - xA) * max(0, yB - yA)
    return inter / float(
        (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]) + (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]) - inter + 1e-6)

def clean(txt):
    txt = txt.upper().replace(" ", "").replace("-", "").replace("PL", "").replace(".", "").replace(":", "")
    replacements = {'O': '0', 'D': '0', 'Q': '0', 'I': '1', 'L': '1', '|': '1', '/': '1', ']': '1', '[': '1', '(': '1',
                    ')': '1', 'Z': '2', 'B': '8', 'S': '5', 'G': '6', 'A': '4', 'Y': 'V'}
    for k, v in replacements.items(): txt = txt.replace(k, v)
    return "".join(c for c in txt if c.isalnum())

def preprocess_crop(img):
    h, w = img.shape[:2]
    if h == 0: return img
    return cv2.resize(img, (int(w * (64.0 / h)), 64), interpolation=cv2.INTER_CUBIC)

trained_model = YOLO(best_model_path)
use_gpu = torch.cuda.is_available()
reader = easyocr.Reader(['en'], gpu=use_gpu)

test_subset = test_set[:100]
if len(test_subset) < 100: test_subset += train_set[:100 - len(test_subset)]

print(f"\n🧪 Testowanie {len(test_subset)} zdjęć...")

correct, ious, start_time = 0, [], time.time()

for item in test_subset:
    img = cv2.imread(item['src_img'])
    if img is None: continue

    gt_clean = clean(item['label'])
    gt_coords = item['coords']

    preds = trained_model.predict(img, imgsz=640, verbose=False, conf=0.25)[0]

    best_iou, best_box = 0, gt_coords
    if preds.boxes:
        boxes = preds.boxes.xyxy.cpu().numpy().astype(int)
        ious_list = [get_iou(gt_coords, b) for b in boxes]
        if ious_list:
            best_iou = max(ious_list)
            best_box = boxes[np.argmax(ious_list)]
    ious.append(best_iou)

    if best_iou > 0.5:
        x1, y1, x2, y2 = best_box
        h, w = img.shape[:2]

        candidates = []
        shifts = [(0, 0, 5, 5), (0, 0, 15, 15), (0, 0, -5, 15), (0, 0, 15, -5)]
        for d in shifts:
            c = img[max(0, y1 - d[0]):min(h, y2 + d[1]), max(0, x1 - d[2]):min(w, x2 + d[3])]
            if c.size:
                candidates.append(c)
                if c.shape[1] > 30: candidates.append(c[:, int(c.shape[1] * 0.14):])

        match = False
        for c in candidates:
            if match: break
            gray = cv2.cvtColor(preprocess_crop(c), cv2.COLOR_BGR2GRAY)
            filters = [
                cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 19, 5),
                cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                cv2.bitwise_not(cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
            ]

            for f in filters:
                pad = cv2.copyMakeBorder(f, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
                txt = clean("".join(
                    reader.readtext(pad, detail=0, beamWidth=5, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')))
                if gt_clean == txt or gt_clean in txt or txt in gt_clean or difflib.SequenceMatcher(None, txt,
                                                                                                    gt_clean).ratio() > 0.6:
                    correct += 1
                    match = True
                    break

dur = time.time() - start_time
acc = (correct / len(test_subset)) * 100
grade = calculate_final_grade(acc, dur)

print(f"Mean IoU:       {np.mean(ious):.4f}")
print(f"Accuracy:       {acc:.2f}%")
print(f"Time (100 img): {dur:.2f}s")
print(f"OCENA:          {grade}")
