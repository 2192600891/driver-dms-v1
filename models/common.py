                                                     

import math

import numpy as np
import requests
import torch
import torch.nn as nn
from PIL import Image, ImageDraw

from utils.datasets import letterbox
from utils.general import non_max_suppression, make_divisible, scale_coords, xyxy2xywh
from utils.plots import color_list


def autopad(k, p=None):                   
                   
    if p is None:
        p = k // 2 if isinstance(k, int) else [x // 2 for x in k]            
    return p


def DWConv(c1, c2, k=1, s=1, act=True):
                           
    return Conv(c1, c2, k, s, g=math.gcd(c1, c2), act=act)


class Conv(nn.Module):
                          
    def __init__(self, c1, c2, k=1, s=1, p=None, g=1, act=True):                                                  
        super(Conv, self).__init__()
        self.conv = nn.Conv2d(c1, c2, k, s, autopad(k, p), groups=g, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU() if act is True else (act if isinstance(act, nn.Module) else nn.Identity())

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))

    def fuseforward(self, x):
        return self.act(self.conv(x))


class Bottleneck(nn.Module):
                         
    def __init__(self, c1, c2, shortcut=True, g=1, e=0.5):                                              
        super(Bottleneck, self).__init__()
        c_ = int(c2 * e)                   
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c_, c2, 3, 1, g=g)
        self.add = shortcut and c1 == c2

    def forward(self, x):
        return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))


class BottleneckCSP(nn.Module):
                                                                            
    def __init__(self, c1, c2, n=1, shortcut=True, g=1, e=0.5):                                                      
        super(BottleneckCSP, self).__init__()
        c_ = int(c2 * e)                   
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = nn.Conv2d(c1, c_, 1, 1, bias=False)
        self.cv3 = nn.Conv2d(c_, c_, 1, 1, bias=False)
        self.cv4 = Conv(2 * c_, c2, 1, 1)
        self.bn = nn.BatchNorm2d(2 * c_)                            
        self.act = nn.LeakyReLU(0.1, inplace=True)
        self.m = nn.Sequential(*[Bottleneck(c_, c_, shortcut, g, e=1.0) for _ in range(n)])

    def forward(self, x):
        y1 = self.cv3(self.m(self.cv1(x)))
        y2 = self.cv2(x)
        return self.cv4(self.act(self.bn(torch.cat((y1, y2), dim=1))))


class C3(nn.Module):
                                        
    def __init__(self, c1, c2, n=1, shortcut=True, g=1, e=0.5):                                                      
        super(C3, self).__init__()
        c_ = int(c2 * e)                   
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c1, c_, 1, 1)
        self.cv3 = Conv(2 * c_, c2, 1)                 
        self.m = nn.Sequential(*[Bottleneck(c_, c_, shortcut, g, e=1.0) for _ in range(n)])
                                                                                                

    def forward(self, x):
        return self.cv3(torch.cat((self.m(self.cv1(x)), self.cv2(x)), dim=1))


class SPP(nn.Module):
                                                      
    def __init__(self, c1, c2, k=(5, 9, 13)):
        super(SPP, self).__init__()
        c_ = c1 // 2                   
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c_ * (len(k) + 1), c2, 1, 1)
        self.m = nn.ModuleList([nn.MaxPool2d(kernel_size=x, stride=1, padding=x // 2) for x in k])

    def forward(self, x):
        x = self.cv1(x)
        return self.cv2(torch.cat([x] + [m(x) for m in self.m], 1))


class Focus(nn.Module):
                                       
    def __init__(self, c1, c2, k=1, s=1, p=None, g=1, act=True):                                                  
        super(Focus, self).__init__()
        self.conv = Conv(c1 * 4, c2, k, s, p, g, act)
                                          

    def forward(self, x):                                 
        return self.conv(torch.cat([x[..., ::2, ::2], x[..., 1::2, ::2], x[..., ::2, 1::2], x[..., 1::2, 1::2]], 1))
                                            


class Contract(nn.Module):
                                                                               
    def __init__(self, gain=2):
        super().__init__()
        self.gain = gain

    def forward(self, x):
        N, C, H, W = x.size()                                                            
        s = self.gain
        x = x.view(N, C, H // s, s, W // s, s)                     
        x = x.permute(0, 3, 5, 1, 2, 4).contiguous()                     
        return x.view(N, C * s * s, H // s, W // s)                  


class Expand(nn.Module):
                                                                              
    def __init__(self, gain=2):
        super().__init__()
        self.gain = gain

    def forward(self, x):
        N, C, H, W = x.size()                                              
        s = self.gain
        x = x.view(N, s, s, C // s ** 2, H, W)                     
        x = x.permute(0, 3, 4, 1, 5, 2).contiguous()                     
        return x.view(N, C // s ** 2, H * s, W * s)                   


class Concat(nn.Module):
                                                   
    def __init__(self, dimension=1):
        super(Concat, self).__init__()
        self.d = dimension

    def forward(self, x):
        return torch.cat(x, self.d)


class NMS(nn.Module):
                                          
    conf = 0.25                        
    iou = 0.45                 
    classes = None                                   

    def __init__(self):
        super(NMS, self).__init__()

    def forward(self, x):
        return non_max_suppression(x[0], conf_thres=self.conf, iou_thres=self.iou, classes=self.classes)


class autoShape(nn.Module):
                                                                                                               
    img_size = 640                           
    conf = 0.25                            
    iou = 0.45                     
    classes = None                                   

    def __init__(self, model):
        super(autoShape, self).__init__()
        self.model = model.eval()

    def autoshape(self):
        print('autoShape already enabled, skipping... ')                                                
        return self

    def forward(self, imgs, size=640, augment=False, profile=False):
                                                                                                    
                                                        
                                                                                                        
                                                                                                
                                                                           
                                                            
                                                                 
                                                                                                          

        p = next(self.model.parameters())                       
        if isinstance(imgs, torch.Tensor):         
            return self.model(imgs.to(p.device).type_as(p), augment, profile)             

                     
        n, imgs = (len(imgs), imgs) if isinstance(imgs, list) else (1, [imgs])                                    
        shape0, shape1 = [], []                              
        for i, im in enumerate(imgs):
            if isinstance(im, str):                   
                im = Image.open(requests.get(im, stream=True).raw if im.startswith('http') else im)        
            im = np.array(im)            
            if im.shape[0] < 5:                
                im = im.transpose((1, 2, 0))                                          
            im = im[:, :, :3] if im.ndim == 3 else np.tile(im[:, :, None], 3)                     
            s = im.shape[:2]       
            shape0.append(s)               
            g = (size / max(s))        
            shape1.append([y * g for y in s])
            imgs[i] = im          
        shape1 = [make_divisible(x, int(self.stride.max())) for x in np.stack(shape1, 0).max(0)]                   
        x = [letterbox(im, new_shape=shape1, auto=False)[0] for im in imgs]       
        x = np.stack(x, 0) if n > 1 else x[0][None]         
        x = np.ascontiguousarray(x.transpose((0, 3, 1, 2)))                
        x = torch.from_numpy(x).to(p.device).type_as(p) / 255.                    

                   
        with torch.no_grad():
            y = self.model(x, augment, profile)[0]           
        y = non_max_suppression(y, conf_thres=self.conf, iou_thres=self.iou, classes=self.classes)       

                      
        for i in range(n):
            scale_coords(shape1, y[i][:, :4], shape0[i])

        return Detections(imgs, y, self.names)


class Detections:
                                                   
    def __init__(self, imgs, pred, names=None):
        super(Detections, self).__init__()
        d = pred[0].device          
        gn = [torch.tensor([*[im.shape[i] for i in [1, 0, 1, 0]], 1., 1.], device=d) for im in imgs]                  
        self.imgs = imgs                                  
        self.pred = pred                                               
        self.names = names               
        self.xyxy = pred               
        self.xywh = [xyxy2xywh(x) for x in pred]               
        self.xyxyn = [x / g for x, g in zip(self.xyxy, gn)]                   
        self.xywhn = [x / g for x, g in zip(self.xywh, gn)]                   
        self.n = len(self.pred)

    def display(self, pprint=False, show=False, save=False, render=False):
        colors = color_list()
        for i, (img, pred) in enumerate(zip(self.imgs, self.pred)):
            str = f'image {i + 1}/{len(self.pred)}: {img.shape[0]}x{img.shape[1]} '
            if pred is not None:
                for c in pred[:, -1].unique():
                    n = (pred[:, -1] == c).sum()                        
                    str += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "                 
                if show or save or render:
                    img = Image.fromarray(img.astype(np.uint8)) if isinstance(img, np.ndarray) else img           
                    for *box, conf, cls in pred:                           
                                                                               
                        ImageDraw.Draw(img).rectangle(box, width=4, outline=colors[int(cls) % 10])        
            if pprint:
                print(str.rstrip(', '))
            if show:
                img.show(f'image {i}')        
            if save:
                f = f'results{i}.jpg'
                img.save(f)        
                print(f"{'Saving' * (i == 0)} {f},", end='' if i < self.n - 1 else ' done.\n')
            if render:
                self.imgs[i] = np.asarray(img)

    def print(self):
        self.display(pprint=True)                 

    def show(self):
        self.display(show=True)                

    def save(self):
        self.display(save=True)                

    def render(self):
        self.display(render=True)                  
        return self.imgs

    def __len__(self):
        return self.n

    def tolist(self):
                                                                                     
        x = [Detections([self.imgs[i]], [self.pred[i]], self.names) for i in range(self.n)]
        for d in x:
            for k in ['imgs', 'pred', 'xyxy', 'xyxyn', 'xywh', 'xywhn']:
                setattr(d, k, getattr(d, k)[0])                   
        return x


class Classify(nn.Module):
                                                        
    def __init__(self, c1, c2, k=1, s=1, p=None, g=1):                                                  
        super(Classify, self).__init__()
        self.aap = nn.AdaptiveAvgPool2d(1)                  
        self.conv = nn.Conv2d(c1, c2, k, s, autopad(k, p), groups=g)                  
        self.flat = nn.Flatten()

    def forward(self, x):
        z = torch.cat([self.aap(y) for y in (x if isinstance(x, list) else [x])], 1)               
        return self.flat(self.conv(z))                      
