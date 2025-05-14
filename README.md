# 项目背景
项目中需要利用大语言模型进行文生图（Text-to-Image）服务。我们使用 ComfyUI 结合
StoryDiffusion 插件构建了文生图工作流。现在需要你将这个能力包装成一个稳定的微服务，供其
他服务调用。

## 技术要求

### 环境搭建与验证

- [x] 在本地成功安装 ComfyUI 环境
  - [x] 为快速验证主要流程和逻辑，先使用Desktop Application完成ComfyUI的安装与配置(MacOS M1)。
    - Desktop 默认 127.0.0.1:8000 
    - MacOS调试阶段无法使用CUDA，暂时使用CPU模式开发
  - [ ] _**源码安装与启动，部署环节待优化；**_
- [x] 安装并配置 StoryDiffusion 插件
  - [x] Q1:插件拷入`custom_nodes`加载失败,通过UI上Manager 查看ComfyUI_StoryDiffusion是否安装成功,出现"Import Failed"
    - 排查过程: 分别手动安装omegaconf，cv2(opencv-python)后pass；
- [x] 验证文生图功能可以正常使用
    - [x] 参考txt2img示例进行还原
      - [x] error： 'label_emb.0.0.weight' -> 原因使用错误模型无此参数
        - `wget https://huggingface.co/RunDiffusion/Juggernaut-XL-v8/resolve/9022a900377ce2d3303d3e6d86b09f6874e1e2a7/juggernautXL_v8Rundiffusion.safetensors`
          - `cp juggernautXL_v8Rundiffusion.safetensors ./ComfyUI/models/checkpoints`
    - ![CleanShot 2025-05-14 at 21.51.09.png](Screenshot/CleanShot%202025-05-14%20at%2021.51.09.png)
 
---- 

### 接口服务开发 (comfy-service)
#### 开发准备
1.  ComfyUI接口能力边界，评估comfy-service服务的调用形式。
    - 参考 [Built in Routes](https://docs.comfy.org/essentials/comfyui-server/comms_routes) 明确待用接口
    - 参考 server.py
2. 技术选型，ComfyServer 使用的是python语言，


#### 结论
- 技术选型使用python，原因

- [ ] 提供异步的文生图接口
    - 新增POST `generate` 包装POST `/prompt`
- [ ] 支持任务状态查询
    - 复用GET `/prompt`
- [ ] 支持任务取消
    - 包装POST `/interrupt`
- [ ] 合理的错误处理机制
- [ ] 日志记录系统

#### 接口示例
```shell

POST /api/v1/generate
GET /api/v1/tasks/{taskId}
DELETE /api/v1/tasks/{taskId}

```

### 分布式部署方案(也可以使用现有云服务商提供的类似功能服务)
> 设计一个支持多机器、多GPU的分布式部署方案：

- [ ] 提供完整的 Dockerfile
- [ ] 设计任务分发机制
- [ ] 实现基于GPU使用率的负载均衡
- [ ] 考虑故障转移机制
- [ ] 监控告警方案

### 技术栈要求
-  后端框架：Spring Boot/Python Flask/FastAPI/等 （任选）
-  任务队列：Redis/RabbitMQ/等 （任选）
-  容器化：Docker
-  服务器/GPU按需调度http://github.com/konbluesky/ComfyUI-Learning


## 命令
```shell
./.venv/bin/python3 -c "import sys; print(sys.executable)" 

source .venv/bin/activate
python3 -c "import sys; print(sys.executable)"     
deactivate
python3 -c "import sys; print(sys.executable)"



conda env create -n giggle-assignment

label_emb.0.0.weight

```

#### References

- https://github.com/smthemex/ComfyUI_StoryDiffusion
- https://github.com/comfyanonymous/ComfyUI
- https://docs.comfy.org/get_started/introduction
- https://github.com/zjf2671/hh-mcp-comfyui