"""A4 — ChArUco detection limits for a wide-angle (fisheye) egocentric stereo rig.

* Timeline of the distance sessions (1.5 s bins): fraction of frames with a board,
  mean corners, marker side in pixels, stereo distance (when detectable).
* Corner completeness vs marker size in pixels (all detections, left camera).
* Detection yield of the hand-held 'session A' recordings.
Run: PYTHONPATH=. python3 a4_detection_limits.py out_dir   (needs out/a1_per_frame.csv)
"""
import sys, os, json
import numpy as np, pandas as pd
from odl_calib import DATA, BOARDS

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
A1 = pd.read_csv(f'{OUT}/a1_per_frame.csv')
FULL = {'a4': 40, 'far': 8}
tl = []
for rec, kind in [('145221_00000', 'a4'), ('145446_00000', 'far')]:
    L = json.load(open(f'{DATA}/det_{rec}_left.json'))
    d1 = A1[A1.recording == rec]
    t = np.array([x['f'] / 30 for x in L])
    nc = np.array([max([len(b.get('ids', [])) for b in x['boards']], default=0) for x in L])
    ms = np.array([max([b['msize'] for b in x['boards'] if len(b.get('ids', [])) > 0], default=np.nan) for x in L])
    for t0 in np.arange(0, t.max(), 1.5):
        m = (t >= t0) & (t < t0 + 1.5)
        dd = d1[(d1.t_s >= t0) & (d1.t_s < t0 + 1.5)]
        tl.append(dict(recording=rec, board=kind, t_start_s=t0, frames=int(m.sum()), frac_any_corner=float(np.mean(nc[m] >= 4)),
                       frac_full_board=float(np.mean(nc[m] >= FULL[kind])), mean_corners=float(nc[m].mean()),
                       marker_px_median=float(np.nanmedian(ms[m])) if np.any(~np.isnan(ms[m])) else np.nan,
                       stereo_dist_m=float(dd.plane_dist_m.median()) if len(dd) else np.nan))
pd.DataFrame(tl).round(3).to_csv(f'{OUT}/a4_distance_timeline.csv', index=False)

# completeness vs marker pixels, all recordings (left camera)
rows = []
recs = {'124235_00000': 'a4', '124235_00001': 'a4', '124235_00002': 'a4', '142800_00000': 'a4', '143229_00000': 'a4',
        '145221_00000': 'a4', '150437_00000': 'a4', '145446_00000': 'far', '145935_00000': 'far', '145719_00000': 'far'}
for rec, kind in recs.items():
    for x in json.load(open(f'{DATA}/det_{rec}_left.json')):
        for b in x['boards']:
            if b['nm'] >= 2:
                rows.append(dict(recording=rec, board=kind, marker_px=b['msize'], markers=b['nm'], corners=len(b.get('ids', [])),
                                 complete=len(b.get('ids', [])) >= FULL[kind]))
D = pd.DataFrame(rows)
bins = [8, 12, 16, 20, 24, 30, 40, 60, 120]
D['marker_px_bin'] = pd.cut(D.marker_px, bins)
comp = D.groupby(['board', 'marker_px_bin'], observed=True).agg(n=('corners', 'size'), median_corners=('corners', 'median'), frac_complete=('complete', 'mean')).reset_index()
comp['marker_px_bin'] = comp.marker_px_bin.astype(str)
comp.round(3).to_csv(f'{OUT}/a4_completeness_vs_marker_px.csv', index=False)

# yield of hand-held target sessions (A) and the drift attempt
yl = []
for rec in ['124235_00000', '124235_00001', '124235_00002', '142800_00000', '143229_00000', '143229_00001', '150150_00000']:
    L = json.load(open(f'{DATA}/det_{rec}_left.json'))
    step = L[1]['f'] - L[0]['f']
    nc = np.array([max([len(b.get('ids', [])) for b in x['boards']], default=0) for x in L])
    yl.append(dict(recording=rec, sampled_every_n_frames=step, sampled_frames=len(L), duration_s=len(L) * step / 30,
                   frac_frames_ge12_corners=float(np.mean(nc >= 12)), frac_frames_any_corner=float(np.mean(nc >= 4))))
pd.DataFrame(yl).round(3).to_csv(f'{OUT}/a4_session_yield.csv', index=False)
print(comp.round(3).to_string()); print(pd.DataFrame(yl).round(3).to_string())
# theoretical marker size at distance for both boards (printed size from ruler: 97.2 % / 97.1 % scale)
f = 482.35
th = [dict(board=k, printed_marker_mm=m, distance_m=z, marker_px_center=f * m / 1000 / z) for k, m in [('a4', 22 * 29.1667 / 30), ('far', 42 * 53.37 / 55)] for z in [0.3, 0.5, 0.6, 0.8, 0.9, 1.0, 1.5]]
pd.DataFrame(th).round(2).to_csv(f'{OUT}/a4_marker_px_model.csv', index=False)
T = pd.DataFrame(tl); print(T[T.recording == '145221_00000'].round(2).to_string())
