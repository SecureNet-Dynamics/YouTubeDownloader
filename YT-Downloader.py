import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def check_and_install_dependencies():
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append('yt-dlp')
        
    try:
        import pandas
    except ImportError:
        missing.append('pandas')

    if missing:
        root = tk.Tk()
        root.withdraw()
        deps_str = ", ".join(missing)
        msg = f"The following required packages are missing: {deps_str}\n\nWould you like to install them automatically?"
        if messagebox.askyesno("Missing Dependencies", msg):
            install_win = tk.Toplevel(root)
            install_win.title("Installing Dependencies")
            install_win.geometry("400x150")
            
            tk.Label(install_win, text=f"Installing: {deps_str}\n\nPlease wait, this may take a minute...", font=("Segoe UI", 10)).pack(expand=True)
            install_win.update()
            
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                install_win.destroy()
                messagebox.showinfo("Success", "Dependencies installed successfully!\n\nThe application will now start.")
                root.destroy()
            except Exception as e:
                install_win.destroy()
                messagebox.showerror("Error", f"Failed to install dependencies:\n{str(e)}\n\nPlease install manually using pip.")
                sys.exit(1)
        else:
            sys.exit(1)

check_and_install_dependencies()

import pandas as pd
from yt_dlp import YoutubeDL
import os
import threading
from datetime import datetime
import csv
from functools import partial
import re

class YTDLogger:
    def __init__(self, app, index):
        self.app = app
        self.index = index
        
    def debug(self, msg):
        if "has already been downloaded" in msg:
            self.app.root.after(0, self.app.mark_video_skipped, self.index)
            
    def info(self, msg):
        pass
        
    def warning(self, msg):
        pass
        
    def error(self, msg):
        pass

class ModernYouTubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Studio Pro")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Set style
        self.setup_styles()
        
        # Variables
        self.scraped_videos = [] # List of dicts: {'title': title, 'link': url, 'progress': '0%', 'status': status}
        self.downloading = False
        self.output_path_var = tk.StringVar()
        self.download_progress_var = tk.DoubleVar()
        self.include_shorts = tk.BooleanVar(value=True)
        self.max_videos_var = tk.IntVar(value=0)
        
        # Build UI
        self.init_main_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#2c3e50')
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Status.TLabel', font=('Segoe UI', 10))
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        
        # Button styles
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        style.map('Primary.TButton',
                  background=[('active', '#2980b9'), ('pressed', '#1c6388'), ('disabled', '#bdc3c7')],
                  foreground=[('active', 'white'), ('disabled', '#7f8c8d')])
        
    def init_main_ui(self):
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_container, text="YouTube Studio Pro Downloader", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # 1. Fetch Videos Section
        input_frame = ttk.LabelFrame(main_container, text="1. Fetch Videos", padding="15")
        input_frame.pack(fill='x', pady=(0, 15))
        
        url_frame = ttk.Frame(input_frame)
        url_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(url_frame, text="YouTube URL:", font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, font=('Segoe UI', 10))
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.scrape_btn = ttk.Button(url_frame, text="🔍 Fetch Videos", command=self.scrape_videos, style='Primary.TButton')
        self.scrape_btn.pack(side='left')
        
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill='x')
        ttk.Checkbutton(options_frame, text="Include Shorts", variable=self.include_shorts).pack(side='left', padx=(0, 20))
        ttk.Label(options_frame, text="Max videos (0=all):").pack(side='left', padx=(0, 5))
        ttk.Spinbox(options_frame, from_=0, to=10000, width=8, textvariable=self.max_videos_var).pack(side='left')
        
        ttk.Label(options_frame, text="Browser Cookies:").pack(side='left', padx=(20, 5))
        self.browser_var = tk.StringVar(value="None")
        ttk.Combobox(options_frame, textvariable=self.browser_var, values=["None", "chrome", "firefox", "edge", "brave", "safari", "opera", "vivaldi"], state='readonly', width=8).pack(side='left')
        
        # Example links
        examples_frame = ttk.Frame(options_frame)
        examples_frame.pack(side='left', padx=(20, 0))
        ttk.Label(examples_frame, text="Examples:", font=('Segoe UI', 9), foreground='#7f8c8d').pack(side='left', padx=(0, 5))
        for example in ["Channel", "Playlist", "Video"]:
            btn = ttk.Button(examples_frame, text=example, command=lambda e=example: self.set_example(e))
            btn.pack(side='left', padx=2)
            
        # 2. Download Settings Section
        dl_opts_frame = ttk.LabelFrame(main_container, text="2. Download Settings", padding="15")
        dl_opts_frame.pack(fill='x', pady=(0, 15))
        
        dir_frame = ttk.Frame(dl_opts_frame)
        dir_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(dir_frame, text="Save to:", font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        ttk.Entry(dir_frame, textvariable=self.output_path_var, state='readonly', font=('Segoe UI', 10)).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(dir_frame, text="📁 Browse", command=self.browse_output_dir).pack(side='left')
        
        q_frame = ttk.Frame(dl_opts_frame)
        q_frame.pack(fill='x')
        ttk.Label(q_frame, text="Quality:").pack(side='left', padx=(0, 5))
        self.quality_var = tk.StringVar(value="720p")
        ttk.Combobox(q_frame, textvariable=self.quality_var, values=["1080p", "720p", "480p", "360p", "Best Available"], state='readonly', width=15).pack(side='left', padx=(0, 20))
        
        ttk.Label(q_frame, text="Format:").pack(side='left', padx=(0, 5))
        self.format_var = tk.StringVar(value="mp4")
        ttk.Combobox(q_frame, textvariable=self.format_var, values=["mp4", "mkv", "webm"], state='readonly', width=10).pack(side='left')

        # 3. Actions Section
        action_frame = ttk.Frame(main_container)
        action_frame.pack(pady=(0, 15))
        
        self.download_btn = ttk.Button(action_frame, text="⬇️ Download All", command=self.start_download, state='disabled', style='Primary.TButton', width=20)
        self.download_btn.pack(side='left', padx=5)
        
        self.export_btn = ttk.Button(action_frame, text="💾 Export to CSV", command=self.save_to_csv, state='disabled', width=15)
        self.export_btn.pack(side='left', padx=5)
        
        self.clear_btn = ttk.Button(action_frame, text="🗑️ Clear List", command=self.clear_all, width=15)
        self.clear_btn.pack(side='left', padx=5)
        
        # Progress & Status
        self.progress_bar = ttk.Progressbar(main_container, mode='determinate', variable=self.download_progress_var, maximum=100)
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        self.status_label = ttk.Label(main_container, text="Ready", style='Status.TLabel', foreground='#7f8c8d')
        self.status_label.pack(pady=(0, 10))
        
        # Results Treeview
        results_frame = ttk.LabelFrame(main_container, text="3. Video List", padding="10")
        results_frame.pack(fill='both', expand=True)
        
        columns = ('Title', 'URL', 'Progress', 'Status')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        self.tree.heading('Title', text='Video Title')
        self.tree.heading('URL', text='YouTube URL')
        self.tree.heading('Progress', text='Progress')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('Title', width=400)
        self.tree.column('URL', width=250)
        self.tree.column('Progress', width=80, anchor='center')
        self.tree.column('Status', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def get_cookie_opts(self):
        browser = self.browser_var.get()
        if browser != "None":
            return {'cookiesfrombrowser': (browser,)}
        return {}

    def set_example(self, example_type):
        self.url_entry.delete(0, tk.END)
        if example_type == "Channel":
            self.url_entry.insert(0, "https://www.youtube.com/@YouTube")
        elif example_type == "Playlist":
            self.url_entry.insert(0, "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")
        else:
            self.url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path_var.set(directory)
            self.update_download_button_state()
            
    def update_download_button_state(self):
        if self.output_path_var.get() and self.scraped_videos and not self.downloading:
            self.download_btn.config(state='normal')
        else:
            self.download_btn.config(state='disabled')
            
    def scrape_videos(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if 'youtube.com' not in url and 'youtu.be' not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
            
        self.clear_list_only()
        self.scrape_btn.config(state='disabled')
        self.download_btn.config(state='disabled')
        self.export_btn.config(state='disabled')
        
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        self.update_status("Fetching video information...", '#3498db')
        
        thread = threading.Thread(target=self._scrape_videos_thread, args=(url,))
        thread.daemon = True
        thread.start()
        
    def _scrape_videos_thread(self, url):
        try:
            self.extract_videos_from_url(url)
            self.root.after(0, self._finalize_scraper_results)
        except Exception as e:
            self.root.after(0, self._scraper_error, str(e))
            
    def add_video_to_ui(self, title, video_url):
        video_data = {'title': title, 'link': video_url, 'progress': '0%', 'status': 'Pending'}
        self.scraped_videos.append(video_data)
        self.tree.insert('', 'end', values=(title, video_url, '0%', 'Pending'))
        self.update_download_button_state()
        
    def extract_videos_from_url(self, url):
        # Detect if it's a channel/playlist URL
        is_channel = any(x in url for x in ['/@', '/c/', '/channel/', '/user/', '/playlist', '/results'])
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist' if is_channel else False,
            'socket_timeout': 60,  # Increased timeout for Windows with security software
            'retries': 5,
            'ignoreerrors': True,
            'extractor_args': {'youtube': ['player_client=android,web']},
        }
        # Only add JS runtime if Node.js is available (optional fallback for Windows)
        import shutil
        if shutil.which('node'):
            ydl_opts['js_runtimes'] = {'node': {}}
        
        ydl_opts.update(self.get_cookie_opts())
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info and 'entries' in info:
                    entries = list(info['entries'])
                    total = len(entries)
                    
                    for idx, entry in enumerate(entries):
                        if not entry:
                            continue
                        
                        # Handle string entries (from extract_flat for channels)
                        if isinstance(entry, str):
                            # It's a video ID, construct URL
                            video_id = entry
                            title = f'Video {video_id}'
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                        else:
                            # Handle dict entries with missing titles/deleted videos
                            title = entry.get('title')
                            if not title or title in ['[Deleted video]', '[Private video]']:
                                continue
                            
                            video_id = entry.get('id') or entry.get('url')
                            if video_id:
                                video_url = f"https://www.youtube.com/watch?v={video_id}" if len(str(video_id)) == 11 else video_id
                            else:
                                video_url = entry.get('url', 'Unknown URL')
                        
                        # Add to UI directly
                        self.root.after(0, self.add_video_to_ui, title, video_url)
                        
                        if total > 0:
                            percent = (idx + 1) / total * 100
                            self.root.after(0, lambda p=percent, i=idx+1, t=total: self.update_status(f"Extracting: {i}/{t} videos ({p:.1f}%)", '#3498db'))
                        
                        max_vids = self.max_videos_var.get()
                        if max_vids > 0 and len(self.scraped_videos) >= max_vids:
                            break
                            
                elif info:
                    title = info.get('title', 'Unknown Title')
                    video_url = url
                    self.root.after(0, self.add_video_to_ui, title, video_url)
                else:
                    raise Exception("Could not extract video information. The URL may be invalid, private, or requires authentication.")
                    
        except Exception as e:
            raise Exception(f"Failed to extract videos: {str(e)}")
            
    def _finalize_scraper_results(self):
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.download_progress_var.set(0)
        self.scrape_btn.config(state='normal')
        
        if self.scraped_videos:
            self.update_status(f"✅ Extracted {len(self.scraped_videos)} videos!", '#27ae60')
            self.export_btn.config(state='normal')
            self.update_download_button_state()
        else:
            self.update_status("❌ No videos found", '#e74c3c')
            
    def _scraper_error(self, error_msg):
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.download_progress_var.set(0)
        self.scrape_btn.config(state='normal')
        self.update_status(f"❌ Error: {error_msg}", '#e74c3c')
        self.update_download_button_state()
        messagebox.showerror("Extraction Error", error_msg)
        
    def start_download(self):
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please select output directory!")
            return
            
        if not self.scraped_videos:
            messagebox.showerror("Error", "No videos to download!")
            return
            
        self.downloading = True
        self.download_btn.config(state='disabled')
        self.scrape_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        self.download_progress_var.set(0)
        
        thread = threading.Thread(target=self.download_videos_thread)
        thread.daemon = True
        thread.start()
        
    def download_videos_thread(self):
        total = len(self.scraped_videos)
        
        quality_map = {
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "Best Available": "bestvideo+bestaudio/best"
        }
        
        for idx, video in enumerate(self.scraped_videos):
            if video['status'] in ['✅ Completed', '⏭️ Skipped']:
                continue
                
            self.root.after(0, self.update_video_row, idx, "0%", "⬇️ Downloading...")
            self.root.after(0, self.update_status, f"Downloading {idx + 1}/{total}: {video['title'][:50]}", '#3498db')
            
            # Setup options specifically for this video to inject the hook with index
            hook = partial(self.download_progress_hook, index=idx)
            logger = YTDLogger(self, idx)
            
            # Convert path to forward slashes for Windows compatibility with yt-dlp
            output_path = self.output_path_var.get().replace('\\', '/')
            output_template = f"{output_path}/%(title)s.%(ext)s"
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': quality_map.get(self.quality_var.get(), "bestvideo[height<=720]+bestaudio/best[height<=720]"),
                'merge_output_format': self.format_var.get(),
                'quiet': False, # Allow logger to catch messages
                'no_warnings': True,
                'nooverwrites': True, # Important for skipping
                'progress_hooks': [hook],
                'logger': logger,
                'socket_timeout': 60,
                'retries': 3,
                'extractor_args': {'youtube': ['player_client=android,web']},
            }
            # Only add JS runtime if Node.js is available
            import shutil
            if shutil.which('node'):
                ydl_opts['js_runtimes'] = {'node': {}}
            ydl_opts.update(self.get_cookie_opts())
            
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['link']])
                    
                # If it wasn't marked as skipped by the logger, mark it completed
                if self.scraped_videos[idx]['status'] != '⏭️ Skipped':
                    self.root.after(0, self.update_video_row, idx, "100%", "✅ Completed")
                    
            except Exception as e:
                print(f"Error downloading {video['link']}: {e}")
                self.root.after(0, self.update_video_row, idx, "Error", "❌ Failed")
                self.root.after(0, self.update_status, f"Failed: {video['title'][:50]}", '#e74c3c')
                
            self.root.after(0, self.download_progress_var.set, ((idx + 1) / total) * 100)
                
        self.root.after(0, self.download_complete)
        
    def download_progress_hook(self, d, index):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip()
            # Strip ANSI escape codes if present
            percent_str = self.strip_ansi(percent_str)
            self.root.after(0, self.update_video_progress, index, percent_str)
        elif d['status'] == 'finished':
            self.root.after(0, self.update_video_progress, index, '100%')
            
    def strip_ansi(self, text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def mark_video_skipped(self, index):
        self.update_video_row(index, "100%", "⏭️ Skipped")

    def update_video_progress(self, index, progress):
        self.scraped_videos[index]['progress'] = progress
        self.update_tree_item(index)
        
    def update_video_row(self, index, progress, status):
        self.scraped_videos[index]['progress'] = progress
        self.scraped_videos[index]['status'] = status
        self.update_tree_item(index)
        
    def update_tree_item(self, index):
        items = self.tree.get_children()
        if index < len(items):
            item = items[index]
            video = self.scraped_videos[index]
            self.tree.item(item, values=(video['title'], video['link'], video['progress'], video['status']))
            
            if "✅" in video['status']:
                self.tree.tag_configure('completed', foreground='#27ae60')
                self.tree.item(item, tags=('completed',))
            elif "⏭️" in video['status']:
                self.tree.tag_configure('skipped', foreground='#f39c12')
                self.tree.item(item, tags=('skipped',))
            elif "❌" in video['status']:
                self.tree.tag_configure('failed', foreground='#e74c3c')
                self.tree.item(item, tags=('failed',))
                
    def update_status(self, message, color):
        self.status_label.config(text=message, foreground=color)
        
    def download_complete(self):
        self.downloading = False
        self.scrape_btn.config(state='normal')
        self.clear_btn.config(state='normal')
        self.update_download_button_state()
        
        if not self.scraped_videos:
            return
            
        all_done = all(v['status'] in ['✅ Completed', '⏭️ Skipped'] for v in self.scraped_videos)
        if all_done:
            self.update_status("✅ All downloads completed successfully!", '#27ae60')
            messagebox.showinfo("Success", "All videos have been processed successfully!")
        else:
            self.update_status("⚠️ Downloads finished with some errors.", '#e67e22')
            messagebox.showwarning("Warning", "Downloads finished, but some videos failed.")
            
    def clear_list_only(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.scraped_videos = []
        self.export_btn.config(state='disabled')
        self.update_download_button_state()
        
    def clear_all(self):
        self.clear_list_only()
        self.url_entry.delete(0, tk.END)
        self.update_status("Ready", '#7f8c8d')
        self.download_progress_var.set(0)
        
    def save_to_csv(self):
        if not self.scraped_videos:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"youtube_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Title', 'Video Link', 'Progress', 'Status'])
                    writer.writeheader()
                    for video in self.scraped_videos:
                        writer.writerow({
                            'Title': video['title'], 
                            'Video Link': video['link'], 
                            'Progress': video['progress'],
                            'Status': video['status']
                        })
                self.update_status(f"Saved to: {os.path.basename(file_path)}", '#27ae60')
                messagebox.showinfo("Success", f"✅ Exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")

def main():
    root = tk.Tk()
    app = ModernYouTubeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()