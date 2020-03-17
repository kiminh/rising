import torch
from abc import abstractmethod, ABC
from typing import Union, Sequence
from rising.utils.shape import reshape


class AbstractParameter(ABC, torch.nn.Module):
    """
    Abstract Parameter class to inject randomness to transforms
    """

    @staticmethod
    def _get_n_samples(size: Union[Sequence, torch.Size] = (1,)):
        """
        Calculates the number of elements in the given size

        Parameters
        ----------
        size: Sequence or torch.Size

        Returns
        -------
        int
            the number of elements

        """
        if not isinstance(size, torch.Size):
            size = torch.Size(size)
        return size.numel()

    @abstractmethod
    def sample(self, n_samples: int) -> Union[torch.Tensor, list]:
        """
        Abstract sampling function

        Parameters
        ----------
        n_samples : int
            the number of samples to return

        Returns
        -------
        torch.Tensor or list
            the sampled values

        """
        raise NotImplementedError

    def forward(self, size: Union[Sequence, torch.Size] = (1,),
                device: Union[torch.device, str] = None,
                dtype: Union[torch.dtype, str] = None,
                tensor_like: torch.Tensor = None) -> Union[list, torch.Tensor]:
        """
        Forward function (will also be called if the module is called).
        Calculates the number of samples from the given shape, performs the
        sampling and converts it back to the correct shape.

        Parameters
        ----------
        size: Sequence or torch.Size
            the size of the sampled values
        device : torch.device or str, optional
            the device the result value should be set to, if it is a tensor
        dtype : torch.dtype or str, optional
            the dtype, the result value should be casted to, if it is a tensor
        tensor_like: torch.Tensor, optional
            the tensor, having the correct dtype and device. The result will
            be pushed onto this device and casted to this dtype if this is
            specified.

        Returns
        -------
        list or torch.Tensor
            the sampled values

        Notes
        -----
        if the parameter ``tensor_like`` is given,
        it overwrites the parameters ``dtype`` and ``device``

        """
        n_samples = self._get_n_samples(size)
        flat_samples = self.sample(n_samples)

        if not isinstance(flat_samples, torch.Tensor):
            try:
                flat_samples = torch.tensor(flat_samples)
            except TypeError:
                pass

        samples = reshape(flat_samples, size)

        if isinstance(samples, torch.Tensor):
            if tensor_like is not None:
                samples = samples.to(tensor_like)
            else:
                samples = samples.to(device=device, dtype=dtype)

        return samples
