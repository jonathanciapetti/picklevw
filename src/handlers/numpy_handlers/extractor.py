# """
# Simple classes to download and extract CIFAR-10 data avoiding wget dependencies.
# """
# import tarfile
#
#
# class Extractor:
#     """
#     Simple class to extract CIFAR-10 archive
#     """
#     def __init__(self):
#         self.mode = 'r:gz'  # tar.gz
#
#     def extract(self, archive_path, extract_path):
#         tarfile.open(name=archive_path, mode=self.mode).extractall(extract_path)