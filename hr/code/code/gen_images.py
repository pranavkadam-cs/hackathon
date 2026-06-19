"""Generate placeholder images for all missing dataset images."""
import csv, os, random
from pathlib import Path
from PIL import Image, ImageDraw

rows = list(csv.DictReader(open('dataset/sample_claims.csv')))

case_info = {}
for i, r in enumerate(rows):
    case_num = str(i+1).zfill(3)
    case_info[f'case_{case_num}'] = {
        'obj': r['claim_object'],
        'claim': r['user_claim'][:60],
        'user': r['user_id']
    }

colors = {
    'car':     [(160,160,170), (120,120,130), (100,110,120)],
    'laptop':  [(40, 40, 50),  (30, 30, 40),  (60, 55, 70)],
    'package': [(190,150,80),  (160,120,60),  (200,165,90)],
}

all_paths = set()
for r in rows:
    for p in r['image_paths'].split(';'):
        all_paths.add(p.strip())

for p in sorted(all_paths):
    full = os.path.join('dataset', p)
    Path(full).parent.mkdir(parents=True, exist_ok=True)
    case = p.split('/')[2]
    info = case_info.get(case, {'obj': 'unknown', 'claim': '', 'user': ''})
    obj  = info['obj']
    col  = random.choice(colors.get(obj, [(150,150,150)]))

    img  = Image.new('RGB', (640, 480), color=col)
    draw = ImageDraw.Draw(img)

    # Background panel
    draw.rectangle([60, 80, 580, 400], outline=(255,255,200), width=3)
    # Damage area simulation
    draw.ellipse([250, 170, 390, 310], fill=(70, 35, 15), outline=(200,90,40), width=3)
    # Scratch lines
    draw.line([(200,200),(320,310)], fill=(200,180,160), width=2)
    draw.line([(310,190),(400,280)], fill=(200,180,160), width=2)

    draw.text((15, 8),  info['user'] + ' | ' + obj,    fill=(255,255,255))
    draw.text((15, 28), info['claim'],                   fill=(210,210,210))
    draw.text((15, 455), p,                              fill=(160,160,160))

    img.save(full, quality=85)
    print(f'Created: {full}')

print(f'\nDone — {len(all_paths)} placeholder images created.')
