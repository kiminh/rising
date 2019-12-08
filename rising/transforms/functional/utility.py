from typing import Sequence, List, Tuple
from torch import Tensor
import torch

__all__ = ["box_to_seg", "seg_to_box", "instance_to_semantic"]


def box_to_seg(boxes: Sequence[Sequence[int]], shape: Sequence[int] = None,
               dtype: torch.dtype = None, device: torch.device = None,
               out: Tensor = None) -> Tensor:
    """
    Converts a sequence of bounding boxes to a segmentation

    Parameters
    ----------
    boxes: Sequence[Sequence[int]]
        sequence of bounding boxes encoded as
        (dim0_min, dim1_min, dim0_max, dim1_max, [dim2_min, dim2_max]).
        Supported bounding boxes for 2D (4 entries per box) and 3d (6 entries per box)
    shape: Sequence[int]
        if :param:`out` is not provided, shape of output tensor must be specified
    dtype: torch.dtype
        if :param:`out` is not provided, dtype of output tensor must be specified
    device: torch.device
        if :param:`out` is not provided, device of output tensor must be specified
    out: Tensor
        if :param:`out` is not None, the segmentation will be saved inside this tensor

    Returns
    -------
    Tensor
        bounding boxes encoded as a segmentation
    """
    if out is None:
        out = torch.zeros(*shape, dtype=dtype, device=device)

    for _idx, box in enumerate(boxes, 1):
        if len(box) == 4:
            out[..., box[0]:box[2], box[1]:box[3]] = _idx
        elif (len(box)) == 6:
            out[..., box[0]:box[2] + 1, box[1]:box[3] + 1, box[4]:box[5] + 1] = _idx
        else:
            raise TypeError(f"Boxes must have length 4 (2D) or 6(3D) forund {len(box)}")
    return out


def seg_to_box(seg: Tensor, dim: int) -> List[Tensor]:
    """
    Convert instance segmentation to bounding boxes

    Parameters
    ----------
    seg: Tensor
        segmentation of individual classes (index should start from one and be continuous)
    dim: int
        number of spatial dimensions

    Returns
    -------
    List[Tensor]
        list of bounding boxes
    Tensor
        tuple with classes for bounding boxes
    """
    boxes = []
    _seg = seg.detach()
    for _idx in range(1, seg.max().detach().item() + 1):
        instance_map = (_seg == _idx).nonzero()
        _mins = instance_map.min(dim=0)[0]
        _maxs = instance_map.max(dim=0)[0]
        box = [_mins[-dim], _mins[-dim + 1], _maxs[-dim], _maxs[-dim + 1]]
        if dim > 2:
            box = box + [c for cv in zip(_mins[-dim + 2:], _maxs[-dim + 2:]) for c in cv]
        boxes.append(torch.tensor(box).to(dtype=torch.float, device=seg.device))
    return boxes


def instance_to_semantic(instance: Tensor, cls: Sequence[int]) -> Tensor:
    """
    Convert an instance segmentation to an semantic segmentation

    Parameters
    ----------
    instance: Tensor
        instance segmentation of objects (objects need to start from 1, 0 background)
    cls: Sequence[int]
        mapping from indices from instance segmentation to real classes.

    Returns
    -------
    Tensor
        semantic segmentation

    Warnings
    --------
    :param:`instance` needs to encode objects starting from 1 and the indices need to be continuous
    (0 is interpreted as background)
    """
    seg = torch.zeros_like(instance)
    for idx, c in enumerate(cls, 1):
        seg[instance == idx] = c
    return seg
