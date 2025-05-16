# Comfy 服务系统说明文档

[开发过程记录](Document.md)


## 系统概述

Comfy 服务系统是一个分布式图像生成服务，由三个主要组件组成：
- Comfy Service：核心服务节点，负责实际的图像生成任务
- Comfy Balancer：负载均衡器，负责任务分发和节点管理
- ComfyUI: 负责最终图片渲染生成动作 

## 安装运行说明

- 服务安装说明
  ```shell
  docker-compose up
  ```
- ComfyUI 安装参考
  - 客户端 : Win & MacOS [官网下载](https://www.comfy.org/download)
  - 源码安装: [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)

- 开发调试
  ```shell
  docker-compose down && docker-compose up --build
  ``` 

## 组件说明

### Comfy Balancer

#### 文件说明

```shell
comfy-balancer
├── config.py
├── Dockerfile
├── logger.py
├── main.py
├── requirements.txt
└── web.py
```

### Comfy Service

#### 文件说明

```shell
comfy-service
├── comfy_api.py
├── config.py
├── Dockerfile
├── health_check.py
├── logger.py
├── main.py
├── models.py
├── paths.py
├── requirements.txt
├── web.py
└── workflows
    ├── first-workflow-api.json
    └── first-workflow.json
```

- `workflows`： 配置文件说明，一套流程的api描述文件和模板文件`前缀`命名需要一致，
  - api文件由ui界面导出 ，操作路径`工作流->导出（API）`
  - 模板文件从ComfyUI安装时设置的工作目录获取，路径`{WORK_HOME}/user/default/workflows`


## 部署图

![](Screenshot/deploy-prod.png "生产环境")

![](Screenshot/deploy-dev.png "开发环境")

## 效果

- Logdy 

### 待完善




