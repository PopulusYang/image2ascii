import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
import cv2
import os
import shutil
import threading
import img2ascii
import platform
import subprocess
import json
import math
import sys

# Handle CLI mode for packaged executable
if len(sys.argv) > 1 and sys.argv[1] == "--play":
    try:
        delay = float(sys.argv[2])
        skip = int(sys.argv[3])
    except:
        delay = 0.02
        skip = 0
    img2ascii.show(delay, skip)
    sys.exit(0)

CONFIG_FILE = "config.json"

translations = {
    "en": {
        "title": "Image2Ascii Player",
        "instruction": "Select a video file to convert and play:",
        "browse": "Browse",
        "resolution": "Resolution: -",
        "resolution_fmt": "Resolution: {}x{} (Frames: {} -> {})",
        "resolution_unknown": "Resolution: Unknown",
        "ascii_label": "Ascii Characters (Dark -> Light):",
        "speed_label": "Frame Delay (s):",
        "scale_label": "Scale Factor:",
        "skip_label": "Frame Skip:",
        "scaled_res": "Scaled Resolution: -",
        "scaled_res_fmt": "Scaled Resolution: {}x{}",
        "status_ready": "Ready",
        "status_starting": "Starting...",
        "status_extracting": "Extracting frames...",
        "status_generating": "Generating ASCII...",
        "status_playing": "Playing...",
        "status_done": "Done.",
        "status_error": "Error occurred.",
        "btn_process": "Process & Play",
        "btn_processing": "Processing...",
        "btn_clear": "Clear Cache",
        "msg_error_title": "Error",
        "msg_select_video": "Please select a video file first.",
        "msg_success_title": "Success",
        "msg_process_complete": "Processing complete! Playing in terminal.",
        "msg_cache_cleared": "Cache cleared.",
        "msg_confirm_title": "Confirm",
        "msg_confirm_clear": "Are you sure you want to clear the cache (imgout and textout)?",
        "msg_warning_title": "Warning",
        "msg_high_res": "Scaled resolution ({}x{}) is high (>150x150).\nPlayback might not work properly.\n\nContinue?",
        "msg_error_cache": "Failed to clear cache: {}",
        "text_space": "Space",
        "levels_label": "Levels:",
    },
    "zh_cn": {
        "title": "Image2Ascii 播放器",
        "instruction": "选择视频文件进行转换和播放：",
        "browse": "浏览",
        "resolution": "分辨率: -",
        "resolution_fmt": "分辨率: {}x{} (帧数: {} -> {})",
        "resolution_unknown": "分辨率: 未知",
        "ascii_label": "Ascii 字符 (暗 -> 亮):",
        "speed_label": "帧延迟 (秒):",
        "scale_label": "缩放比例:",
        "skip_label": "跳帧数:",
        "scaled_res": "缩放后分辨率: -",
        "scaled_res_fmt": "缩放后分辨率: {}x{}",
        "status_ready": "就绪",
        "status_starting": "启动中...",
        "status_extracting": "提取帧...",
        "status_generating": "生成 ASCII...",
        "status_playing": "播放中...",
        "status_done": "完成。",
        "status_error": "发生错误。",
        "btn_process": "处理并播放",
        "btn_processing": "处理中...",
        "btn_clear": "清理缓存",
        "msg_error_title": "错误",
        "msg_select_video": "请先选择视频文件。",
        "msg_success_title": "成功",
        "msg_process_complete": "处理完成！正在终端播放。",
        "msg_cache_cleared": "缓存已清理。",
        "msg_confirm_title": "确认",
        "msg_confirm_clear": "确定要清理缓存 (imgout 和 textout) 吗？",
        "msg_warning_title": "警告",
        "msg_high_res": "缩放后分辨率 ({}x{}) 过高 (>150x150)。\n播放可能无法正常进行。\n\n是否继续？",
        "msg_error_cache": "清理缓存失败: {}",
        "text_space": "空格",
        "levels_label": "层级数:",
    },
    "zh_tw": {
        "title": "Image2Ascii 播放器",
        "instruction": "選擇視訊檔案進行轉換和播放：",
        "browse": "瀏覽",
        "resolution": "解析度: -",
        "resolution_fmt": "解析度: {}x{} (影格數: {} -> {})",
        "resolution_unknown": "解析度: 未知",
        "ascii_label": "Ascii 字元 (暗 -> 亮):",
        "speed_label": "影格延遲 (秒):",
        "scale_label": "縮放比例:",
        "skip_label": "跳格數:",
        "scaled_res": "縮放後解析度: -",
        "scaled_res_fmt": "縮放後解析度: {}x{}",
        "status_ready": "就緒",
        "status_starting": "啟動中...",
        "status_extracting": "提取影格...",
        "status_generating": "生成 ASCII...",
        "status_playing": "播放中...",
        "status_done": "完成。",
        "status_error": "發生錯誤。",
        "btn_process": "處理並播放",
        "btn_processing": "處理中...",
        "btn_clear": "清理快取",
        "msg_error_title": "錯誤",
        "msg_select_video": "請先選擇視訊檔案。",
        "msg_success_title": "成功",
        "msg_process_complete": "處理完成！正在終端播放。",
        "msg_cache_cleared": "快取已清理。",
        "msg_confirm_title": "確認",
        "msg_confirm_clear": "確定要清理快取 (imgout 和 textout) 嗎？",
        "msg_warning_title": "警告",
        "msg_high_res": "縮放後解析度 ({}x{}) 過高 (>150x150)。\n播放可能無法正常進行。\n\n是否繼續？",
        "msg_error_cache": "清理快取失敗: {}",
        "text_space": "空格",
        "levels_label": "層級數:",
    },
}


def load_config():
    default_config = {"language": "zh_cn", "geometry": "700x800"}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # 与默认配置合并以确保所有键都存在
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception as e:
        print(f"Error loading config: {e}")
    return default_config


def save_config(key, value):
    try:
        config = load_config()
        config[key] = value
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")


app_config = load_config()
current_lang = app_config["language"]


def get_text(key):
    return str(translations[current_lang].get(key, key))


def extract_frames(video_path, output_folder, progress_callback=None):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    vidcap = cv2.VideoCapture(video_path)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    success, image = vidcap.read()
    count = 0
    while success:
        if progress_callback and total_frames > 0:
            progress_callback(count, total_frames)

        # 保存为 outputX.jpg 以匹配 img2ascii 的预期
        cv2.imwrite(os.path.join(output_folder, f"output{count}.jpg"), image)
        success, image = vidcap.read()
        count += 1
    return count


def process_video():
    global last_processed_video, last_processed_scale, last_processed_ascii
    video_path = file_path_var.get()
    if not video_path:
        messagebox.showerror(get_text("msg_error_title"), get_text("msg_select_video"))
        return

    # 检查分辨率警告
    try:
        scale = int(entry_scale.get())
        if scale <= 0:
            scale = 6
    except ValueError:
        scale = 6

    # 获取 ASCII 字符
    def parse_char(c):
        if c in ["Space", "空格", ""]:
            return " "
        return c[0] if len(c) > 0 else " "

    current_ascii = [parse_char(entry.get()) for entry in ascii_entries]

    if video_width > 0 and video_height > 0:
        scaled_w = int(video_width / scale)
        scaled_h = int(video_height / scale)
        if scaled_w > 150 or scaled_h > 150:
            if not messagebox.askyesno(
                get_text("msg_warning_title"),
                get_text("msg_high_res").format(scaled_w, scaled_h),
            ):
                return

    # 检查是否可以跳过处理
    skip_processing = False
    if (
        video_path == last_processed_video
        and scale == last_processed_scale
        and current_ascii == last_processed_ascii
        and os.path.exists("./textout/")
        and os.path.exists("./imgout/")
    ):
        skip_processing = True
    else:
        last_processed_video = video_path
        last_processed_scale = scale
        last_processed_ascii = current_ascii

    btn_process.config(state=tk.DISABLED, text=get_text("btn_processing"))
    progress_bar["value"] = 0
    lbl_status.config(text=get_text("status_starting"))

    def update_progress(current, total, stage_start, stage_weight):
        if total > 0:
            percent = (current / total) * stage_weight + stage_start
            progress_bar["value"] = percent
            # root.update_idletasks() # 在线程中不安全，使用变量或让主循环通过 widget config 处理（在简单情况下大多是线程安全的）

    def run():
        try:
            if not skip_processing:
                # 1. 提取帧 (0% -> 40%)
                lbl_status.config(text=get_text("status_extracting"))
                extract_frames(
                    video_path, "./imgout/", lambda c, t: update_progress(c, t, 0, 40)
                )

                # 2. 清理 textout
                if os.path.exists("./textout/"):
                    shutil.rmtree("./textout/")
                os.makedirs("./textout/")

                # 更新 Ascii 列表
                img2ascii.Ascii = current_ascii

                # 3. 生成 ASCII (40% -> 95%)
                lbl_status.config(text=get_text("status_generating"))
                img2ascii.genPics(
                    lambda c, t: update_progress(c, t, 40, 55),
                    scale=scale,
                    ascii_chars=current_ascii,
                )

            # 4. 播放
            lbl_status.config(text=get_text("status_playing"))
            progress_bar["value"] = 100

            # 获取延迟
            delay = "0.02"
            try:
                delay = str(float(entry_speed.get()))
            except ValueError:
                pass

            # 获取跳帧
            skip = "0"
            try:
                skip = str(int(entry_skip.get()))
            except ValueError:
                pass

            # 在新终端窗口中启动
            if getattr(sys, "frozen", False):
                # Use player.exe which has console=True
                base_dir = os.path.dirname(sys.executable)
                player_exe = os.path.join(base_dir, "player.exe")
                if not os.path.exists(player_exe):
                    # Fallback to self if player.exe not found (though it might not show output)
                    player_exe = sys.executable

                cmd_str = f'"{player_exe}" --play {delay} {skip}'
            else:
                cmd_str = f"python img2ascii.py {delay} {skip}"

            if platform.system() == "Windows":
                os.system(f"start cmd /k {cmd_str}")
            elif platform.system() == "Darwin":  # macOS
                script = f'''tell application "Terminal" to do script "python3 {os.getcwd()}/img2ascii.py {delay} {skip}"'''
                subprocess.run(["osascript", "-e", script])
            else:  # Linux
                # Try common terminals
                try:
                    subprocess.Popen(
                        [
                            "x-terminal-emulator",
                            "-e",
                            f"python3 img2ascii.py {delay} {skip}",
                        ]
                    )
                except FileNotFoundError:
                    try:
                        subprocess.Popen(
                            [
                                "gnome-terminal",
                                "--",
                                "python3",
                                "img2ascii.py",
                                str(delay),
                                str(skip),
                            ]
                        )
                    except FileNotFoundError:
                        try:
                            subprocess.Popen(
                                ["xterm", "-e", f"python3 img2ascii.py {delay} {skip}"]
                            )
                        except:
                            print("Could not find a suitable terminal emulator.")

            messagebox.showinfo(
                get_text("msg_success_title"), get_text("msg_process_complete")
            )
            lbl_status.config(text=get_text("status_done"))
        except Exception as e:
            messagebox.showerror(get_text("msg_error_title"), str(e))
            lbl_status.config(text=get_text("status_error"))
        finally:
            btn_process.config(state=tk.NORMAL, text=get_text("btn_process"))

    threading.Thread(target=run).start()


video_width = 0
video_height = 0
video_frames = 0
last_processed_video = None
last_processed_scale = None
last_processed_ascii = None


def update_scaled_res(*args):
    # 更新缩放后的分辨率
    try:
        scale = int(scale_var.get())
        if scale > 0 and video_width > 0 and video_height > 0:
            new_w = int(video_width / scale)
            new_h = int(video_height / scale)
            lbl_scaled_resolution.config(
                text=get_text("scaled_res_fmt").format(new_w, new_h)
            )
        else:
            lbl_scaled_resolution.config(text=get_text("scaled_res"))
    except ValueError:
        lbl_scaled_resolution.config(text=get_text("scaled_res"))

    # 更新帧数
    try:
        skip = int(skip_var.get())
    except ValueError:
        skip = 0

    if video_width > 0 and video_height > 0:
        converted_frames = video_frames
        if skip > 0:
            converted_frames = math.ceil(video_frames / (skip + 1))

        lbl_resolution.config(
            text=get_text("resolution_fmt").format(
                video_width, video_height, video_frames, converted_frames
            )
        )
    else:
        lbl_resolution.config(text=get_text("resolution"))


def clear_cache():
    if messagebox.askyesno(
        get_text("msg_confirm_title"), get_text("msg_confirm_clear")
    ):
        try:
            if os.path.exists("./imgout/"):
                shutil.rmtree("./imgout/")
                os.makedirs("./imgout/")
            if os.path.exists("./textout/"):
                shutil.rmtree("./textout/")
                os.makedirs("./textout/")
            messagebox.showinfo(
                get_text("msg_success_title"), get_text("msg_cache_cleared")
            )
        except Exception as e:
            messagebox.showerror(
                get_text("msg_error_title"), get_text("msg_error_cache").format(e)
            )


def select_file():
    global video_width, video_height, video_frames
    filename = filedialog.askopenfilename(
        title="Select Video", filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
    )
    if filename:
        file_path_var.set(filename)
        try:
            cap = cv2.VideoCapture(filename)
            if cap.isOpened():
                video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                # lbl_resolution 更新由 update_scaled_res 处理
                update_scaled_res()
            cap.release()
        except Exception as e:
            print(f"Error reading video info: {e}")
            lbl_resolution.config(text=get_text("resolution_unknown"))


def change_language(selection):
    global current_lang
    if selection == "简体中文 (UTF-8)":
        current_lang = "zh_cn"
    elif selection == "繁體中文 (UTF-8)":
        current_lang = "zh_tw"
    else:
        current_lang = "en"
    save_config("language", current_lang)
    update_ui_text()


def update_ui_text():
    root.title(get_text("title"))
    lbl_instruction.config(text=get_text("instruction"))
    btn_browse.config(text=get_text("browse"))

    if not (video_width > 0 and video_height > 0):
        lbl_resolution.config(text=get_text("resolution"))

    lbl_ascii.config(text=get_text("ascii_label"))
    lbl_levels.config(text=get_text("levels_label"))
    lbl_speed.config(text=get_text("speed_label"))
    lbl_scale.config(text=get_text("scale_label"))
    lbl_skip.config(text=get_text("skip_label"))

    update_scaled_res()

    lbl_status.config(text=get_text("status_ready"))
    btn_process.config(text=get_text("btn_process"))
    btn_clear.config(text=get_text("btn_clear"))

    # 如果包含本地化的空格文本，则更新 ASCII 输入框
    for entry in ascii_entries:
        val = entry.get()
        if val in ["Space", "空格"]:
            entry.delete(0, tk.END)
            entry.insert(0, get_text("text_space"))


root = ttk.Window(themename="cosmo")
root.title("Image2Ascii Player")
root.geometry(app_config["geometry"])


def on_closing():
    save_config("geometry", root.geometry())
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

# 主容器
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 顶部栏 (语言)
top_frame = ttk.Frame(main_frame)
top_frame.pack(fill=tk.X, pady=(0, 10))

lang_map = {"zh_cn": "简体中文 (UTF-8)", "zh_tw": "繁體中文 (UTF-8)", "en": "English"}
default_lang_text = lang_map.get(current_lang, "简体中文 (UTF-8)")
lang_var = tk.StringVar(value=default_lang_text)
lang_options = ["简体中文 (UTF-8)", "繁體中文 (UTF-8)", "English"]

opt_lang = ttk.Combobox(
    top_frame, textvariable=lang_var, values=lang_options, state="readonly", width=20
)
opt_lang.pack(side=tk.RIGHT)
opt_lang.bind("<<ComboboxSelected>>", lambda e: change_language(lang_var.get()))

# 文件选择区域
file_frame = ttk.Labelframe(main_frame, text="Video Source", padding=10)
file_frame.pack(fill=tk.X, pady=5)

lbl_instruction = ttk.Label(file_frame, text=get_text("instruction"))
lbl_instruction.pack(anchor=tk.W, pady=(0, 5))

input_frame = ttk.Frame(file_frame)
input_frame.pack(fill=tk.X)

file_path_var = tk.StringVar()
entry_path = ttk.Entry(input_frame, textvariable=file_path_var)
entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

btn_browse = ttk.Button(
    input_frame, text=get_text("browse"), command=select_file, bootstyle="primary"
)
btn_browse.pack(side=tk.LEFT)

lbl_resolution = ttk.Label(file_frame, text=get_text("resolution"), bootstyle="info")
lbl_resolution.pack(anchor=tk.W, pady=(5, 0))

# ASCII 字符设置区域
ascii_frame = ttk.Labelframe(main_frame, text="ASCII Configuration", padding=10)
ascii_frame.pack(fill=tk.X, pady=10)

lbl_ascii = ttk.Label(ascii_frame, text=get_text("ascii_label"))
lbl_ascii.pack(anchor=tk.W)

ascii_inputs_frame = ttk.Frame(ascii_frame)
ascii_inputs_frame.pack(fill=tk.X, pady=5)


def validate_ascii_input(P):
    if P == "":
        return True
    if P in ["Space", "空格"]:
        return True
    # 允许输入/删除 "Space" 或 "空格"
    if "Space".startswith(P) and len(P) > 1:
        return True
    if "空格".startswith(P):
        return True

    if len(P) > 1:
        return False
    return P.isascii()


vcmd = (root.register(validate_ascii_input), "%P")


def on_ascii_focus_out(event):
    widget = event.widget
    text = widget.get()
    if text == " ":
        widget.delete(0, tk.END)
        widget.insert(0, get_text("text_space"))


# Levels control
levels_frame = ttk.Frame(ascii_frame)
levels_frame.pack(fill=tk.X, pady=5)
lbl_levels = ttk.Label(levels_frame, text=get_text("levels_label"))
lbl_levels.pack(side=tk.LEFT)
var_levels = tk.IntVar(value=3)

ascii_entries = []


def update_ascii_entries(n):
    # Clear existing
    for widget in ascii_inputs_frame.winfo_children():
        widget.destroy()
    ascii_entries.clear()

    # Default chars to cycle through
    defaults = [
        " ",
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
        "0",
        "1",
        "2",
        "3",
    ]

    for i in range(n):
        entry = ttk.Entry(
            ascii_inputs_frame, width=5, validate="key", validatecommand=vcmd
        )
        entry.pack(side=tk.LEFT, padx=2)

        # Set default value
        val = defaults[i % len(defaults)]
        if val == " ":
            val = get_text("text_space")

        entry.insert(0, val)
        entry.bind("<FocusOut>", on_ascii_focus_out)
        ascii_entries.append(entry)


def on_levels_change(*args):
    try:
        n = var_levels.get()
        if n < 2:
            n = 2
        if n > 20:
            n = 20
        update_ascii_entries(n)
    except:
        pass


spin_levels = ttk.Spinbox(
    levels_frame,
    from_=2,
    to=20,
    textvariable=var_levels,
    width=5,
    command=on_levels_change,
)
spin_levels.pack(side=tk.LEFT, padx=5)
spin_levels.bind("<Return>", lambda e: on_levels_change())
spin_levels.bind("<FocusOut>", lambda e: on_levels_change())

# Initialize
update_ascii_entries(3)


# 播放设置区域
settings_frame = ttk.Labelframe(main_frame, text="Playback Settings", padding=10)
settings_frame.pack(fill=tk.X, pady=5)

# 设置区域的网格布局
settings_frame.columnconfigure(1, weight=1)
settings_frame.columnconfigure(3, weight=1)
settings_frame.columnconfigure(5, weight=1)

# 播放速度
lbl_speed = ttk.Label(settings_frame, text=get_text("speed_label"))
lbl_speed.grid(row=0, column=0, padx=5, sticky=tk.W)
entry_speed = ttk.Entry(settings_frame, width=10)
entry_speed.insert(0, "0.02")
entry_speed.grid(row=0, column=1, padx=5, sticky=tk.W)

# 缩放比例
lbl_scale = ttk.Label(settings_frame, text=get_text("scale_label"))
lbl_scale.grid(row=0, column=2, padx=5, sticky=tk.W)
scale_var = tk.StringVar(value="6")
scale_var.trace("w", update_scaled_res)
entry_scale = ttk.Entry(settings_frame, textvariable=scale_var, width=10)
entry_scale.grid(row=0, column=3, padx=5, sticky=tk.W)

# 跳帧设置
lbl_skip = ttk.Label(settings_frame, text=get_text("skip_label"))
lbl_skip.grid(row=0, column=4, padx=5, sticky=tk.W)
skip_var = tk.StringVar(value="0")
skip_var.trace("w", update_scaled_res)
entry_skip = ttk.Entry(settings_frame, textvariable=skip_var, width=10)
entry_skip.grid(row=0, column=5, padx=5, sticky=tk.W)

lbl_scaled_resolution = ttk.Label(
    settings_frame, text=get_text("scaled_res"), bootstyle="secondary"
)
lbl_scaled_resolution.grid(row=1, column=0, columnspan=6, pady=(10, 0), sticky=tk.W)

# 状态和进度条
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill=tk.X, pady=10)

lbl_status = ttk.Label(
    status_frame, text=get_text("status_ready"), bootstyle="inverse-primary", padding=5
)
lbl_status.pack(fill=tk.X)

progress_bar = ttk.Progressbar(
    main_frame, orient="horizontal", mode="determinate", bootstyle="success-striped"
)
progress_bar.pack(fill=tk.X, pady=5)

# 操作按钮
action_frame = ttk.Frame(main_frame)
action_frame.pack(pady=10)

btn_process = ttk.Button(
    action_frame,
    text=get_text("btn_process"),
    command=process_video,
    bootstyle="success",
    width=20,
)
btn_process.pack(side=tk.LEFT, padx=10)

btn_clear = ttk.Button(
    action_frame,
    text=get_text("btn_clear"),
    command=clear_cache,
    bootstyle="danger-outline",
    width=15,
)
btn_clear.pack(side=tk.LEFT, padx=10)

# 初始化界面文本
update_ui_text()

root.mainloop()
