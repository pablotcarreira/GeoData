import hashlib
import os
from typing import Tuple

import cv2
import matplotlib.pylab as plt
import numpy as np


def plot_imagem(imagem, name="Imagem", size=(10, 15), gray=False):
    plt.figure(figsize=size)
    if not gray:
        plt.imshow(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(imagem)
    plt.title(name)
    plt.axis('off')
    plt.show()

def compare_images(im1, im2):
    plt.figure(figsize=(10, 15))
    plt.imshow(im1)
    plt.imshow(im2)
    plt.axis('off')
    plt.show()






def calc_checksum(arquivo):
    with open(arquivo, 'rb') as source_file:
        md5 = hashlib.md5(source_file.read()).hexdigest()
    return md5


def try_remove(arquivo):
    """Tenta remover um arquivo."""
    try:
        os.remove(arquivo)
    except OSError:
        pass


def normalize_channel_range(x: np.ndarray) -> np.ndarray:
    """Normaliza entre 0 e 1"""
    # return 2 * (x / 255) - 1
    return x / 255


def normalize_block_shape(block_size: Tuple, array_in: np.ndarray) -> np.ndarray:
    """Normaliza o tamanho do bloco para o block size desejado,
    garante que a RN recebe blocos sempre do mesmo tamanho.
    
    Preenche o resto com zeros.

    * Funciona apenas com matrizes bi-dimensionais.
    * As bordas são preenchodas com preto.    
    * Caso o tamanho seja o desejado, retorna a propria matriz de entrada.       

    :param array_in: Matriz (bloco) entrda. 
    :param block_size: Tamanho desejado.
    :return: Matriz com o novo tamanho ou a própria matriz de entrda.
    """
    shape_in = array_in.shape
    if array_in.shape != block_size:
        array_out = np.zeros(block_size, dtype=np.uint8)
        array_out[:shape_in[0], :shape_in[1]] = array_in
    else:
        array_out = array_in
    return array_out


if __name__ == '__main__':
    imagem_cultura = cv2.imread("pedaco.tiff")
    plot_imagem(imagem_cultura)
