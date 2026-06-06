import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from yt_dlp import YoutubeDL
import os
import threading
from datetime import datetime
import csv
import sys

class ModernYouTubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Studio Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Set style
        self.setup_styles()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.scraper_tab = ttk.Frame(self.notebook)
        self.downloader_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.scraper_tab, text="📹 Channel Scraper")
        self.notebook.add(self.downloader_tab, text="⬇️ Bulk Downloader")
        
        # Initialize both tabs
        self.init_scraper_tab()
        self.init_downloader_tab()
        
        # Variables
        self.scraped_videos = []
        
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
                  background=[('active', '#2980b9'), ('pressed', '#1c6388')],
                  foreground=[('active', 'white')])
        
        # Frame styles
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)
        
    # ==================== SCRAPER TAB ====================
    def init_scraper_tab(self):
        # Main container
        main_container = ttk.Frame(self.scraper_tab, padding="20")
        main_container.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_container, text="YouTube Channel Scraper", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Description
        desc = ttk.Label(main_container, text="Extract all videos from any YouTube channel or playlist", 
                        font=('Segoe UI', 10), foreground='#7f8c8d')
        desc.pack(pady=(0, 20))
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_container, text="Channel Information", padding="15")
        input_frame.pack(fill='x', pady=(0, 15))
        
        # URL Input
        ttk.Label(input_frame, text="YouTube URL:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.url_entry = ttk.Entry(input_frame, width=70, font=('Segoe UI', 10))
        self.url_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10))
        
        # Examples
        examples_frame = ttk.Frame(input_frame)
        examples_frame.grid(row=1, column=1, sticky='w', pady=(5, 0))
        
        ttk.Label(examples_frame, text="Examples:", font=('Segoe UI', 9), foreground='#7f8c8d').pack(side='left', padx=(0, 5))
        
        for example in ["Channel (@channelname)", "Playlist", "Video URL"]:
            btn = ttk.Button(examples_frame, text=example, command=lambda e=example: self.set_example(e))
            btn.pack(side='left', padx=2)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_container, text="Options", padding="15")
        options_frame.pack(fill='x', pady=(0, 15))
        
        # Include shorts
        self.include_shorts = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include YouTube Shorts", variable=self.include_shorts).pack(anchor='w')
        
        # Max videos
        max_videos_frame = ttk.Frame(options_frame)
        max_videos_frame.pack(anchor='w', pady=(5, 0))
        ttk.Label(max_videos_frame, text="Max videos to extract (0 for all):").pack(side='left', padx=(0, 10))
        self.max_videos = ttk.Spinbox(max_videos_frame, from_=0, to=10000, width=10)
        self.max_videos.set(0)
        self.max_videos.pack(side='left')
        
        # Action Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(0, 15))
        
        self.scrape_btn = ttk.Button(button_frame, text="🔍 Extract Videos", command=self.scrape_videos, 
                                     style='Primary.TButton', width=20)
        self.scrape_btn.pack(side='left', padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="💾 Save to CSV", command=self.save_to_csv, 
                                   state='disabled', width=20)
        self.save_btn.pack(side='left', padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Clear All", command=self.clear_scraper, width=20)
        self.clear_btn.pack(side='left', padx=5)
        
        # Progress
        self.scraper_progress = ttk.Progressbar(main_container, mode='indeterminate')
        self.scraper_progress.pack(fill='x', pady=(0, 10))
        
        # Status
        self.scraper_status = ttk.Label(main_container, text="Ready", style='Status.TLabel', foreground='#7f8c8d')
        self.scraper_status.pack(pady=(0, 10))
        
        # Results Tree
        results_frame = ttk.LabelFrame(main_container, text="Extracted Videos", padding="10")
        results_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('#', 'Title', 'URL')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        self.results_tree.heading('#', text='#')
        self.results_tree.heading('Title', text='Video Title')
        self.results_tree.heading('URL', text='YouTube URL')
        
        self.results_tree.column('#', width=50)
        self.results_tree.column('Title', width=500)
        self.results_tree.column('URL', width=350)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def set_example(self, example_type):
        if "Channel" in example_type:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, "https://www.youtube.com/@YouTube")
        elif "Playlist" in example_type:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")
        else:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
    def scrape_videos(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if 'youtube.com' not in url and 'youtu.be' not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
            
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        self.scrape_btn.config(state='disabled')
        self.scraper_progress.start()
        self.scraper_status.config(text="Extracting videos...", foreground='#3498db')
        
        # Start scraping in thread
        thread = threading.Thread(target=self._scrape_videos_thread, args=(url,))
        thread.daemon = True
        thread.start()
        
    def _scrape_videos_thread(self, url):
        try:
            videos = self.extract_videos_from_url(url)
            self.scraped_videos = videos
            
            # Update UI in main thread
            self.root.after(0, self._update_scraper_results)
            
        except Exception as e:
            self.root.after(0, self._scraper_error, str(e))
            
    def extract_videos_from_url(self, url):
        """Extract videos from URL with advanced options"""
        videos = []
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'socket_timeout': 30,
            'retries': 3,
            'ignoreerrors': True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                self.root.after(0, lambda: self.scraper_status.config(text="Fetching video information..."))
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    total = len(info['entries'])
                    for idx, entry in enumerate(info['entries']):
                        if entry and entry.get('id'):
                            title = entry.get('title', 'Unknown Title')
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            videos.append((title, video_url))
                            
                            # Update progress
                            if total > 0:
                                percent = (idx + 1) / total * 100
                                self.root.after(0, lambda p=percent: self.scraper_status.config(
                                    text=f"Extracting: {idx+1}/{total} videos ({p:.1f}%)"))
                                
                            # Check max videos
                            max_vids = int(self.max_videos.get())
                            if max_vids > 0 and len(videos) >= max_vids:
                                break
                else:
                    title = info.get('title', 'Unknown Title')
                    video_url = url
                    videos.append((title, video_url))
                    
            return videos
            
        except Exception as e:
            raise Exception(f"Failed to extract videos: {str(e)}")
            
    def _update_scraper_results(self):
        self.scraper_progress.stop()
        self.scrape_btn.config(state='normal')
        
        if self.scraped_videos:
            for idx, (title, url) in enumerate(self.scraped_videos, 1):
                self.results_tree.insert('', 'end', values=(idx, title, url))
                
            self.scraper_status.config(text=f"✅ Extracted {len(self.scraped_videos)} videos!", 
                                      foreground='#27ae60')
            self.save_btn.config(state='normal')
        else:
            self.scraper_status.config(text="❌ No videos found", foreground='#e74c3c')
            
    def _scraper_error(self, error_msg):
        self.scraper_progress.stop()
        self.scrape_btn.config(state='normal')
        self.scraper_status.config(text=f"❌ Error: {error_msg}", foreground='#e74c3c')
        messagebox.showerror("Extraction Error", error_msg)
        
    def save_to_csv(self):
        if not self.scraped_videos:
            messagebox.showwarning("No Data", "No videos to save. Please extract videos first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"youtube_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Title', 'Video Link'])
                    writer.writeheader()
                    for title, url in self.scraped_videos:
                        writer.writerow({'Title': title, 'Video Link': url})
                        
                messagebox.showinfo("Success", f"✅ Saved {len(self.scraped_videos)} videos to:\n{file_path}")
                self.scraper_status.config(text=f"Saved to: {os.path.basename(file_path)}", foreground='#27ae60')
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")
                
    def clear_scraper(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.scraped_videos = []
        self.url_entry.delete(0, tk.END)
        self.scraper_status.config(text="Ready", foreground='#7f8c8d')
        self.save_btn.config(state='disabled')
        
    # ==================== DOWNLOADER TAB ====================
    def init_downloader_tab(self):
        # Main container
        main_container = ttk.Frame(self.downloader_tab, padding="20")
        main_container.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_container, text="Bulk Video Downloader", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # CSV Selection Frame
        csv_frame = ttk.LabelFrame(main_container, text="CSV File", padding="15")
        csv_frame.pack(fill='x', pady=(0, 15))
        
        csv_inner = ttk.Frame(csv_frame)
        csv_inner.pack(fill='x')
        
        self.csv_path_var = tk.StringVar()
        ttk.Entry(csv_inner, textvariable=self.csv_path_var, state='readonly', font=('Segoe UI', 10)).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(csv_inner, text="📂 Browse", command=self.browse_csv, width=15).pack(side='left')
        
        # Output Directory Frame
        output_frame = ttk.LabelFrame(main_container, text="Output Directory", padding="15")
        output_frame.pack(fill='x', pady=(0, 15))
        
        output_inner = ttk.Frame(output_frame)
        output_inner.pack(fill='x')
        
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_inner, textvariable=self.output_path_var, state='readonly', font=('Segoe UI', 10)).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(output_inner, text="📁 Browse", command=self.browse_output_dir, width=15).pack(side='left')
        
        # Download Options
        options_frame = ttk.LabelFrame(main_container, text="Download Options", padding="15")
        options_frame.pack(fill='x', pady=(0, 15))
        
        # Quality selection
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(quality_frame, text="Video Quality:").pack(side='left', padx=(0, 10))
        self.quality_var = tk.StringVar(value="720p")
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                      values=["1080p", "720p", "480p", "360p", "Best Available"], 
                                      state='readonly', width=20)
        quality_combo.pack(side='left')
        
        # Format selection
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(anchor='w')
        
        ttk.Label(format_frame, text="Format:").pack(side='left', padx=(0, 10))
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                     values=["mp4", "mkv", "webm"], 
                                     state='readonly', width=20)
        format_combo.pack(side='left')
        
        # Action Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(0, 15))
        
        self.load_btn = ttk.Button(button_frame, text="📋 Load Videos", command=self.load_videos, 
                                   state='disabled', width=20)
        self.load_btn.pack(side='left', padx=5)
        
        self.download_btn = ttk.Button(button_frame, text="⬇️ Start Download", command=self.start_download, 
                                       state='disabled', style='Primary.TButton', width=20)
        self.download_btn.pack(side='left', padx=5)
        
        self.clear_downloader_btn = ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_downloader, width=20)
        self.clear_downloader_btn.pack(side='left', padx=5)
        
        # Progress
        self.download_progress_var = tk.DoubleVar()
        self.download_progress = ttk.Progressbar(main_container, variable=self.download_progress_var, maximum=100)
        self.download_progress.pack(fill='x', pady=(0, 10))
        
        # Status
        self.download_status = ttk.Label(main_container, text="Ready", style='Status.TLabel', foreground='#7f8c8d')
        self.download_status.pack(pady=(0, 10))
        
        # Videos List
        videos_frame = ttk.LabelFrame(main_container, text="Videos to Download", padding="10")
        videos_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('Title', 'URL', 'Status')
        self.download_tree = ttk.Treeview(videos_frame, columns=columns, show='headings', height=12)
        
        self.download_tree.heading('Title', text='Video Title')
        self.download_tree.heading('URL', text='YouTube URL')
        self.download_tree.heading('Status', text='Status')
        
        self.download_tree.column('Title', width=450)
        self.download_tree.column('URL', width=350)
        self.download_tree.column('Status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(videos_frame, orient='vertical', command=self.download_tree.yview)
        self.download_tree.configure(yscrollcommand=scrollbar.set)
        
        self.download_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Video data storage
        self.download_videos = []
        self.downloading = False
        
    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_path_var.set(file_path)
            self.load_btn.config(state='normal')
            
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path_var.set(directory)
            self.update_download_button_state()
            
    def load_videos(self):
        if not self.csv_path_var.get():
            messagebox.showerror("Error", "Please select a CSV file first!")
            return
            
        try:
            df = pd.read_csv(self.csv_path_var.get())
            
            if 'Title' not in df.columns or 'Video Link' not in df.columns:
                messagebox.showerror("Error", "CSV must contain 'Title' and 'Video Link' columns!")
                return
                
            # Clear existing items
            for item in self.download_tree.get_children():
                self.download_tree.delete(item)
                
            self.download_videos = []
            valid_videos = 0
            
            for _, row in df.iterrows():
                title = str(row['Title']).strip()
                link = str(row['Video Link']).strip()
                if link and link != 'nan' and 'youtube.com' in link:
                    self.download_videos.append({
                        'title': title,
                        'link': link,
                        'status': 'Pending'
                    })
                    self.download_tree.insert('', 'end', values=(title, link, 'Pending'))
                    valid_videos += 1
                    
            if valid_videos == 0:
                messagebox.showwarning("Warning", "No valid YouTube links found in CSV!")
                return
                
            self.download_status.config(text=f"✅ Loaded {valid_videos} videos", foreground='#27ae60')
            self.update_download_button_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def update_download_button_state(self):
        if self.output_path_var.get() and self.download_videos and not self.downloading:
            self.download_btn.config(state='normal')
        else:
            self.download_btn.config(state='disabled')
            
    def start_download(self):
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please select output directory!")
            return
            
        if not self.download_videos:
            messagebox.showerror("Error", "No videos to download!")
            return
            
        self.downloading = True
        self.download_btn.config(state='disabled')
        self.load_btn.config(state='disabled')
        self.download_progress_var.set(0)
        
        thread = threading.Thread(target=self.download_videos_thread)
        thread.daemon = True
        thread.start()
        
    def download_videos_thread(self):
        total = len(self.download_videos)
        
        # Get quality setting
        quality_map = {
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "Best Available": "bestvideo+bestaudio/best"
        }
        
        ydl_opts = {
            'outtmpl': os.path.join(self.output_path_var.get(), '%(title)s.%(ext)s'),
            'format': quality_map.get(self.quality_var.get(), "bestvideo[height<=720]+bestaudio/best[height<=720]"),
            'merge_output_format': self.format_var.get(),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.download_progress_hook],
        }
        
        for idx, video in enumerate(self.download_videos):
            try:
                self.root.after(0, self.update_video_status, idx, "⬇️ Downloading...")
                
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['link']])
                    
                self.root.after(0, self.update_video_status, idx, "✅ Completed")
                self.root.after(0, self.update_download_progress, ((idx + 1) / total) * 100)
                self.root.after(0, self.update_download_status, 
                              f"Downloaded {idx + 1}/{total}: {video['title'][:50]}")
                
            except Exception as e:
                self.root.after(0, self.update_video_status, idx, f"❌ Failed")
                self.root.after(0, self.update_download_status, f"Failed: {video['title'][:50]}")
                
        self.root.after(0, self.download_complete)
        
    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.root.after(0, self.update_download_progress, percent)
                
    def update_video_status(self, index, status):
        item = self.download_tree.get_children()[index]
        values = list(self.download_tree.item(item, 'values'))
        values[2] = status
        self.download_tree.item(item, values=values)
        
        if "✅" in status:
            self.download_tree.tag_configure('completed', foreground='#27ae60')
            self.download_tree.item(item, tags=('completed',))
        elif "❌" in status:
            self.download_tree.tag_configure('failed', foreground='#e74c3c')
            self.download_tree.item(item, tags=('failed',))
            
    def update_download_progress(self, value):
        self.download_progress_var.set(value)
        
    def update_download_status(self, message):
        self.download_status.config(text=message, foreground='#3498db')
        
    def download_complete(self):
        self.downloading = False
        self.download_btn.config(state='disabled')
        self.load_btn.config(state='normal')
        self.download_status.config(text="✅ All downloads completed!", foreground='#27ae60')
        messagebox.showinfo("Success", "All videos have been downloaded successfully!")
        
    def clear_downloader(self):
        for item in self.download_tree.get_children():
            self.download_tree.delete(item)
        self.download_videos = []
        self.csv_path_var.set("")
        self.output_path_var.set("")
        self.download_status.config(text="Ready", foreground='#7f8c8d')
        self.download_progress_var.set(0)
        self.load_btn.config(state='disabled')
        self.download_btn.config(state='disabled')

def main():
    root = tk.Tk()
    app = ModernYouTubeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()