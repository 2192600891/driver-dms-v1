import os
import numpy as np
import cv2
import torch
from numpy import random
                 
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords,\
    set_logging
from utils.torch_utils import select_device, time_synchronized
 
 
def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
                                                                                                    
    shape = img.shape[:2]                                 
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
 
                             
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:                                                          
        r = min(r, 1.0)
 
                     
    ratio = r, r                        
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]              
    if auto:                     
        dw, dh = np.mod(dw, 32), np.mod(dh, 32)              
    elif scaleFill:           
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]                        
 
    dw /= 2                               
    dh /= 2
 
    if shape[::-1] != new_unpad:          
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)              
    return img, ratio, (dw, dh)
 
 
weights = os.getenv("DMS_WEIGHTS", r'weights/best.pt')
imgsz = int(os.getenv("DMS_IMG_SIZE", "640"))
opt_conf_thres = float(os.getenv("DMS_CONF_THRES", "0.6"))
opt_iou_thres = float(os.getenv("DMS_IOU_THRES", "0.45"))


def _resolve_device():
    configured = os.getenv("DMS_DEVICE", "").strip()
    if configured:
        return configured
    return "0" if torch.cuda.is_available() else "cpu"
 
            
set_logging()
device = select_device(_resolve_device())
half = device.type != 'cpu'                                         
 
            
model = attempt_load(weights, map_location=device)                   
imgsz = check_img_size(imgsz, s=model.stride.max())                  
if half:
    model.half()           

if device.type != 'cpu':
    warmup = torch.zeros((1, 3, imgsz, imgsz), device=device)
    model(warmup.half() if half else warmup)
 
                      
names = model.module.names if hasattr(model, 'module') else model.names
colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
 
 
def predict(im0s):
 
                                    
    img = letterbox(im0s, new_shape=imgsz)[0]
             
    img = img[:, :, ::-1].transpose(2, 0, 1)                            
    img = np.ascontiguousarray(img)
 
    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()                    
    img /= 255.0                        
    if img.ndimension() == 3:
        img = img.unsqueeze(0)
 
               
                                               
    pred = model(img)[0]
 
               
    pred = non_max_suppression(pred, opt_conf_thres, opt_iou_thres)
 
                        
    ret = []
    for i, det in enumerate(pred):                        
        if len(det):
                                                     
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s.shape).round()
                           
            for *xyxy, conf, cls in reversed(det):
                label = f'{names[int(cls)]}'
                prob = round(float(conf) * 100, 2)           
                ret_i = [label, prob, xyxy]
                ret.append(ret_i)
  
    return ret


def runtime_info():
    return {
        "device": str(device),
        "device_type": device.type,
        "weights": weights,
        "img_size": imgsz,
        "conf_thres": opt_conf_thres,
        "iou_thres": opt_iou_thres,
        "half": half,
        "cuda_available": torch.cuda.is_available(),
    }
