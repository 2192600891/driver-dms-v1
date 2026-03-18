"""Exports a YOLOv5 *.pt model to ONNX and TorchScript formats

Usage:
    $ export PYTHONPATH="$PWD" && python models/export.py --weights ./weights/yolov5s.pt --img 640 --batch 1
"""

import argparse
import sys
import time

sys.path.append('./')                                                  

import torch
import torch.nn as nn

import models
from models.experimental import attempt_load
from utils.activations import Hardswish, SiLU
from utils.general import set_logging, check_img_size

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='./yolov5s.pt', help='weights path')                       
    parser.add_argument('--img-size', nargs='+', type=int, default=[640, 640], help='image size')                 
    parser.add_argument('--batch-size', type=int, default=1, help='batch size')
    opt = parser.parse_args()
    opt.img_size *= 2 if len(opt.img_size) == 1 else 1          
    print(opt)
    set_logging()
    t = time.time()

                        
    model = attempt_load(opt.weights, map_location=torch.device('cpu'))                   
    labels = model.names

            
    gs = int(max(model.stride))                          
    opt.img_size = [check_img_size(x, gs) for x in opt.img_size]                                    

           
    img = torch.zeros(opt.batch_size, 3, *opt.img_size)                                      

                  
    for k, m in model.named_modules():
        m._non_persistent_buffers_set = set()                               
        if isinstance(m, models.common.Conv):                                      
            if isinstance(m.act, nn.Hardswish):
                m.act = Hardswish()
            elif isinstance(m.act, nn.SiLU):
                m.act = SiLU()
                                                 
                                                                       
    model.model[-1].export = True                                  
    y = model(img)           

                        
    try:
        print('\nStarting TorchScript export with torch %s...' % torch.__version__)
        f = opt.weights.replace('.pt', '.torchscript.pt')            
        ts = torch.jit.trace(model, img)
        ts.save(f)
        print('TorchScript export success, saved as %s' % f)
    except Exception as e:
        print('TorchScript export failure: %s' % e)

                 
    try:
        import onnx

        print('\nStarting ONNX export with onnx %s...' % onnx.__version__)
        f = opt.weights.replace('.pt', '.onnx')            
        torch.onnx.export(model, img, f, verbose=False, opset_version=12, input_names=['images'],
                          output_names=['classes', 'boxes'] if y is None else ['output'])

                
        onnx_model = onnx.load(f)                   
        onnx.checker.check_model(onnx_model)                    
                                                                                              
        print('ONNX export success, saved as %s' % f)
    except Exception as e:
        print('ONNX export failure: %s' % e)

                   
    try:
        import coremltools as ct

        print('\nStarting CoreML export with coremltools %s...' % ct.__version__)
                                                                                 
        model = ct.convert(ts, inputs=[ct.ImageType(name='image', shape=img.shape, scale=1 / 255.0, bias=[0, 0, 0])])
        f = opt.weights.replace('.pt', '.mlmodel')            
        model.save(f)
        print('CoreML export success, saved as %s' % f)
    except Exception as e:
        print('CoreML export failure: %s' % e)

            
    print('\nExport complete (%.2fs). Visualize with https://github.com/lutzroeder/netron.' % (time.time() - t))
