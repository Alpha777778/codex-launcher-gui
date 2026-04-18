# Codex GUI 启动器

一个本地 GUI 面板，用来管理并启动 `codex resume <会话号>` 命令。

## 功能

- 添加会话（备注 + 会话号）
- 双击列表任意行可回填输入框后更新
- 左侧“勾选”列支持逐行点击勾选/取消
- 启动勾选（每个会话单独打开一个终端）
- 一键全部启动
- 可勾选 `YOLO` 模式：
  - 勾选：`codex resume <会话号> --yolo`
  - 不勾选：`codex resume <会话号>`
- 删除勾选会话
- 新建会话按钮：执行 `C:/Users/Administrator/Desktop/X.bat.lnk`
- 会话持久化保存到 `sessions.json`

## 运行环境

- Windows（推荐）
- Python 3.10+
- 已安装并可直接使用 `codex` 命令

## 启动

```bash
python codex_launcher.py
```

## 使用说明

1. 输入“备注”和“会话号”，点击“添加/更新”。
2. 点击表格第一列“勾选”符号（☐/☑）选择要操作的会话。
3. 点击“启动勾选”启动当前勾选会话。
4. 点击“一键全部启动”依次启动所有会话。
5. 点击“新建会话”会执行桌面快捷方式脚本。
6. 勾选“启用 YOLO 模式”时，启动命令自动追加 `--yolo`。

## 数据文件

- `sessions.json`：会话清单，格式如下：

```json
[
  {
    "note": "示例备注",
    "session_id": "019d8bda-8ee1-79c3-9179-87be0235b8d7"
  }
]
```

## 常见问题

- 提示找不到 `codex`：请先确认 `codex` 已安装并在系统 PATH 中。
- 提示找不到新建会话脚本：请确认 `C:/Users/Administrator/Desktop/X.bat.lnk` 存在。