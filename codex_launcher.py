import json
import os
import re
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
DEFAULT_SESSIONS = [
    {"note": "纹身", "session_id": "019d6d14-8139-7bb3-a520-2eaf0b63527c"},
    {"note": "TG脚本", "session_id": "019d8069-a1f2-7891-8472-9ed2befb7384"},
    {"note": "词根导出", "session_id": "019d8643-ffeb-7fd2-8cca-fe1e28799f20"},
    {"note": "哈啰", "session_id": "019d86d8-fe62-7952-aba1-2781271710c8"},
    {"note": "经期计算器", "session_id": "019d8bda-8ee1-79c3-9179-87be0235b8d7"},
    {"note": "写推文", "session_id": "019d7f93-93b4-7002-b90e-c10760967e81"},
    {"note": "抢单", "session_id": "019d92ed-2b7c-7550-a3b1-8aef3aaf2286"},
    {"note": "说明书", "session_id": "019d9af0-cca7-7cd2-b276-2b2ee8d31659"},
    {"note": "变身", "session_id": "019d9fbc-1ef3-7c20-b5fa-569dc0dfe01d"},
    {"note": "主页", "session_id": "019da26d-61e6-7d73-ab35-ffa650033e2f"},
]


class CodexLauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Codex 启动器")
        self.geometry("920x560")
        self.minsize(840, 500)

        self.data_path = Path(__file__).with_name("sessions.json")
        self.sessions = self.load_sessions()

        self.note_var = tk.StringVar()
        self.session_var = tk.StringVar()
        self.yolo_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="就绪")

        self.build_ui()
        self.refresh_table()

    def build_ui(self) -> None:
        form = ttk.Frame(self, padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="备注").grid(row=0, column=0, padx=(0, 8), pady=6, sticky="w")
        ttk.Entry(form, textvariable=self.note_var, width=22).grid(row=0, column=1, padx=(0, 16), pady=6, sticky="we")

        ttk.Label(form, text="会话号").grid(row=0, column=2, padx=(0, 8), pady=6, sticky="w")
        ttk.Entry(form, textvariable=self.session_var, width=45).grid(row=0, column=3, padx=(0, 16), pady=6, sticky="we")

        ttk.Button(form, text="添加/更新", command=self.add_or_update_session).grid(row=0, column=4, padx=(0, 8), pady=6)
        ttk.Button(form, text="清空输入", command=self.clear_inputs).grid(row=0, column=5, pady=6)

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=2)

        table_wrap = ttk.Frame(self, padding=(12, 0, 12, 0))
        table_wrap.pack(fill="both", expand=True)

        self.table = ttk.Treeview(
            table_wrap,
            columns=("note", "session_id"),
            show="headings",
            selectmode="extended",
        )
        self.table.heading("note", text="备注")
        self.table.heading("session_id", text="会话号")
        self.table.column("note", width=200, anchor="w")
        self.table.column("session_id", width=650, anchor="w")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<Double-1>", self.load_selected_to_inputs)

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(self, padding=12)
        actions.pack(fill="x")

        ttk.Checkbutton(actions, text="启用 YOLO 模式", variable=self.yolo_var).pack(side="left")
        ttk.Button(actions, text="启动选中", command=self.launch_selected).pack(side="right", padx=(8, 0))
        ttk.Button(actions, text="一键全部启动", command=self.launch_all).pack(side="right", padx=(8, 0))
        ttk.Button(actions, text="删除选中", command=self.delete_selected).pack(side="right", padx=(8, 0))

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(12, 0, 12, 12))
        status.pack(fill="x")

    def load_sessions(self) -> list[dict[str, str]]:
        if not self.data_path.exists():
            self.data_path.write_text(json.dumps(DEFAULT_SESSIONS, ensure_ascii=False, indent=2), encoding="utf-8")
            return list(DEFAULT_SESSIONS)
        try:
            data = json.loads(self.data_path.read_text(encoding="utf-8"))
            return [
                {
                    "note": str(item.get("note", "")).strip(),
                    "session_id": str(item.get("session_id", "")).strip(),
                }
                for item in data
                if item.get("note") and item.get("session_id")
            ]
        except Exception:
            backup_path = self.data_path.with_suffix(".broken.json")
            self.data_path.replace(backup_path)
            self.data_path.write_text(json.dumps(DEFAULT_SESSIONS, ensure_ascii=False, indent=2), encoding="utf-8")
            return list(DEFAULT_SESSIONS)

    def save_sessions(self) -> None:
        self.data_path.write_text(json.dumps(self.sessions, ensure_ascii=False, indent=2), encoding="utf-8")

    def refresh_table(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)
        for session in self.sessions:
            self.table.insert("", "end", values=(session["note"], session["session_id"]))

    def clear_inputs(self) -> None:
        self.note_var.set("")
        self.session_var.set("")

    def load_selected_to_inputs(self, _event=None) -> None:
        selected = self.table.selection()
        if len(selected) != 1:
            return
        note, session_id = self.table.item(selected[0], "values")
        self.note_var.set(note)
        self.session_var.set(session_id)
        self.status_var.set("已加载到输入框，可直接更新")

    def validate_session_id(self, session_id: str) -> bool:
        return bool(UUID_PATTERN.match(session_id))

    def add_or_update_session(self) -> None:
        note = self.note_var.get().strip()
        session_id = self.session_var.get().strip()

        if not note:
            messagebox.showwarning("提示", "请先输入备注")
            return
        if not session_id:
            messagebox.showwarning("提示", "请先输入会话号")
            return
        if not self.validate_session_id(session_id):
            messagebox.showwarning("提示", "会话号格式不正确，应为 8-4-4-4-12 的 UUID")
            return

        for item in self.sessions:
            if item["session_id"] == session_id:
                item["note"] = note
                self.save_sessions()
                self.refresh_table()
                self.status_var.set(f"已更新：{note}")
                return

        self.sessions.append({"note": note, "session_id": session_id})
        self.save_sessions()
        self.refresh_table()
        self.status_var.set(f"已添加：{note}")

    def delete_selected(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的会话")
            return

        values_to_delete = {self.table.item(iid, "values")[1] for iid in selected}
        self.sessions = [item for item in self.sessions if item["session_id"] not in values_to_delete]
        self.save_sessions()
        self.refresh_table()
        self.status_var.set(f"已删除 {len(values_to_delete)} 条会话")

    def build_command(self, session_id: str) -> str:
        cmd = f"codex resume {session_id}"
        if self.yolo_var.get():
            cmd += " --yolo"
        return cmd

    def open_terminal(self, command: str) -> None:
        if os.name == "nt":
            subprocess.Popen(
                ["cmd", "/k", command],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            return
        subprocess.Popen(["bash", "-lc", command])

    def launch_selected(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("提示", "请至少选择一个会话")
            return

        commands = []
        for iid in selected:
            _, session_id = self.table.item(iid, "values")
            commands.append(self.build_command(session_id))

        for command in commands:
            self.open_terminal(command)

        self.status_var.set(f"已启动 {len(commands)} 个会话")

    def launch_all(self) -> None:
        if not self.sessions:
            messagebox.showinfo("提示", "当前没有可启动会话")
            return

        commands = [self.build_command(item["session_id"]) for item in self.sessions]
        for command in commands:
            self.open_terminal(command)

        self.status_var.set(f"已一键启动全部会话，共 {len(commands)} 个")


def main() -> None:
    app = CodexLauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
