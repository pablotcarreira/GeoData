# Pablo Carreira - 30/05/17
from random import Random
from typing import Sequence

import numpy as np

MIRROR_TOP = "top"
MIRROR_BOTTOM = "bottom"
MIRROR_LEFT = "left"
MIRROR_RIGHT = "right"
MIRROR_ERROR_MESSAGE = "Padding bigger than block dimension."
SAMPLER_RATIO_METHOD = "ratio"
SAMPLER_METHOD_N_SAMPLES = "n_samples"


class ArraySampler:
    def __init__(self, method: str, ratio: float = None, n_samples: int = None, random_seed: str = "abc"):
        """Creates a ramdom sampler that takes ramdom samples from a sequence or an array 
        by a percentage or by a number of samples.

        Elements are taken randomly, if you want the same elements to be taken every time, make
        sure that you always use the same seed.

        Check the sample method on how to take the samples.

        :param method: One of SAMPLER_RATIO_METHOD or SAMPLER_METHOD_N_SAMPLES. 
        :param ratio: The ratio of selected / not selected elements (0 < ratio < 1), 
            required if method=SAMPLER_RATIO_METHOD        
        :param n_samples: Number of samples, required if method=SAMPLER_METHOD_N_SAMPLES
        :param random_seed: A string to be used as the seed for the pseudo random generator, providing the same seed
            ensure that the same samples will be obteined on every call.
        """
        self.method = method
        self.random_seed = random_seed
        self.n_samples = n_samples
        self.ratio = ratio

        # Parameters checks:
        if method == SAMPLER_RATIO_METHOD:
            if ratio < 0 or ratio > 1 or ratio is None:
                raise ValueError("Ratio must be < 1 and > 0")
        elif method == SAMPLER_METHOD_N_SAMPLES:
            if n_samples is None:
                raise ValueError("Must provide n_samples.")
        else:
            raise ValueError("Invalid method.")

    def _calculate_output_length(self, n_blocks_total: int):
        """Calculates the number of selected and not selected blocks."""
        if self.method == SAMPLER_RATIO_METHOD:
            n_selected = int(n_blocks_total * self.ratio)
        elif self.method == SAMPLER_METHOD_N_SAMPLES:
            if n_blocks_total < self.n_samples:
                raise ValueError("More samples requested than available in the data.")
            n_selected = self.n_samples
        else:
            raise ValueError("Invalid method.")
        return n_selected, n_blocks_total - n_selected

    def sample(self, array: Sequence) -> Sequence:
        """Take samples from a sequence using the defined method.

        :param array: The list of indices.
        :returns: A tuple containing a alist of selected elements and a list of not selected elements.
        """
        n_blocks = len(array)
        n_selected, n_not_selected = self._calculate_output_length(n_blocks)
        random_generator = Random(self.random_seed)
        # Obs: Para otimização, é possível copiar e reproduzir a função sample,
        # separando os selecionados e não selecionados.
        selected = random_generator.sample(array, n_selected)
        # Agora calcula os não selecionados:
        not_selected = []
        for item in array:
            if item not in selected:
                not_selected.append(item)
        return selected, not_selected

    def predict_samples_sizes(self, img_shape, block_size: Sequence):
        """Given an input shape and a block size, predict the size of selected and not selected samples list."""
        # Quantos blocos inteiros cabem, quantos pixels sobram
        n_block_rows, resto_pixel_rows = divmod(img_shape[0], block_size[0])
        n_block_cols, resto_pixel_cols = divmod(img_shape[1], block_size[1])
        # Caso haja um pedaço sobrando do final, inclui mais um bloco.
        if resto_pixel_rows != 0:
            n_block_rows += 1
        if resto_pixel_cols != 0:
            n_block_cols += 1
        n_blocks_total = n_block_rows * n_block_cols
        return self._calculate_output_length(n_blocks_total)


def mirror_block(block_data: np.ndarray, padding: int, direction: str):
    """Mirrors a portion of a block by a given padding.

    :param block_data: A image block. 
    :param padding: The size of the mirroring in px.
    :param direction: top, bottom, left, right.
    :returns: The block added of the mirror padding. 
    """
    if padding == 0:
        return block_data
    elif padding < 0:
        raise ValueError("Padding must be positive.")

    if direction == MIRROR_TOP:
        if padding > block_data.shape[0]:
            raise ValueError(MIRROR_ERROR_MESSAGE)
        mirrored = np.flipud(block_data[:padding])
        return np.vstack((mirrored, block_data))
    elif direction == MIRROR_BOTTOM:
        if padding > block_data.shape[0]:
            raise ValueError(MIRROR_ERROR_MESSAGE)
        mirrored = np.flipud(block_data[-padding:])
        return np.vstack((block_data, mirrored))
    elif direction == MIRROR_LEFT:
        if padding > block_data.shape[1]:
            raise ValueError(MIRROR_ERROR_MESSAGE)
        mirrored = np.fliplr(block_data[:, :padding])
        return np.hstack((mirrored, block_data))
    elif direction == MIRROR_RIGHT:
        if padding > block_data.shape[1]:
            raise ValueError(MIRROR_ERROR_MESSAGE)
        mirrored = np.fliplr(block_data[:, -padding:])
        return np.hstack((block_data, mirrored))
    else:
        AttributeError('Direction must be one of [top, bottom, left, right] got: {}.'.format(direction))


def normalize_channel_range(x: np.ndarray) -> np.ndarray:
    """Normaliza entre 0 e 1"""
    # return 2 * (x / 255) - 1
    return x / 255
