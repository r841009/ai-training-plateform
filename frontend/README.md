# Frontend

Vue 3 + Element Plus 前端。Project List / Project Detail（Dataset、Training Job、Model Version、Evaluation、Retrain）。建立於 Phase 15。

目前採用 CDN + 靜態檔，先不引入 Node build toolchain。

```powershell
python -m http.server 5173 --directory frontend
```

開啟 `http://127.0.0.1:5173?mock=1`。

預設使用 standalone mock API，不需要 PostgreSQL / Redis / backend。需要切換到真實 API 時在瀏覽器 console 執行：

```js
localStorage.setItem('apiBase', 'http://127.0.0.1:8000')
```

切回 standalone mock：

```js
localStorage.setItem('apiBase', 'mock')
```
