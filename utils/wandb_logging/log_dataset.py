import argparse
from pathlib import Path

import yaml

from wandb_utils import WandbLogger
from utils.datasets import LoadImagesAndLabels

WANDB_ARTIFACT_PREFIX = 'wandb-artifact://'


def create_dataset_artifact(opt):
    with open(opt.data) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)             
    logger = WandbLogger(opt, '', None, data, job_type='create_dataset')
    nc, names = (1, ['item']) if opt.single_cls else (int(data['nc']), data['names'])
    names = {k: v for k, v in enumerate(names)}                       
    logger.log_dataset_artifact(LoadImagesAndLabels(data['train']), names, name='train')            
    logger.log_dataset_artifact(LoadImagesAndLabels(data['val']), names, name='val')          

                                          
    data['train'] = WANDB_ARTIFACT_PREFIX + str(Path(opt.project) / 'train')
    data['val'] = WANDB_ARTIFACT_PREFIX + str(Path(opt.project) / 'val')
    path = opt.data if opt.overwrite_config else opt.data.replace('.', '_wandb.')                          
    data.pop('download', None)                                                                 
    with open(path, 'w') as f:
        yaml.dump(data, f)
    print("New Config file => ", path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/coco128.yaml', help='data.yaml path')
    parser.add_argument('--single-cls', action='store_true', help='train as single-class dataset')
    parser.add_argument('--project', type=str, default='YOLOv5', help='name of W&B Project')
    parser.add_argument('--overwrite_config', action='store_true', help='overwrite data.yaml')
    opt = parser.parse_args()

    create_dataset_artifact(opt)
