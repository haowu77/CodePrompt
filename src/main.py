import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class CodeExporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代码导出工具")
        self.root.geometry("800x600")

        # 默认配置
        self.default_extensions = ('.java', '.yml', '.xml')
        self.default_exclude_dirs = ('target', 'build', '.git')
        self.default_output_dir = os.path.expanduser("~/Downloads")

        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="导出配置", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        # 源目录选择
        ttk.Label(input_frame, text="源码根目录:").grid(row=0, column=0, sticky=tk.W)
        self.source_dir_entry = ttk.Entry(input_frame, width=50)
        self.source_dir_entry.grid(row=0, column=1, padx=5)
        ttk.Button(
            input_frame, text="浏览...",
            command=lambda: self.select_directory(self.source_dir_entry)
        ).grid(row=0, column=2)

        # 输出文件
        ttk.Label(input_frame, text="输出文件路径:").grid(row=1, column=0, sticky=tk.W)
        self.output_file_entry = ttk.Entry(input_frame, width=50)
        self.output_file_entry.grid(row=1, column=1, padx=5)
        self.output_file_entry.insert(0, os.path.join(self.default_output_dir, "exported_code.txt"))
        ttk.Button(
            input_frame, text="浏览...",
            command=lambda: self.select_output_file(self.output_file_entry)
        ).grid(row=1, column=2)

        # 文件扩展名
        ttk.Label(input_frame, text="包含的文件后缀 (逗号分隔):").grid(row=2, column=0, sticky=tk.W)
        self.extensions_entry = ttk.Entry(input_frame, width=50)
        self.extensions_entry.grid(row=2, column=1, padx=5)
        self.extensions_entry.insert(0, ", ".join(self.default_extensions))

        # 排除目录
        ttk.Label(input_frame, text="排除的目录 (逗号分隔):").grid(row=3, column=0, sticky=tk.W)
        self.exclude_dirs_entry = ttk.Entry(input_frame, width=50)
        self.exclude_dirs_entry.grid(row=3, column=1, padx=5)
        self.exclude_dirs_entry.insert(0, ", ".join(self.default_exclude_dirs))

        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(
            button_frame, text="开始导出",
            command=self.start_export, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="清空日志",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=5)

        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="导出日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = ScrolledText(
            log_frame, wrap=tk.WORD,
            font=('Consolas', 10), height=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(
            main_frame, textvariable=self.status_var,
            relief=tk.SUNKEN, anchor=tk.W
        ).pack(fill=tk.X, pady=(5, 0))

    def select_directory(self, entry_widget):
        """选择目录并更新输入框"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dir_path)

    def select_output_file(self, entry_widget):
        """选择输出文件并更新输入框"""
        initial_dir = os.path.dirname(entry_widget.get()) or self.default_output_dir
        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile="exported_code.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("日志已清空")

    def log_message(self, message):
        """向日志区域添加消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def start_export(self):
        """执行导出操作"""
        # 获取用户输入
        root_dir = self.source_dir_entry.get().strip()
        output_file = self.output_file_entry.get().strip()
        include_ext = tuple(
            ext.strip() for ext in self.extensions_entry.get().split(",")
            if ext.strip()
        )
        exclude_dirs = tuple(
            dir_.strip() for dir_ in self.exclude_dirs_entry.get().split(",")
            if dir_.strip()
        )

        # 验证输入
        if not root_dir:
            messagebox.showerror("错误", "请选择源码根目录")
            return
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件路径")
            return
        if not include_ext:
            messagebox.showerror("错误", "请指定至少一个文件后缀")
            return

        # 检查目录是否存在
        if not os.path.exists(root_dir):
            messagebox.showerror("错误", f"路径不存在: {root_dir}")
            return

        # 准备导出
        self.log_message(f"开始导出: {root_dir}")
        self.log_message(f"输出到: {os.path.abspath(output_file)}")
        self.status_var.set("处理中...")
        self.progress["value"] = 0
        self.root.update()

        try:
            total_files = sum(
                1 for root, dirs, files in os.walk(root_dir)
                if not any(exclude in root for exclude in exclude_dirs)
                for file in files
                if file.endswith(include_ext)
            )
            processed_files = 0

            with open(output_file, 'w', encoding='utf-8') as outfile:
                for root, dirs, files in os.walk(root_dir):
                    # 排除指定目录
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]

                    for file in files:
                        if file.endswith(include_ext):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, root_dir)

                            # 更新进度
                            processed_files += 1
                            progress_percent = (processed_files / total_files) * 100
                            self.progress["value"] = progress_percent
                            self.status_var.set(
                                f"处理中: {processed_files}/{total_files} ({progress_percent:.1f}%)"
                            )
                            self.log_message(f"正在处理: {rel_path}")
                            self.root.update()

                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                    content = infile.read()
                                outfile.write(f"\n=== {rel_path} ===\n{content}\n")
                            except Exception as e:
                                error_msg = f"文件读取失败: {rel_path} - {str(e)}"
                                self.log_message(error_msg)
                                outfile.write(f"\n=== {rel_path} ===\n[ERROR: {error_msg}]\n")

            # 完成处理
            self.progress["value"] = 100
            self.status_var.set(f"完成! 已处理 {processed_files} 个文件")
            self.log_message("导出完成!")
            messagebox.showinfo(
                "完成",
                f"成功导出 {processed_files} 个文件到:\n{os.path.abspath(output_file)}"
            )
        except Exception as e:
            self.log_message(f"导出失败: {str(e)}")
            self.status_var.set("导出失败")
            messagebox.showerror("错误", f"导出过程中发生错误:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()

    # 设置现代化主题 (需安装sv_ttk或使用系统主题)
    try:
        import sv_ttk

        sv_ttk.set_theme("light")
    except ImportError:
        pass

    app = CodeExporterApp(root)
    root.mainloop()
