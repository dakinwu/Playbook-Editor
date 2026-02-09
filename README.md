# Dakin-editbible

內部「小寶典」內容編輯、導覽自動生成、知識庫問答與新人引導流程的 Django 專案。

## 功能
- Summernote 內容編輯與儲存
- 依 `h1/h2` 自動生成左側導覽
- 新人引導檢核表（token 連結）
- 知識庫問答（FAISS 檢索 + Azure OpenAI）
- Azure AD SSO 登入

## 專案結構
- `EDIT/` Django 專案根目錄
- `EDIT/EDIT/` Django 設定與路由
- `EDIT/views.py` 主頁、編輯與檢核流程
- `EDIT/chatbot/` 知識庫問答相關邏輯
- `EDIT/newbie/` 資料模型
- `EDIT/templates/` HTML 模板
- `EDIT/static/` 靜態資源
- `EDIT/static/knowledge_base/` 知識庫資料與聊天記錄
- `EDIT/db.sqlite3` SQLite 資料庫（預設）
- `requirements.txt` Python 相依套件

## 環境需求
- Python 3.10（`python_ldap` wheel 為 cp310）
- Windows（使用 `pywin32` / `win32com`）
- 建議 Conda 或 venv

## 本機啟動
1. 建立環境與安裝依賴
   - `conda create -n editplat python=3.10`
   - `conda activate editplat`
   - `pip install -r requirements.txt`
2. 準備設定檔與憑證
   - `EDIT/aad.config.json`（Azure AD 設定）
   - `EDIT/cert.crt`、`EDIT/cert.key`（本機 HTTPS）
3. 確認模板路徑
   - `EDIT/EDIT/settings.py` 的 `TEMPLATES[0].DIRS` 需為 `EDIT/templates` 的絕對路徑
4. 啟動
   - 進入 `EDIT/` 後執行：
     `python manage.py runserver_plus 0.0.0.0:7861 --cert-file cert.crt`

## 資料模型（`newbie`）
- `Bible`：小寶典內容與導覽 HTML
- `friends`：使用者與工作人脈大拼圖資料
- `check`：新人引導檢核表與簽核狀態

## 知識庫流程
- 內容在 `/edit/` 儲存後會：
  - 更新 `Bible.html_code`、`Bible.navbar_code`
  - 產出 `Output.txt`，並建立 `static/knowledge_base/bible/temp_embeddings`
- `/knowledge_chat/` 使用向量檢索與 LLM 回覆

## 注意事項
- `chatbot/views.py` 目前含有硬編碼的 Azure OpenAI 金鑰與端點，建議改為環境變數並移出版本控制。
- `views.py` 內有硬編碼路徑（例如 `C:/Users/.../Output.txt`），搬移專案時需更新。
- `requirements.txt` 內的 `python_ldap` 使用本機 wheel 路徑，換機需更新為自己的 wheel 或替代安裝方式。
- 若部署在無法連外的內網，模板中的 JS/CSS 請改用本地 `static/` 資源，而非 CDN。
- `DEBUG=True` 與 `ALLOWED_HOSTS=['*']` 僅適用於內部開發環境。

## 參考文件
- ~~`啟用步驟.txt`~~
- ~~`檔案說明.txt`~~
- ~~`需新增功能.txt`~~
