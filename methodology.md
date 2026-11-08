# Methodology
* Detection on every sampled frame (left camera), markers clustered spatially; per board: marker count, mean marker side (px), interpolated ChArUco corners.
* Completeness = corners / board corners (40 or 8); binned by marker side px.
* Distance timeline in 1.5 s bins with stereo plane distance from Field Note #09 when available.
* Session yield = share of sampled frames (every 3rd) with ≥12 corners.
* Pinhole marker size model: px = f · printed_marker_mm / distance, f = 482.35 px.
