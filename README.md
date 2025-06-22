# Estia-AI 个人助手项目文档 V2.0

## 1. 项目简介 (Project Overview)

本项目旨在创建一个完全在本地运行、可通过语音进行实时交互的个性化AI伴侣。经过一系列的技术探索和挑战，我们最终确立了一套以**稳定性**和**高性能**为核心的精简架构，成功地让一个强大的AI大语言模型在个人电脑上“活”了起来。

这个文档记录了项目的核心架构、标准启动流程、开发过程中的心得总结以及未来的发展计划。

## 2. 技术架构 (Technical Architecture)

经过实践检验，我们最终确定的V2.0技术架构如下：

* **AI大脑 (后端服务):**
    * **核心:** 轻量级的 `llama.cpp` 服务器 (`server.exe`)。
    * **职责:** 专门负责高效地加载GGUF格式的大语言模型，并通过API提供推理能力。
    * **优点:** 极其稳定，资源占用小，绕开了所有复杂的Python环境依赖和编译问题。

* **AI身体 (前端应用):**
    * **核心:** 我们自己编写的 `estia` Python项目 (`main.py` + `core/` 模块)。
    * **职责:** 负责语音的输入（录音）与输出（合成播放），以及作为“总指挥”与“大脑”的API进行逻辑交互。

* **核心组件选型:**
    * **LLM 模型:** `Qwen/Qwen3-14B-Instruct-GGUF` (Q4_K_M) - 一个在能力和资源消耗上取得完美平衡的140亿参数模型。
    * **语音识别 (STT):** `openai-whisper` (原生库) - 稳定可靠，识别率高，且不依赖Triton。
    * **语音合成 (TTS):** `edge-tts` + `pygame` - 无需本地模型，声音质量高，播放稳定。

* **通讯协议:**
    * 两者之间通过本地HTTP网络进行通信，采用与OpenAI兼容的API格式。

## 3. 标准启动流程 (Standard Launch Procedure)

本项目采用“大脑”与“身体”分离运行的模式，需要开启两个终端窗口。

#### **第一步：启动“大脑” (Terminal 1)**

1.  打开一个PowerShell终端。
2.  进入 `llama.cpp` 服务器所在的目录 (例如 `D:\estia\llama`)。
3.  执行以下指令来加载模型并启动服务：
    ```powershell
    .\llama-server.exe -m .\models\Mistral-Small-3.1-24B-Instruct-2503-Q4_K_M.gguf -c 8192 -ngl 90
    ```
4.  等待看到 `server listening on http://127.0.0.1:8080` 的提示，**保持此窗口不要关闭**。

#### **第二步：启动“身体” (Terminal 2)**

1.  打开**第二个**全新的PowerShell终端。
2.  激活我们为应用创建的专属Conda环境：
    ```powershell
    conda activate estia_app
    ```
3.  进入我们自己的项目主目录 (例如 `D:\estia`)。
    ```powershell
    cd D:\estia
    ```
4.  运行主程序：
    ```powershell
    $env:HF_ENDPOINT = "https://hf-mirror.com"
    python main.py
    ```
5.  根据提示，按回车键开始录音，与你的AI助手进行对话。在程序运行时，按 `Ctrl+C` 可以优雅地退出。

## 4. 项目总结与心得 (Project Summary & Learnings)

* **环境配置是最大的挑战：** 在Windows上进行AI开发，最大的敌人往往不是代码逻辑，而是底层的编译环境。正确安装Visual Studio C++ Build Tools和NVIDIA CUDA Toolkit是成功编译`llama-cpp-python`等库的前提。
* **模型格式的选择至关重要：** GGUF格式配合`llama.cpp`后端，是目前在个人Windows电脑上运行大模型最稳定、最通用的解决方案。AWQ等格式虽然性能强大，但其依赖的`flash-attention`和`triton`在Windows上存在难以解决的兼容性问题。
* **依赖管理的复杂性：** 一个庞大的项目（如Oobabooga）拥有复杂的依赖树。手动安装或修复依赖时，很容易陷入“按下葫芦浮起瓢”的困境。创建一个干净、最小化的独立环境是最佳实践。
* **从用户到开发者的转变：** 遇到问题时，不能只等待解决方案。通过主动阅读错误日志、分析脚本源代码，甚至直接修改它，我们才能真正掌控一个项目，并从根源上解决问题。

## 5. 未来计划 (Future Roadmap)

我们的AI助手现在只是一个“初生的婴儿”，未来还有无限的成长空间。

* **近期 (Short-term):**
    * **记忆系统 (`memory.py`):** 实现一个简单的短期记忆功能，让她能记住最近几轮的对话内容，进行更连贯的交流。
    * **人格定制 (`personality.py`):** 创建一个灵活的人格管理系统，可以轻松地通过修改配置文件，让她扮演不同的角色（如老师、朋友、游戏伙伴等）。
    * **声音定制 (TTS):** 探索 `GPT-SoVITS` 等声音克隆技术，用你喜欢的声音（甚至你自己的声音）替换掉当前的 `Edge-TTS`。

* **中期 (Mid-term):**
    * **唤醒词 (`Wake Word`):** 研究并集成 `pvporcupine` 等唤醒词引擎，实现通过呼叫她的名字来激活对话，取代“按回车键”的交互方式。
    * **QLoRA 微调:** 尝试对一个基础模型（如Qwen3-8B-Base）进行QLoRA微调，训练一个拥有独一无二知识或说话风格的专属模型。

* **长期 (Long-term):**
    * **视觉能力 (`game_vision.py`):** 集成 `OpenCV`，让她能够“看到”你的游戏画面，并就游戏内容与你展开交流。
    * **工具使用 (Tool Use):** 让她学会使用外部工具，比如查询实时天气、上网搜索信息、执行简单的计算等。

## 6. Q&A / 常见问题解答

**Q1: 为什么在Windows上安装某些AI库时，总是提示缺少C++编译器？**
**A:** 因为这些库（如`llama-cpp-python`）包含C++源代码，需要在使用者的电脑上进行“现场编译”才能安装。这要求系统必须安装了“C++编译工具箱”，最标准的方式就是安装Visual Studio并勾选“使用C++的桌面开发”组件。

**Q2: 为什么 `transformers` 库会报 `triton` 找不到的错误？**
**A:** 这是Windows平台的兼容性“天花板”。新版的`transformers`为了性能，会尝试调用`flash-attention`库，而`flash-attention`又依赖一个叫`triton`的底层库。`triton`官方目前不提供Windows版本，因此这条依赖链在Windows上是断裂的。解决方案是采用不经过这条依赖链的技术栈，比如我们最终选择的`llama.cpp`。

**Q3: 为什么我们最终放弃了Oobabooga，转而使用`llama.cpp`服务器？**
**A:** Oobabooga是一个功能强大但极其复杂的“All-in-One”平台，它的众多依赖（特别是WebUI相关的）在我们复杂的网络和系统环境下，造成了难以解决的兼容性问题。为了追求系统的**极致稳定和简洁**，我们回归本源，只采用其核心的推理引擎`llama.cpp`作为独立的后台服务，从而绕开了所有不必要的复杂性。