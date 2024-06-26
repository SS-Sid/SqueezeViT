import os
from PIL import Image

import numpy as np
import pandas as pd

from torchvision.datasets.vision import VisionDataset

from typing import Callable, Optional

import torch
import pickle

class NIH_CXR_14(VisionDataset):
    metadata_file_name = "Data_Entry_2017.csv"
    
    classes = [
#         "No Finding",
        "Atelectasis",
        "Cardiomegaly",
        "Effusion",
        "Infiltration",
        "Mass",
        "Nodule",
        "Pneumonia",
        "Pneumothorax",
        "Consolidation",
        "Edema",
        "Emphysema",
        "Fibrosis",
        "Pleural_Thickening",
        "Hernia"
    ]
    
    train_list = "train_val_list.txt"
    test_list = "test_list.txt"
    
    def __init__(
            self,
            root: str,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None
    ):
        super().__init__(root, transform=transform, target_transform=target_transform)
        self.root = root
        self.train = train
        
        self.transform = transform
        self.target_transform = target_transform
        
        self._load_metadata()
        
        self.samples = self.make_dataset()
    
    def _load_metadata(self) -> None:
        self.metadata = pd.read_csv(
            os.path.join(self.root, self.metadata_file_name),
            usecols=["Image Index", "Finding Labels"]
        ).reset_index().set_index("Image Index")
        
        self.metadata["Finding Labels"] = self.metadata["Finding Labels"].apply(lambda x: x.split("|"))
        self.metadata["One-Hot Labels"] = self.metadata["Finding Labels"].apply(lambda x: [1 if lbl in x else 0 for lbl in self.classes])
    
    def make_dataset(self):
        if self.train:
            data_list = self.train_list
        else:
            data_list = self.test_list
        
        samples = []
        
        with open(os.path.join(self.root, data_list), 'rt') as split_file:
            for line in split_file:
                image_file_name = line.strip()
                
                image_file_path = self.get_image_path_from_name(image_file_name)
                image_labels = self.metadata.loc[image_file_name, "One-Hot Labels"]
                
                image_labels = torch.FloatTensor(image_labels)
                sample = image_file_path, image_labels
                samples.append(sample)
        
        return samples

    def get_image_path_from_name(self, image_file_name):
        image_file_index = self.metadata.loc[image_file_name, "index"]
        image_dir_num = int(1 + np.ceil((image_file_index - 4999 + 1)/10000))
        
        image_dir_name = "images_" + str(image_dir_num).zfill(3)
        image_path = os.path.join(self.root, image_dir_name, "images", image_file_name)
        
        return image_path
    
    def __getitem__(self, index):
        image_file_path, target = self.samples[index]
        img = self.get_pil_image(image_file_path)
        
        
        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)
        return img, target
    
    def __len__(self):
        return len(self.samples)
    
    def get_pil_image(self, image_file_path):
        with open(image_file_path, "rb") as image_file:
            img = Image.open(image_file)
            return img.convert("RGB")


class Preloaded_NIH_CXR_14(VisionDataset):
    classes = [
#         "No Finding",
        "Atelectasis",
        "Cardiomegaly",
        "Effusion",
        "Infiltration",
        "Mass",
        "Nodule",
        "Pneumonia",
        "Pneumothorax",
        "Consolidation",
        "Edema",
        "Emphysema",
        "Fibrosis",
        "Pleural_Thickening",
        "Hernia"
    ]
    
    def __init__(
            self,
            root: str,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None
    ):
        super().__init__(root, transform=transform, target_transform=target_transform)
        self.root = root
        self.train = train
        
        self.transform = transform
        self.target_transform = target_transform
        
        self.samples = self.load_dataset()
    
    def load_dataset(self):
        if self.train:
            phase = "train"
        else:
            phase = "test"
        
        samples = []
        
        main_dir = os.path.join(self.root, phase)
        for batch_dir in os.listdir(main_dir):
            with open(os.path.join(main_dir, batch_dir), 'rb') as file:
                batch = pickle.load(file)
                samples.extend(batch)
        
        return samples
    
    def __getitem__(self, index):
        img, target = self.samples[index]
        
        
        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)
        
        return img, target
    
    def __len__(self):
        return len(self.samples)


class Preloaded_CheXpert(VisionDataset):
    classes = ['No Finding', 'Enlarged Cardiomediastinum', 'Cardiomegaly',
       'Lung Opacity', 'Lung Lesion', 'Edema', 'Consolidation', 'Pneumonia',
       'Atelectasis', 'Pneumothorax', 'Pleural Effusion', 'Pleural Other',
       'Fracture', 'Support Devices']
    
    def __init__(
            self,
            root: str,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None
    ):
        super().__init__(root, transform=transform, target_transform=target_transform)
        self.root = root
        self.train = train
        
        self.transform = transform
        self.target_transform = target_transform
        
        self.samples = self.load_dataset()
    
    def load_dataset(self):
        if self.train:
            phase = "train"
        else:
            phase = "test"
        
        samples = []
        
        main_dir = os.path.join(self.root, phase)
        for batch_dir in os.listdir(main_dir):
            with open(os.path.join(main_dir, batch_dir), 'rb') as file:
                batch = pickle.load(file)
                samples.extend(batch)
                # print(len(samples[0][1]))
        
        return samples
    
    def __getitem__(self, index):
        img, target = self.samples[index]
        # print(len(target))
        
        
        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)
        
        return img, target
    
    def __len__(self):
        return len(self.samples)
    
    
class Preloaded_VinBig(VisionDataset):
    # classes = [
#         "No Finding",
    #     "Atelectasis",
    #     "Cardiomegaly",
    #     "Effusion",
    #     "Infiltration",
    #     "Mass",
    #     "Nodule",
    #     "Pneumonia",
    #     "Pneumothorax",
    #     "Consolidation",
    #     "Edema",
    #     "Emphysema",
    #     "Fibrosis",
    #     "Pleural_Thickening",
    #     "Hernia"
    # ]
    
    def __init__(
            self,
            root: str,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None
    ):
        super().__init__(root, transform=transform, target_transform=target_transform)
        self.root = root
        self.train = train
        
        self.transform = transform
        self.target_transform = target_transform
        
        self.samples = self.load_dataset()
    
    def load_dataset(self):
        if self.train:
            phase = "train"
        else:
            phase = "test"
        
        samples = []
        
        main_dir = os.path.join(self.root, phase)
        for batch_dir in os.listdir(main_dir):
            with open(os.path.join(main_dir, batch_dir), 'rb') as file:
                batch = pickle.load(file)
                samples.extend(batch)
        
        return samples
    
    def __getitem__(self, index):
        img, target = self.samples[index]
        
        
        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)
        
        return img, target
    
    def __len__(self):
        return len(self.samples)