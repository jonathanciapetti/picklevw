# import streamlit as st
# import numpy as np
# from typing import Any
#
#
# # def handle_streamlit_image(obj: Any):
# #     """
# #     Tries to interpret and display image batches from pickled objects, in a dataset-agnostic way.
# #
# #     Supports:
# #     - 4D NumPy arrays (N, H, W, C): standard image batches
# #     - 3D NumPy arrays (H, W, C): single image
# #     - Flat image batches (N, C*H*W) reshaped into images if shape is inferable
# #     - Dictionaries with a 'data' key that contains one of the above formats
# #     """
# #     def display_image(img: np.ndarray, caption: str = ""):
# #         try:
# #             if img.dtype != np.uint8:
# #                 img = np.clip(img, 0, 255).astype(np.uint8)
# #             st.image(img, caption=caption, use_column_width=False)
# #         except Exception as ex:
# #             print(ex)
# #
# #     try:
# #         # Case 1: wrapped in a dict (common for CIFAR-like datasets)
# #         if isinstance(obj, dict) and "data" in obj:
# #             data = obj["data"]
# #             meta = {k: v for k, v in obj.items() if k != "data"}
# #         else:
# #             data = obj
# #             meta = {}
# #
# #         if isinstance(data, np.ndarray):
# #             if data.ndim == 4:
# #                 # (N, H, W, C)
# #                 st.write(f"Detected {data.shape[0]} images")
# #                 for i in range(min(10, data.shape[0])):
# #                     display_image(data[i], caption=f"Image {i}")
# #             elif data.ndim == 3 and data.shape[2] in (1, 3, 4):
# #                 # Single image
# #                 display_image(data, caption="Single image")
# #             elif data.ndim == 2:
# #                 # Possibly flat (N, C*H*W)
# #                 N, D = data.shape
# #                 C_guess = 3 if D % 3 == 0 else 1 if D % 1 == 0 else None
# #                 if C_guess:
# #                     H_W = D // C_guess
# #                     side = int(H_W**0.5)
# #                     if side * side * C_guess == D:
# #                         st.write(f"Inferred flat image batch: {N} images, shape ≈ {side}×{side}×{C_guess}")
# #                         for i in range(min(10, N)):
# #                             img_flat = data[i]
# #                             img = img_flat.reshape(C_guess, side, side).transpose(1, 2, 0)
# #                             display_image(img, caption=f"Image {i}")
# #                     else:
# #                         st.warning("Unable to infer image shape from flat data.")
# #                 else:
# #                     st.warning("2D array not in recognizable image format.")
# #             else:
# #                 st.warning(f"Unsupported ndarray shape: {data.shape}")
# #         else:
# #             st.warning("Data is not a NumPy array.")
# #
# #         if meta:
# #             st.markdown("**Metadata**")
# #             for k, v in meta.items():
# #                 st.write(f"- `{k}`: {type(v).__name__} ({len(v) if hasattr(v, '__len__') else 'scalar'})")
# #     except Exception as ex:
# #         print(ex)
#
#
# """
# Class that encapsulates CIFAR-10 dataset.
#
# The CIFAR-10 dataset consists of 60000 32x32 colour images in 10 classes,
#  with 6000 images per class. There are 50000 training images and 10000 test images.
# """
# import pickle
# from pathlib import Path
# from typing import List
#
# import numpy as np
# from .extractor import Extractor
#
#
# class CIFARSample:
#     """
#     One example from the CIFAR-10 dataset.
#     """
#     def __init__(self, image, label, filename):
#         self.image = image
#         self.label = label
#         self.filename = filename
#
#     @property
#     def label_hr(self):
#         # Human readable label
#         return CIFAR10.label_to_str[self.label]
#
#     def __str__(self):
#         return f'[{self.label_hr}] - {self.filename}'
#
#
# class CIFAR10:
#     # URL to download the dataset from Toronto university
#     cifar_url = 'https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'
#
#     # Mappings from numeric to human readable labels (and the other way around)
#     label_to_str = {0: 'airplane', 1: 'automobile', 2: 'bird', 3: 'cat', 4: 'deer',
#                     5: 'dog', 6: 'frog', 7: 'horse', 8: 'ship', 9: 'truck'}
#     str_to_label = {v: k for (k, v) in label_to_str.items()}
#
#     def __init__(self, dataset_root: str):
#         self.dataset_root = Path(dataset_root)
#         self.tgz_filename = Path('cifar-10-python.tar.gz')
#
#         # There are 50000 training images and 10000 test images.
#         self.samples = {
#             'train': np.ndarray(shape=(50000,), dtype=CIFARSample),
#             'test': np.ndarray(shape=(10000,), dtype=CIFARSample),
#         }
#
#         # Possibly download and extract the dataset
#         if not self.dataset_root.is_dir():
#             self._download_and_extract_cifar10()
#
#         # Unpickle the five train batches
#         for batch_f in self.dataset_root.glob('data_batch*'):
#             self._unpickle_data_batch(batch_f, split='train')
#
#         # Unpickle the only test batch
#         self._unpickle_data_batch(self.dataset_root / 'test_batch', split='test')
#
#     @staticmethod
#     def to_ndarray(sample_list: List[CIFARSample], normalize: bool=False, flatten: bool=False):
#         """
#         Convert a list of CifarSample to ndarray for further processing (e.g. training a classifier)
#
#         :param sample_list: List of CIFARSample
#         :param normalize: If true, `x` is scaled and centered on zero.
#         :param flatten: If true `x` is unrolled in a vector.
#         :return x, y: Images and labels as ndarray.
#         """
#         x = np.asarray([s.image for s in sample_list])
#         if normalize:
#             x = x.astype(np.float32) / 255. - 0.5  # zero centering
#         if flatten:
#             x = x.reshape(-1, 32 * 32 * 3)
#         y = np.asarray([s.label for s in sample_list])
#         return x, y
#
#     def _unpickle_data_batch(self, batch_file, split):
#         # Read pickle file
#         with open(batch_file, 'rb') as f:
#             data = pickle.load(f, encoding='bytes')
#
#         # Handle the fact that train set is split into five batch files
#         samples_start_idx = 0
#         if split == 'train':
#             batch_num = int(batch_file.name[-1])
#             samples_start_idx = int(10000 * (batch_num - 1))
#
#         # Each pickle batch file contains 10000 examples
#         for i in range(10000):
#             idx = samples_start_idx + i
#             sample = CIFARSample(image=data[b'data'][i].reshape(3, 32, 32).transpose(1, 2, 0),
#                                  label=data[b'labels'][i],
#                                  filename=data[b'filenames'][i].decode())
#             self.samples[split][idx] = sample
