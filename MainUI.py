import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import APIget
from datetime import datetime
import json


class WeatherAlertMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("天气预警监测系统")
        self.root.geometry("800x600")

        # 监控状态
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 150  # 固定150秒

        # 创建界面
        self.setup_ui()

        # 默认坐标 (41.19, 122.07)
        self.lat_var.set("41.19")
        self.lon_var.set("122.07")

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="天气预警监测系统",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)

        # 输入框架
        input_frame = ttk.LabelFrame(main_frame, text="位置设置", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(1, weight=1)

        # 纬度
        ttk.Label(input_frame, text="纬度:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.lat_var = tk.StringVar()
        lat_entry = ttk.Entry(input_frame, textvariable=self.lat_var, width=15)
        lat_entry.grid(row=0, column=1, sticky=tk.W, padx=5)

        # 经度
        ttk.Label(input_frame, text="经度:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.lon_var = tk.StringVar()
        lon_entry = ttk.Entry(input_frame, textvariable=self.lon_var, width=15)
        lon_entry.grid(row=0, column=3, sticky=tk.W, padx=5)

        # 间隔显示（只读）
        ttk.Label(input_frame, text="监测间隔:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        interval_label = ttk.Label(input_frame, text="150 秒 (固定)", foreground="blue")
        interval_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # 提示信息
        info_label = ttk.Label(input_frame, text="※ 为了减少API使用，监测间隔固定为150秒，无法修改", foreground="gray")
        info_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, pady=10)

        self.start_button = ttk.Button(control_frame, text="开始监测",
                                       command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(control_frame, text="停止监测",
                                      command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.clear_button = ttk.Button(control_frame, text="清空显示",
                                       command=self.clear_display)
        self.clear_button.grid(row=0, column=2, padx=5)

        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                 relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="监测结果", padding="5")
        result_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # 使用滚动文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD,
                                                     width=70, height=20)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置文本标签样式
        self.result_text.tag_config("title", font=("Arial", 10, "bold"), foreground="blue")
        self.result_text.tag_config("alert", foreground="red")
        self.result_text.tag_config("info", foreground="green")
        self.result_text.tag_config("time", foreground="gray")

    def log_message(self, message, tag=None):
        """在结果显示区域添加消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"[{timestamp}] ", "time")
        self.result_text.insert(tk.END, f"{message}\n", tag)
        self.result_text.see(tk.END)  # 自动滚动到底部
        self.root.update_idletasks()

    def clear_display(self):
        """清空显示区域"""
        self.result_text.delete(1.0, tk.END)
        self.log_message("显示已清空", "info")

    def start_monitoring(self):
        """开始监测"""
        try:
            # 验证输入
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())

            # 检查经纬度范围
            if not (-90 <= lat <= 90):
                messagebox.showerror("输入错误", "纬度必须在 -90 到 90 之间")
                return
            if not (-180 <= lon <= 180):
                messagebox.showerror("输入错误", "经度必须在 -180 到 180 之间")
                return

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的经纬度")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("监测运行中...")
        self.log_message(f"开始监测 - 位置: ({lat}, {lon}), 监测间隔: 150秒", "info")

    def stop_monitoring(self):
        """停止监测"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("监测已停止")
        self.log_message("监测已停止", "info")

    def monitor_loop(self):
        """监测循环"""
        while self.monitoring:
            try:
                lat = float(self.lat_var.get())
                lon = float(self.lon_var.get())

                # 更新状态显示（需要在主线程中更新）
                self.root.after(0, lambda: self.status_var.set(f"正在获取数据..."))

                # 获取天气预警信息
                result = APIget.get_my_qweather_alert(lat, lon)


                with open('ALERT.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)

                # 在主线程中处理结果
                self.root.after(0, self.process_result, result)

                # 等待150秒
                for remaining in range(self.update_interval, 0, -1):
                    if not self.monitoring:
                        break
                    # 每30秒更新一次倒计时显示，减少UI更新频率
                    if remaining % 30 == 0 or remaining <= 10:
                        minutes = remaining // 60
                        seconds = remaining % 60
                        countdown_msg = f"下次监测: {minutes}分{seconds}秒后"
                        self.root.after(0, lambda msg=countdown_msg: self.status_var.set(msg))
                    time.sleep(1)

            except Exception as e:
                self.root.after(0, self.log_message, f"监测出错: {str(e)}", "alert")
                # 出错后等待5秒再重试
                for _ in range(5):
                    if not self.monitoring:
                        break
                    time.sleep(1)

    def process_result(self, result):
        """处理API返回的结果"""
        if not result:
            self.log_message("未获取到数据", "alert")
            return

        metadata = result.get("metadata", {})

        if metadata.get("zeroResult"):
            self.log_message("当前地点没有天气预警。", "info")
            attributions = metadata.get('attributions', [])
            if attributions:
                self.log_message(f"数据声明: {attributions}", "info")
        else:
            alerts = result.get("alerts", [])
            alert_count = len(alerts)
            self.log_message(f"共找到 {alert_count} 条预警：", "title")

            for i, alert in enumerate(alerts, 1):
                title = alert.get("headline", "无标题")
                desc = alert.get("description", "无描述")

                self.log_message(f"\n--- 预警 {i}/{alert_count} ---", "title")
                self.log_message(f"标题: {title}", "alert")
                self.log_message(f"详情: {desc}", "")
                self.log_message("-" * 50, "")

        # 更新状态
        self.status_var.set("监测运行中")

    def on_closing(self):
        """关闭窗口时的处理"""
        if self.monitoring:
            if messagebox.askokcancel("退出", "监测正在运行中，确定要退出吗？"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = WeatherAlertMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()