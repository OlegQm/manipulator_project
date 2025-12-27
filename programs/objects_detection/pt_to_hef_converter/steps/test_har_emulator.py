#!/usr/bin/env python3
import argparse
import os
from typing import Dict, List, Sequence, Tuple, Union, Optional

import numpy as np
from PIL import Image
from hailo_sdk_client import ClientRunner, InferenceContext

DEFAULT_IMG_SIZE = 640
DEFAULT_SCORE_TH = 0.2
DEFAULT_REG_MAX = 16


# ----------------------------- PREPROCESS ---------------------------------

def load_and_preprocess_image(path: str, img_size: int) -> np.ndarray:
    # Returns NHWC uint8: (1, H, W, 3)
    img = Image.open(path).convert("RGB")
    img = img.resize((img_size, img_size))
    arr = np.asarray(img, dtype=np.uint8)
    return arr[np.newaxis, ...]


# ---------------------- Helpers: NMS and IoU ------------------------------

def box_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """
    box: (4,)  [x1, y1, x2, y2]
    boxes: (N,4)
    returns: (N,)
    """
    if boxes.size == 0:
        return np.zeros((0,), dtype=np.float32)

    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])

    inter_w = np.maximum(0.0, x2 - x1)
    inter_h = np.maximum(0.0, y2 - y1)
    inter = inter_w * inter_h

    area_box = np.maximum(0.0, box[2] - box[0]) * np.maximum(0.0, box[3] - box[1])
    area_boxes = np.maximum(0.0, boxes[:, 2] - boxes[:, 0]) * np.maximum(0.0, boxes[:, 3] - boxes[:, 1])
    union = area_box + area_boxes - inter + 1e-9

    return inter / union


def nms_per_class(boxes: np.ndarray, scores: np.ndarray, iou_th: float = 0.7) -> np.ndarray:
    """
    Simple per-class NMS.
    boxes: (N,4), scores: (N,)
    returns: indices kept (K,)
    """
    if boxes.size == 0:
        return np.array([], dtype=int)

    idxs = np.argsort(-scores)
    keep: List[int] = []

    while idxs.size > 0:
        i = int(idxs[0])
        keep.append(i)
        if idxs.size == 1:
            break
        ious = box_iou(boxes[i], boxes[idxs[1:]])
        idxs = idxs[1:][ious < iou_th]

    return np.array(keep, dtype=int)


# ---------------------- Hailo YOLOv8 NMS decoder -------------------------

def hailo_yolov8_nms_to_detections(
    nms_output: np.ndarray,
    img_w: int,
    img_h: int,
    score_th: float = DEFAULT_SCORE_TH,
) -> np.ndarray:
    """
    NMS output format:
      (1, C, 5, K) or (C, 5, K), where:
        C = num_classes,
        5 = [y_min, x_min, y_max, x_max, score] in 0..1,
        K = max_proposals_per_class.
    Returns:
      (N, 6): [x1, y1, x2, y2, score, cls_id]
    """
    arr = nms_output

    if isinstance(arr, (list, tuple)):
        if not arr:
            return np.zeros((0, 6), dtype=np.float32)
        arr = arr[0]

    if not isinstance(arr, np.ndarray):
        raise ValueError(f"Unexpected output type: {type(arr)}")

    if arr.ndim == 4 and arr.shape[0] == 1:
        arr = arr[0]  # (C, 5, K)

    if arr.ndim != 3 or arr.shape[1] != 5:
        raise ValueError(f"Unexpected NMS output shape {arr.shape}, expected [C, 5, K]")

    num_classes, _, num_props = arr.shape
    dets: List[List[float]] = []

    for cls_id in range(num_classes):
        y_min = arr[cls_id, 0]
        x_min = arr[cls_id, 1]
        y_max = arr[cls_id, 2]
        x_max = arr[cls_id, 3]
        scores = arr[cls_id, 4]

        for k in range(num_props):
            score = float(scores[k])
            if score < score_th:
                continue

            x1 = float(x_min[k] * img_w)
            y1 = float(y_min[k] * img_h)
            x2 = float(x_max[k] * img_w)
            y2 = float(y_max[k] * img_h)

            dets.append([x1, y1, x2, y2, score, float(cls_id)])

    if not dets:
        return np.zeros((0, 6), dtype=np.float32)

    return np.array(dets, dtype=np.float32)


# ---------------------- RAW YOLOv8 OUTPUT DECODER -------------------------

RawOutputs = Union[np.ndarray, Sequence[np.ndarray], Dict[str, np.ndarray]]


def _infer_default_strides(num_levels: int) -> List[int]:
    """
    Heuristic defaults:
      3 levels -> P3,P4,P5 -> [8,16,32]
      4 levels -> P2,P3,P4,P5 -> [4,8,16,32]
    """
    if num_levels == 3:
        return [8, 16, 32]
    if num_levels == 4:
        return [4, 8, 16, 32]
    # Fallback: start at 8 and double
    return [8 * (2 ** i) for i in range(num_levels)]


def _normalize_raw_outputs(outputs: RawOutputs) -> List[np.ndarray]:
    """
    Convert outputs to a list of numpy arrays in a stable order.
    Expected raw order: [bbox_L0, cls_L0, bbox_L1, cls_L1, ...].
    """
    if isinstance(outputs, (list, tuple)):
        return [o for o in outputs if isinstance(o, np.ndarray)]

    if isinstance(outputs, dict):
        # Try to sort by key name; many runtimes produce output0/output1/... keys
        keys = sorted(outputs.keys())
        return [outputs[k] for k in keys if isinstance(outputs[k], np.ndarray)]

    raise ValueError(f"Unsupported raw output container: {type(outputs)}")


def decode_yolov8_raw_outputs(
    outputs: RawOutputs,
    img_size: int,
    score_th: float = DEFAULT_SCORE_TH,
    reg_max: int = DEFAULT_REG_MAX,
    strides: Optional[Sequence[int]] = None,
    nms_iou_th: float = 0.7,
) -> np.ndarray:
    """
    Decodes YOLOv8 DFL raw outputs (no NMS in the graph).

    outputs: list/tuple or dict of tensors, total length must be 2*num_levels:
      [bbox_L0, cls_L0, bbox_L1, cls_L1, ...]
    where bbox: (1, H, W, 4*reg_max), cls: (1, H, W, num_classes)

    Returns: (N,6) [x1,y1,x2,y2,score,cls_id] after per-class NMS.
    """
    out_list = _normalize_raw_outputs(outputs)
    if len(out_list) % 2 != 0 or len(out_list) < 2:
        raise ValueError(f"Unexpected raw outputs length: {len(out_list)} (must be even and >= 2)")

    num_levels = len(out_list) // 2
    if strides is None:
        strides = _infer_default_strides(num_levels)
    strides = list(strides)
    if len(strides) != num_levels:
        raise ValueError(f"strides length {len(strides)} does not match num_levels {num_levels}")

    proj = np.arange(reg_max, dtype=np.float32)
    all_det: List[np.ndarray] = []

    for level in range(num_levels):
        stride = float(strides[level])

        bbox_map = out_list[2 * level]
        cls_map = out_list[2 * level + 1]

        if bbox_map.ndim != 4 or cls_map.ndim != 4:
            raise ValueError(
                f"Unexpected tensor ranks at level {level}: bbox {bbox_map.shape}, cls {cls_map.shape}"
            )

        bbox_map = bbox_map[0]  # (H, W, 4*reg_max)
        cls_map = cls_map[0]    # (H, W, C)

        H, W, c_reg = bbox_map.shape
        _, _, c_cls = cls_map.shape

        if c_reg != 4 * reg_max:
            raise ValueError(f"Unexpected bbox channels: {c_reg}, expected {4 * reg_max}")

        # (H*W, 4, reg_max)
        bbox_flat = bbox_map.reshape(H * W, 4, reg_max).astype(np.float32)

        # Softmax over reg_max (numerically stable)
        bbox_flat = bbox_flat - bbox_flat.max(axis=2, keepdims=True)
        exp = np.exp(bbox_flat)
        probs = exp / (exp.sum(axis=2, keepdims=True) + 1e-9)

        # Expected distances in bins [0..reg_max-1]
        dists = (probs * proj[None, None, :]).sum(axis=2)  # (N,4)
        dists = dists * stride

        # Grid centers
        ys = np.arange(H, dtype=np.float32)
        xs = np.arange(W, dtype=np.float32)
        grid_y, grid_x = np.meshgrid(ys, xs, indexing="ij")

        cx = (grid_x.reshape(-1) + 0.5) * stride
        cy = (grid_y.reshape(-1) + 0.5) * stride

        l = dists[:, 0]
        t = dists[:, 1]
        r = dists[:, 2]
        b = dists[:, 3]

        x1 = np.clip(cx - l, 0, img_size - 1)
        y1 = np.clip(cy - t, 0, img_size - 1)
        x2 = np.clip(cx + r, 0, img_size - 1)
        y2 = np.clip(cy + b, 0, img_size - 1)

        cls_flat = cls_map.reshape(H * W, c_cls).astype(np.float32)
        cls_scores = 1.0 / (1.0 + np.exp(-cls_flat))  # sigmoid

        best_scores = cls_scores.max(axis=1)
        best_ids = cls_scores.argmax(axis=1)

        mask = best_scores >= score_th
        if not np.any(mask):
            continue

        det_level = np.stack(
            [x1[mask], y1[mask], x2[mask], y2[mask], best_scores[mask], best_ids[mask].astype(np.float32)],
            axis=1,
        )
        all_det.append(det_level)

    if not all_det:
        return np.zeros((0, 6), dtype=np.float32)

    dets = np.concatenate(all_det, axis=0).astype(np.float32)

    # Per-class NMS
    final: List[np.ndarray] = []
    class_ids = dets[:, 5].astype(int)
    for cls in np.unique(class_ids):
        m = class_ids == cls
        cls_boxes = dets[m, 0:4]
        cls_scores = dets[m, 4]
        keep = nms_per_class(cls_boxes, cls_scores, iou_th=nms_iou_th)
        final.append(dets[m][keep])

    if not final:
        return np.zeros((0, 6), dtype=np.float32)

    return np.concatenate(final, axis=0)


# ----------------------------- INFERENCE ----------------------------------

def _print_outputs_diagnostics(outputs) -> None:
    if isinstance(outputs, dict):
        print("[INFO] Outputs is dict with keys:", list(outputs.keys()))
        for name, out in outputs.items():
            if isinstance(out, np.ndarray):
                print(f"[INFO]   {name}: shape={out.shape}, dtype={out.dtype}")
            else:
                print(f"[INFO]   {name}: type={type(out)}")
    elif isinstance(outputs, (list, tuple)):
        print(f"[INFO] Outputs is list/tuple of length {len(outputs)}")
        for i, out in enumerate(outputs):
            if isinstance(out, np.ndarray):
                print(f"[INFO]   out[{i}]: shape={out.shape}, dtype={out.dtype}")
            else:
                print(f"[INFO]   out[{i}]: type={type(out)}")
    else:
        print(f"[INFO] Outputs type: {type(outputs)}")
        if isinstance(outputs, np.ndarray):
            print(f"[INFO]   array shape={outputs.shape}, dtype={outputs.dtype}")


def _parse_strides_arg(s: Optional[str]) -> Optional[List[int]]:
    if s is None:
        return None
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return None
    return [int(p) for p in parts]


def run_on_emulator(
    har_path: str,
    image_paths: Sequence[str],
    context_type: str = "quantized",
    img_size: int = DEFAULT_IMG_SIZE,
    score_th: float = DEFAULT_SCORE_TH,
    reg_max: int = DEFAULT_REG_MAX,
    strides: Optional[Sequence[int]] = None,
    nms_iou_th: float = 0.7,
) -> None:
    if not os.path.isfile(har_path):
        raise FileNotFoundError(f"HAR not found: {har_path}")

    print(f"[INFO] Loading HAR: {har_path}")
    runner = ClientRunner(har=har_path)

    ctx_map = {
        "native": InferenceContext.SDK_NATIVE,
        "fp_optimized": InferenceContext.SDK_FP_OPTIMIZED,
        "quantized": InferenceContext.SDK_QUANTIZED,
    }
    if context_type not in ctx_map:
        raise ValueError(f"Unknown context_type: {context_type}")
    ctx_enum = ctx_map[context_type]

    with runner.infer_context(ctx_enum) as ctx:
        print(f"[INFO] Using inference context: {context_type}")

        for img_path in image_paths:
            if not os.path.isfile(img_path):
                print(f"[WARN] Image not found, skipping: {img_path}")
                continue

            print("\n" + "=" * 80)
            print(f"[INFO] Image: {img_path}")

            inp = load_and_preprocess_image(img_path, img_size)
            print(f"[DEBUG] Input shape: {inp.shape}, dtype: {inp.dtype}")

            outputs = runner.infer(ctx, inp)
            _print_outputs_diagnostics(outputs)

            try:
                # Case 1: NMS output already produced by the graph
                if isinstance(outputs, np.ndarray):
                    print("[INFO] Trying to parse as Hailo NMS output...")
                    dets = hailo_yolov8_nms_to_detections(
                        outputs,
                        img_w=img_size,
                        img_h=img_size,
                        score_th=score_th,
                    )

                # Case 2: Raw outputs (bbox/cls per level)
                elif isinstance(outputs, (list, tuple, dict)):
                    out_list = _normalize_raw_outputs(outputs)
                    if len(out_list) % 2 != 0:
                        raise ValueError(f"Raw outputs must have even length, got {len(out_list)}")

                    num_levels = len(out_list) // 2
                    auto_strides = list(strides) if strides is not None else _infer_default_strides(num_levels)

                    print(
                        f"[INFO] Parsing as raw YOLOv8 outputs (no NMS in HAR): "
                        f"num_levels={num_levels}, strides={auto_strides}, reg_max={reg_max}"
                    )

                    dets = decode_yolov8_raw_outputs(
                        outputs=out_list,
                        img_size=img_size,
                        score_th=score_th,
                        reg_max=reg_max,
                        strides=auto_strides,
                        nms_iou_th=nms_iou_th,
                    )
                else:
                    raise ValueError("Unknown output format for decoding.")

                print(f"[INFO] Parsed detections: {len(dets)} (score >= {score_th})")
                for i, (x1, y1, x2, y2, sc, cls_id) in enumerate(dets[:20]):
                    print(
                        f"  #{i:02d}: cls={int(cls_id)} "
                        f"score={sc:.3f} "
                        f"bbox=({x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f})"
                    )

            except Exception as e:
                print(f"[ERROR] Failed to decode detections: {e}")


# ----------------------------- CLI ----------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test Hailo HAR model on SDK emulator (no hardware needed)."
    )
    parser.add_argument("--har", required=True, help="Path to .har or quantized .har file")
    parser.add_argument("--images", nargs="+", required=True, help="One or more image paths for testing")
    parser.add_argument("--img-size", type=int, default=DEFAULT_IMG_SIZE, help=f"Resize images to this size (default: {DEFAULT_IMG_SIZE})")
    parser.add_argument("--context", choices=["native", "fp_optimized", "quantized"], default="quantized", help="Inference context (emulation mode)")
    parser.add_argument("--score-th", type=float, default=DEFAULT_SCORE_TH, help=f"Score threshold (default: {DEFAULT_SCORE_TH})")
    parser.add_argument("--reg-max", type=int, default=DEFAULT_REG_MAX, help=f"YOLOv8 reg_max for DFL decoding (default: {DEFAULT_REG_MAX})")
    parser.add_argument(
        "--strides",
        type=str,
        default=None,
        help="Comma-separated strides for raw decoding, e.g. '8,16,32' or '4,8,16,32'. If omitted, inferred from number of output levels.",
    )
    parser.add_argument("--nms-iou", type=float, default=0.7, help="IoU threshold for per-class NMS (raw decoding only)")

    args = parser.parse_args()

    run_on_emulator(
        har_path=args.har,
        image_paths=args.images,
        context_type=args.context,
        img_size=args.img_size,
        score_th=args.score_th,
        reg_max=args.reg_max,
        strides=_parse_strides_arg(args.strides),
        nms_iou_th=args.nms_iou,
    )


if __name__ == "__main__":
    main()

