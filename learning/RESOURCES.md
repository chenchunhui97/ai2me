# 资料来源与固定版本

现有三个资料目录保持独立 Git 仓库，在主仓库中忽略。准确 URL 与建档时 HEAD 见 [references.json](references.json)；这里只记录提交，不声称本地工作区与上游完全一致。自己的笔记、修改和验证结果保存到主仓库。

建档过程中新增的 `InfraTech/` 来源为 `https://github.com/CalvinXKY/InfraTech.git`，也保持独立并忽略。检查时尚无可用 HEAD，记录在 manifest 的待补充项，克隆完成后再核实提交版本。

## 按当前任务使用

| 阶段 | 本地资料 | 使用方法 |
|---|---|---|
| T01～T07 | `AI-fundamentals/06_llm_theory_and_fundamentals/`、`09_inference_system/prefill_decode/`、`09_inference_system/kv_cache/` | 先独立推导，再核对；具体数值需要结合模型配置复算 |
| T08～T09 | `AI-fundamentals/02_gpu_programming/04_profiling/` | 学测量方法，先做自己的基线 |
| T10～T13 | `AI-fundamentals/09_inference_system/`、nano-vLLM 和 vLLM 官方源码 | 官方源码固定 commit，文章作为导读 |
| T14～T17 | `AI-fundamentals/02_gpu_programming/`、`AI-System/Labs/BasicLabs/Lab3/` | CUDA 概念、样例与真实 kernel 实验 |
| T18～T24 | `AI-fundamentals/01_hardware_architecture/`、`09_inference_system/`、NVIDIA/昇腾官方文档 | 核实硬件限制、框架版本和真实 API |
| 平台背景 | `aik8s/` | 按需参考部署；当前先补计算和实现 |

本地目录与文中内容可能变动；模型、论文、新架构及性能数字必须核实原始出处，不能仅凭文章存在就视为可靠结论。

## 在新机器重建资料目录

在仓库根目录运行下面代码会按 manifest 克隆缺失的资料仓库并检出记录的版本；已存在的目录会跳过，不覆盖本地改动。需要联网，属于可选操作。

```python
import json
from pathlib import Path
import subprocess

manifest = json.loads(Path('learning/references.json').read_text())
for item in manifest['repositories']:
    destination = Path(item['path'])
    if destination.exists():
        print('保留已有目录:', destination)
        continue
    subprocess.run(['git', 'clone', item['url'], str(destination)], check=True)
    subprocess.run(['git', '-C', str(destination), 'checkout', '--detach', item['commit']], check=True)
```

## 官方与源码入口

- [PyTorch 文档](https://docs.pytorch.org/docs/stable/)
- [nano-vLLM](https://github.com/GeeeekExplorer/nano-vllm)
- [vLLM](https://github.com/vllm-project/vllm)
- [SGLang](https://github.com/sgl-project/sglang)
- [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [Nsight Systems](https://docs.nvidia.com/nsight-systems/)
- [Nsight Compute](https://docs.nvidia.com/nsight-compute/)
- [Ascend 开发者文档](https://www.hiascend.com/document)

使用时把实际 commit、版本和查阅日期写进成果。暂不提前为未读框架生成虚构调用链。
