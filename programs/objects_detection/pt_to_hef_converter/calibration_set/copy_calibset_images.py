import os, math, shutil

src = '<your_dataset_path>/images/train'
dst = '<path_to>/manipulator_project/programs/pt_to_hef_converter/calibration_set'
targets = {
    0: ('apple',),
    1: ('bear',),
    2: ('bird',),
    3: ('dog',),
    4: ('boar',),
    5: ('cat', 'cats'),
    6: ('cow', 'cows'),
    7: ('raccoon',),
    8: ('deer',),
    9: ('elephant',),
    10: ('hedgehog',),
    11: ('monkey',),
    12: ('squirrel',),
    13: ('tiger',)
}

exts = ('.jpg', '.jpeg', '.png', '.bmp')
groups = {k: [] for k in targets}
for f in os.listdir(src):
    fl = f.lower()
    if fl.endswith(exts):
        for k, prefs in targets.items():
            if any(fl.startswith(p) for p in prefs):
                groups[k].append(f)
                break

total_goal = 1000
classes = len(groups)
base = total_goal // classes
extra = total_goal - base * classes
selection = []

for k in sorted(groups):
    files = groups[k]
    take = base + (1 if extra > 0 and len(files) > base else 0)
    extra -= 1 if take > base else 0
    take = min(take, len(files))
    if take == 0:
        continue
    step = max(1, math.floor(len(files) / take))
    selection.extend(files[::step][:take])

os.makedirs(dst, exist_ok=True)
for f in selection:
    shutil.copy(os.path.join(src, f), os.path.join(dst, f))

print(f'Copied {len(selection)} images to {dst}')

