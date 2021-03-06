from typing import List, Tuple, Union, Mapping, Hashable

import torch
from torch import Tensor

__all__ = ["to_device"]

data_type = Union[Tensor, List[Tensor], Tuple[Tensor], Mapping[Hashable, Tensor]]


def to_device(data: data_type, device: Union[torch.device, str], **kwargs) -> data_type:
    """
    Pushes data to device

    Args:
        data: data which should be pushed to device. Sequence and mapping
            items are mapping individually to gpu
        device: target device
        kwargs: keyword arguments passed to assigning function

    Returns:
        Union[torch.Tensor, Sequence, Mapping]: data which was pushed to device
    """
    if torch.is_tensor(data):
        return data.to(device=device, **kwargs)
    elif isinstance(data, Mapping):
        return {key: to_device(item, device, **kwargs) for key, item in data.items()}
    elif isinstance(data, (list, tuple)):
        return type(data)([to_device(item, device, **kwargs) for item in data])
    else:
        return data
