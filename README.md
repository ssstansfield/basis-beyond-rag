# Basis & Beyond · 双书 RAG

**Start here:** open [`Start_RAG.ipynb`](Start_RAG.ipynb), select a **Python 3.12** kernel and choose **Run All**. The notebook prepares the environment, restores the included knowledge base and displays the app inline with a link to open it in a tab. Initial setup needs internet access to download dependencies and the embedding model. Later runs reuse the local cache.

The interface defaults to **English**. Select **中文** in the sidebar to switch the interface and new answers to Chinese. Original book passages retain their original language. For **Light / Dark / System**, use the **⋮ menu** in the top-right corner.

**推荐入口：**打开 [`Start_RAG.ipynb`](Start_RAG.ipynb)，选择 Python 3.12 内核，点击「全部运行」。它会准备依赖、恢复预建知识库、启动应用，并在 Notebook 内展示界面；也可以点击链接在新标签页打开。重复运行启动单元格会复用同一个进程；按 Notebook 说明运行 `rag.stop()` 可停止。需要在浏览器所在电脑本地运行 Jupyter，远程云 Notebook 的 localhost 不指向本机。

项目包含两本 PDF 及 `knowledge/` 中的预建索引。运行时的 `data/`、模型缓存、虚拟环境和临时日志均在 `.gitignore` 中。公开远端仓库为 [`ssstansfield/basis-beyond-rag`](https://github.com/ssstansfield/basis-beyond-rag)。

本地运行的中英文书籍问答应用。现阶段的知识领域是：**美国国债现货与期货、基差与交割、套利交易，以及 LTCM 案例中的杠杆、流动性与风险管理**。

知识来源为 `books/` 下的《The Treasury Bond Basis》（312 页）及《赌金者：长期资本管理公司的升腾与陨落》（314 页）。原 PDF 保持原样。系统引用 **从 1 开始的 PDF 物理页码**，不是书上印刷页码。

当前已建立 **3,902 个片段、384 维 FAISS 索引**：英文书 1,976 个片段，中文书 1,926 个片段；中文书 27 页由 OCR 补充。

## 启动

在 PowerShell 中进入本项目：

```powershell
.\start.ps1
```

然后访问 <http://127.0.0.1:8050>。8050 用于避开本机 Windows 对 8501 等端口的保留。若端口被占用，使用下面的命令自行指定空闲端口：

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8051 --browser.gatherUsageStats false
```

界面有知识领域介绍、问题输入框、示例问题、书籍筛选、回答及可展开的原文证据。提供「Codex 问答」和「仅检索原文」两种模式。仅检索无需登录；问答使用这台电脑已登录的 Codex CLI。

## 从头安装与建库

要求 Python 3.12、Codex CLI；首次下载依赖和 embedding 模型需要联网。

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.lock.txt
codex login
.venv\Scripts\python.exe -m src.ingest
.\start.ps1
```

没有 `uv` 时可以用 `python -m venv .venv` 和 `.venv\Scripts\python.exe -m pip install -r requirements.lock.txt`。开发验证另行安装 `requirements-dev.txt`（包含 pytest、Notebook 执行及浏览器测试工具）。

把新增或更新的 PDF 放进 `books/` 后重新执行 `python -m src.ingest`。文件哈希和流水线配置不变时复用整个索引；重新建库时按文本复用已有向量。`--force` 强制重新处理文本，仍复用相同模型下的已有向量。更换模型或分块参数后会重建。旧索引代保留在 `data/`，新代写入成功后才原子切换 `data/CURRENT`。

## 在 Codex 内检索

本机已注册名为 `books-rag` 的全局 MCP 服务。**新建或重启 Codex 会话**后使用 `/mcp` 查看服务。当前已运行的对话可能需要重新加载工具。

在其他机器上，替换以下两个绝对路径并运行：

```powershell
codex mcp add books-rag -- 'C:\Users\stansfield\Documents\Coding\RAG\.venv\Scripts\python.exe' 'C:\Users\stansfield\Documents\Coding\RAG\mcp_entry.py'
```

服务提供三个只读工具：

- `list_books()`：查看书籍及 `book_id`。
- `search_books(query, book_id?, top_k=6)`：中英文语义检索，最多 12 个片段。
- `get_chunk(chunk_id)`：取回具体片段与出处。

可直接对 Codex 说：「使用 books-rag 知识库，解释 CTD，并引用原书 PDF 页码。」MCP 检索不调用语言模型；Codex 自己根据返回的原文作答。它与网页使用相同的索引。

## 数据和回答流程

```text
PDF → 逐页提取正文 / 图片页本地 OCR → 清理重复页眉页脚
    → 按真实 tokenizer 分块 → 本地 ONNX embedding
    → FAISS（归一化向量内积）+ SQLite（原文、书名、章节、页码）

界面问题 → FAISS 检索 → 原文片段 + 用户问题 → codex exec → 带 [S1] 引用的回答
Codex 对话 → MCP 工具 → 同一 FAISS / SQLite → Codex 组织回答
```

Embedding 模型为 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`，384 维，支持中英文跨语言检索。模型输入限制 128 tokens，因此正文片段上限为 **112 tokens，重叠 20 tokens**，尽量在句末切分，片段不跨页。这里的 token 由该模型的 tokenizer 计算，不能直接换成大模型的 token 数。检索最多保留每页两个片段，减少重叠占满结果。

图片且正文很少的页面使用本地 RapidOCR 补充，OCR 结果按 PDF 哈希及页码缓存。界面会标记 OCR 片段。标题/封面或空白页可能没有可用内容；图表、复杂公式、数字和 OCR 文字需要对照原 PDF。部分章节由 PDF 书签或中文章标题识别；没有可靠章节信息时仍提供书名和页码。

网页通过 `codex exec` 非交互模式生成 JSON 格式回答，校验引用编号是否来自本次检索。证据不足时应明确说明，不将相似度当作正确概率。使用单次临时 Codex 会话，不自动继承其他 MCP 服务。网页只保留当前会话中的最近一次问题与回答。

**数据去向：**书籍解析、OCR、embedding 和检索均在本地完成；点击「Codex 问答」时，问题与本次召回的片段会发给 Codex。模型缓存和索引位于 `data/`，未将书籍上传到托管网站。

## 验证

```powershell
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\check_mcp.py
.venv\Scripts\python.exe scripts\check_codex.py
.venv\Scripts\python.exe scripts\check_notebook.py
.venv\Scripts\python.exe scripts\check_browser.py
```

`check_codex.py` 会真实调用已登录的 Codex，检查国债问答、LTCM 问答、知识库外问题的证据不足响应，以及一个新 Codex 会话是否实际调用已注册 MCP。需要网络并消耗 Codex 用量。它的本地结果在 `tmp/`。`check_notebook.py` 执行真实入口 Notebook，验证启动、进程复用与停止。`check_browser.py` 要求本机安装 Chrome 并已启动网页，验证明暗主题的文字对比度、中英文切换和实际检索交互。

`tests/` 检查中英文分块长度、真实书籍检索与筛选、不存在引用的拦截，以及 Streamlit 输入、提交、原文展示流程。检索和引用检查无法证明所有生成内容都正确，尤其是跨片段计算或复杂表格问题。

2026-11-17 验证结果：5 项 pytest 测试通过（含默认英文、中英文切换后保留问题与结果、按所选语言生成回答）；入口 Notebook 已完整执行，启动、复用、停止检查通过；独立 Chrome 中 Light / Dark 主题对比度检查、中英文切换及原文检索通过，并检查了截图。夜间模式修复移除了固定的浅色背景和深色文字，所有文字、输入框与侧栏跟随原生主题；自定义卡片使用继承颜色，不依赖当前版本未提供的旧 CSS 变量。此前 MCP 三个工具、真实 Codex 问答和新会话 MCP 调用也已通过。

## 文件结构

```text
app.py                  Streamlit 问答界面
Start_RAG.ipynb          推荐入口：准备环境并内嵌启动界面
knowledge/              可携带的当前知识库快照
start.ps1               本地启动脚本
mcp_entry.py            与工作目录无关的 MCP 入口
src/ingest.py           提取 / OCR / 分块 / 建库
src/embedding.py        本地 embedding 与 tokenizer
src/retrieve.py         共用检索逻辑
src/codex_client.py     Codex 回答与引用编号校验
src/i18n.py             英文 / 中文界面文案
src/mcp_server.py       MCP 只读工具
data/CURRENT            当前索引代
data/index-*/           FAISS、SQLite 和 manifest
data/models/            本地模型缓存
data/ocr/               OCR 缓存
tests/                  应用测试
scripts/                MCP 与 Codex 集成验证
```

技术依据：[FastEmbed 支持的模型](https://qdrant.github.io/fastembed/examples/Supported_Models/)、[FAISS](https://github.com/facebookresearch/faiss)、[Codex MCP](https://developers.openai.com/codex/mcp)、[Codex 非交互调用](https://developers.openai.com/codex/noninteractive)、[RapidOCR](https://github.com/RapidAI/RapidOCR)。
