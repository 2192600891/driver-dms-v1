# GPUHub 部署说明

## 平台前提

- GPUHub 官方文档说明其核心形态是 **GPU Container Instance**，支持直接选择镜像创建实例。
- 官方文档同时说明：
  - 计费按实例开关机时间计费，而不是按 GPU 利用率计费。
  - 实例内服务可监听 `6006` 等端口，再通过 GPUHub 控制台或 SSH Tunnel 对外访问。
  - 平台内置镜像默认提供 CUDA / cuDNN，且可继续通过 Conda 安装其他版本。

参考：

- https://docs.gpuhub.com/
- https://docs.gpuhub.com/billing-recharge/billing
- https://docs.gpuhub.com/environment/cuda-cudnn
- https://docs.gpuhub.com/best-practices/ssh-tunnel

## 建议实例环境

- GPU：RTX 4080 / 4080S
- 镜像：优先选带 PyTorch 的官方镜像；如果没有，选 Miniconda 镜像后自行安装 PyTorch
- Python：建议 3.10 及以下均可，本项目服务端代码已兼容较常见的 3.8+

## 部署步骤

```bash
cd /root
git clone <你的仓库地址> driver-dms-v1
cd driver-dms-v1
```

如果使用官方 PyTorch 镜像，先安装其余依赖：

```bash
pip install -r requirements-gpuhub.txt
```

如果镜像未预装 PyTorch，请先安装对应 CUDA 版本的 PyTorch，再安装其余依赖。

## 启动服务

```bash
chmod +x start_gpuhub.sh
PORT=6006 DMS_DEVICE=0 ./start_gpuhub.sh
```

可选环境变量：

- `PORT`：服务端口，默认 `6006`
- `DMS_DEVICE`：推理设备，默认自动选 `0` 或 `cpu`
- `DMS_WEIGHTS`：权重路径，默认 `weights/best.pt`
- `DMS_IMG_SIZE`：推理尺寸，默认 `640`
- `DMS_CONF_THRES`：置信度阈值，默认 `0.6`
- `DMS_IOU_THRES`：NMS 阈值，默认 `0.45`

## 访问方式

- 若 GPUHub 控制台支持实例端口直接暴露，访问 `http://<实例地址>:6006`
- 若仅开放 SSH 访问，可按官方文档建立隧道：

```bash
ssh -CNg -L 6006:127.0.0.1:6006 root@<你的实例地址> -p <端口>
```

随后在本机访问：

```text
http://127.0.0.1:6006
```

## 当前项目改造点

- 新增 `server_app.py`：FastAPI 服务入口
- 新增 `dms_service.py`：复用原有 YOLOv5 + 疲劳检测逻辑，并维护会话统计
- 新增 `web/index.html`：手机端 H5 页面
- 更新 `mydetect.py`：模型加载改为优先自动使用 CUDA
