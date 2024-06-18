# Chimera

Have a wonderful adverture in a virtual world.

## Install

```shell
conda create -n chimera python==3.10.14
conda activate chimera
pip install -r requirements.txt
```

## 角色聊天服务

```shell
python server.py --memory_path "小说路径"
```

## 角色聊天DEMO

```shell
streamlit run chat.py
```

## webui

```shell
streamlit run webui.py
```

![](./assets/webui.png)

## Model
```shell
pip install -U huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download --resume-download shibing624/text2vec-base-chinese --local-dir /Users/kky/project/Chimera/models/text2vec-base-chinese --local-dir-use-s
imlinks False
```