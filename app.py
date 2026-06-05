"""
RAG 文档问答系统 - FastAPI 版
==============================
接口:
    POST /upload   - 上传文档（PDF/TXT），自动解析入库
    POST /chat     - 提问，返回 RAG 回答
    GET  /         - 前端页面

运行方式:
    venv\Scripts\python.exe -m uvicorn app:app --reload

然后浏览器打开: http://127.0.0.1:8000
"""

import os
import shutil

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ==================== 配置 ====================
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
UPLOAD_DIR = "./uploads"           # 上传文件临时存放目录
VECTOR_DB_DIR = "./chroma_db"      # 向量数据库目录
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MODEL = "qwen-turbo"
# =============================================

app = FastAPI(title="RAG 文档问答系统")

# 全局向量数据库对象（应用启动时初始化为空，上传文件后构建）
vectorstore = None


def get_embedding():
    """获取 Embedding 模型实例"""
    return DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=API_KEY,
    )


def load_document(filepath: str):
    """根据文件类型选择对应的加载器"""
    if filepath.endswith(".txt"):
        return TextLoader(filepath, encoding="utf-8").load()
    elif filepath.endswith(".pdf"):
        return PyPDFLoader(filepath).load()
    else:
        raise ValueError(f"不支持的文件格式: {filepath}")


def split_documents(docs):
    """切分文档"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def build_vectorstore_from_file(filepath: str):
    """从文件构建向量数据库"""
    global vectorstore

    print(f"[+] 加载文档: {filepath}")
    raw_docs = load_document(filepath)
    print(f"    原始页数/段落数: {len(raw_docs)}")

    print(f"[+] 切分文档...")
    chunks = split_documents(raw_docs)
    print(f"    切分为 {len(chunks)} 个块")

    print(f"[+] 构建向量数据库...")
    embedding = get_embedding()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=VECTOR_DB_DIR,
    )
    print(f"[+] 向量数据库构建完成，共 {len(chunks)} 个向量")
    return vectorstore


def add_to_vectorstore(filepath: str):
    """将新文档追加到已有向量数据库"""
    global vectorstore

    print(f"[+] 加载新文档: {filepath}")
    raw_docs = load_document(filepath)
    chunks = split_documents(raw_docs)
    print(f"    新增 {len(chunks)} 个块")

    if vectorstore is None:
        # 第一次上传，新建数据库
        embedding = get_embedding()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            persist_directory=VECTOR_DB_DIR,
        )
    else:
        # 追加到已有数据库
        vectorstore.add_documents(chunks)

    print(f"[+] 文档已入库")
    return len(chunks)


def answer_question(query: str) -> dict:
    """
    RAG 核心：检索 + 生成
    返回包含答案和引用片段的字典
    """
    global vectorstore

    if vectorstore is None:
        return {"answer": "请先上传文档！", "sources": []}

    # 1. 检索相关片段
    docs = vectorstore.similarity_search(query, k=3)

    # 2. 构建上下文
    context = "\n\n".join([
        f"[{i+1}] {d.page_content}"
        for i, d in enumerate(docs)
    ])

    # 3. 构造 Prompt
    prompt = f"""你是一个严谨的知识助手。请根据以下参考资料回答用户问题。
如果资料中没有相关内容，请回答"根据提供的资料无法回答该问题"。
不要编造信息。

参考资料：
{context}

用户问题：{query}

请给出准确、简洁的回答："""

    # 4. 调用大模型
    llm = Tongyi(model=MODEL)
    answer = llm.invoke(prompt)

    # 5. 返回结果（包含引用来源，方便追溯）
    sources = [
        {"index": i+1, "content": d.page_content[:200] + "..."}
        for i, d in enumerate(docs)
    ]

    return {"answer": answer, "sources": sources}


# ==================== API 接口 ====================

@app.get("/", response_class=HTMLResponse)
def index():
    """前端页面"""
    return HTMLResponse(content=HTML_PAGE)


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    """
    上传文档接口

    测试方式（curl）:
        curl -X POST "http://127.0.0.1:8000/upload" \
             -H "Content-Type: multipart/form-data" \
             -F "file=@你的文件.pdf"
    """
    if not API_KEY:
        return {"error": "API Key 未配置，请检查 .env 文件"}

    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 保存上传的文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 解析并入向量库
        chunk_count = add_to_vectorstore(file_path)
        return {
            "message": "上传成功",
            "filename": file.filename,
            "chunks": chunk_count,
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat")
def chat(query: str = Form(...)):
    """
    问答接口

    测试方式（curl）:
        curl -X POST "http://127.0.0.1:8000/chat" \
             -H "Content-Type: application/x-www-form-urlencoded" \
             -d "query=Python列表和元组有什么区别"
    """
    if not API_KEY:
        return {"error": "API Key 未配置，请检查 .env 文件"}

    try:
        result = answer_question(query)
        return result
    except Exception as e:
        return {"error": str(e)}


# ==================== 前端页面 HTML ====================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG 智能文档问答系统</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .app-container {
            max-width: 1000px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            height: calc(100vh - 40px);
        }
        .sidebar {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
        }
        .sidebar h2 {
            font-size: 16px;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        .upload-area {
            border: 2px dashed #c0c0c0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 15px;
        }
        .upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .upload-area.dragover {
            border-color: #667eea;
            background: #eef0ff;
        }
        .upload-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .upload-text {
            font-size: 13px;
            color: #666;
        }
        .upload-text small {
            color: #999;
            display: block;
            margin-top: 4px;
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            width: 100%;
            padding: 10px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .upload-btn:hover { background: #5a6fd6; }
        .upload-btn:disabled { background: #ccc; cursor: not-allowed; }
        .upload-status {
            margin-top: 12px;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            display: none;
        }
        .upload-status.show { display: block; }
        .upload-status.success { background: #e8f5e9; color: #2e7d32; }
        .upload-status.error { background: #ffebee; color: #c62828; }
        .upload-status.info { background: #e3f2fd; color: #1565c0; }
        .file-list {
            flex: 1;
            overflow-y: auto;
        }
        .file-list h3 {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }
        .file-item {
            display: flex;
            align-items: center;
            padding: 8px 10px;
            background: #f8f9fa;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 13px;
        }
        .file-item .icon {
            margin-right: 8px;
            font-size: 16px;
        }
        .file-item .name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .file-item .chunks {
            font-size: 11px;
            color: #888;
        }
        .main-panel {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            padding: 20px;
            border-bottom: 1px solid #f0f0f0;
        }
        .chat-header h1 {
            font-size: 18px;
            color: #333;
        }
        .chat-header p {
            font-size: 13px;
            color: #888;
            margin-top: 4px;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.7;
            word-wrap: break-word;
        }
        .message.user {
            align-self: flex-end;
            background: #667eea;
            color: white;
        }
        .message.assistant {
            align-self: flex-start;
            background: #f5f5f5;
            color: #333;
        }
        .message.assistant .sources {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
        }
        .message.assistant .sources-title {
            font-size: 12px;
            color: #888;
            margin-bottom: 6px;
        }
        .message.assistant .source-item {
            font-size: 12px;
            color: #666;
            background: white;
            padding: 6px 10px;
            border-radius: 6px;
            margin-bottom: 4px;
        }
        .message.loading {
            align-self: flex-start;
            background: #f5f5f5;
            color: #888;
            font-style: italic;
        }
        .message.error {
            align-self: flex-start;
            background: #ffebee;
            color: #c62828;
        }
        .welcome-msg {
            text-align: center;
            color: #999;
            padding: 40px 20px;
        }
        .welcome-msg .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .welcome-msg h3 {
            font-size: 16px;
            color: #666;
            margin-bottom: 8px;
        }
        .welcome-msg p {
            font-size: 13px;
        }
        .input-area {
            padding: 15px 20px;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        .input-area input:focus {
            border-color: #667eea;
        }
        .input-area button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .input-area button:hover { background: #5a6fd6; }
        .input-area button:disabled { background: #ccc; cursor: not-allowed; }
        @media (max-width: 768px) {
            .app-container {
                grid-template-columns: 1fr;
                height: auto;
            }
            .sidebar { display: none; }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <h2>文档上传</h2>
            <div class="upload-area" onclick="document.getElementById('fileInput').click()" id="uploadArea">
                <div class="upload-icon">&#128193;</div>
                <div class="upload-text">
                    点击或拖拽上传文档
                    <small>支持 .txt / .pdf</small>
                </div>
            </div>
            <input type="file" id="fileInput" class="file-input" accept="text/plain,application/pdf">
            <button class="upload-btn" id="uploadBtn" onclick="uploadFile()">开始上传</button>
            <div class="upload-status" id="uploadStatus"></div>
            <div class="file-list" id="fileList"></div>
        </div>

        <div class="main-panel">
            <div class="chat-header">
                <h1>RAG 智能文档问答</h1>
                <p>基于检索增强生成（Retrieval-Augmented Generation）技术</p>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="welcome-msg">
                    <div class="icon">&#128172;</div>
                    <h3>开始对话</h3>
                    <p>先上传文档，然后在这里提问<br>我会基于文档内容为你解答</p>
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="queryInput" placeholder="输入你的问题，按回车发送...">
                <button id="sendBtn" onclick="sendMessage()">发送</button>
            </div>
        </div>
    </div>

    <script>
        // 拖拽上传支持
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateUploadArea(files[0].name);
            }
        });
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateUploadArea(fileInput.files[0].name);
            }
        });

        function updateUploadArea(filename) {
            uploadArea.innerHTML = `
                <div class="upload-icon">&#9989;</div>
                <div class="upload-text">已选择: ${escapeHtml(filename)}<small>点击重新选择</small></div>
            `;
        }

        function showStatus(msg, type) {
            const status = document.getElementById('uploadStatus');
            status.textContent = msg;
            status.className = 'upload-status show ' + type;
        }

        async function uploadFile() {
            if (!fileInput.files.length) {
                showStatus('请先选择文件', 'error');
                return;
            }

            const btn = document.getElementById('uploadBtn');
            btn.disabled = true;
            btn.textContent = '上传中...';
            showStatus('正在解析文档并构建向量库...', 'info');

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                const res = await fetch('/upload', { method: 'POST', body: formData });
                const data = await res.json();

                if (data.error) {
                    showStatus('错误: ' + data.error, 'error');
                } else {
                    showStatus(`上传成功！切分为 ${data.chunks} 个文本块`, 'success');
                    addFileToList(data.filename, data.chunks);
                    // 清空选择
                    fileInput.value = '';
                    uploadArea.innerHTML = `
                        <div class="upload-icon">&#128193;</div>
                        <div class="upload-text">点击或拖拽上传文档<small>支持 .txt / .pdf</small></div>
                    `;
                }
            } catch (e) {
                showStatus('请求失败: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '开始上传';
            }
        }

        function addFileToList(filename, chunks) {
            const list = document.getElementById('fileList');
            if (!list.querySelector('h3')) {
                list.innerHTML = '<h3>已上传文档</h3>';
            }
            const icon = filename.endsWith('.pdf') ? '&#128196;' : '&#128209;';
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <span class="icon">${icon}</span>
                <span class="name">${escapeHtml(filename)}</span>
                <span class="chunks">${chunks} 块</span>
            `;
            list.appendChild(item);
        }

        const chatMessages = document.getElementById('chatMessages');
        const queryInput = document.getElementById('queryInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(content, type) {
            const msg = document.createElement('div');
            msg.className = 'message ' + type;
            msg.innerHTML = content;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return msg;
        }

        async function sendMessage() {
            const query = queryInput.value.trim();
            if (!query) return;

            // 添加用户消息
            addMessage(escapeHtml(query), 'user');
            queryInput.value = '';

            // 显示加载中
            const loadingMsg = addMessage('思考中...', 'loading');
            sendBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('query', query);

                const res = await fetch('/chat', { method: 'POST', body: formData });
                const data = await res.json();

                // 移除加载消息
                loadingMsg.remove();

                if (data.error) {
                    addMessage('&#10071; ' + escapeHtml(data.error), 'error');
                    return;
                }

                // 构建回答内容
                let html = escapeHtml(data.answer);
                if (data.sources && data.sources.length) {
                    html += '<div class="sources">';
                    html += '<div class="sources-title">参考片段</div>';
                    data.sources.forEach(s => {
                        html += `<div class="source-item"><strong>[${s.index}]</strong> ${escapeHtml(s.content)}</div>`;
                    });
                    html += '</div>';
                }
                addMessage(html, 'assistant');

            } catch (e) {
                loadingMsg.remove();
                addMessage('&#10071; 请求失败: ' + escapeHtml(e.message), 'error');
            } finally {
                sendBtn.disabled = false;
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
