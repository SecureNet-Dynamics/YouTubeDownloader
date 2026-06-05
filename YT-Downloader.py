import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from yt_dlp import YoutubeDL
import os
import threading
from pathlib import Path

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.csv_file_path = None
        self.output_dir = None
        self.videos_data = []
        self.downloading = False
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="YouTube Video Downloader", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # CSV File Selection
        csv_frame = ttk.LabelFrame(main_frame, text="1. Select CSV File", padding="10")
        csv_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        csv_frame.columnconfigure(1, weight=1)
        
        self.csv_path_var = tk.StringVar()
        ttk.Entry(csv_frame, textvariable=self.csv_path_var, state='readonly').grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(csv_frame, text="Browse CSV", command=self.browse_csv).grid(row=0, column=1)
        
        # Output Directory Selection
        output_frame = ttk.LabelFrame(main_frame, text="2. Select Output Directory", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path_var, state='readonly').grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse Directory", command=self.browse_output_dir).grid(row=0, column=1)
        
        # Videos List Frame
        list_frame = ttk.LabelFrame(main_frame, text="3. Videos to Download", padding="10")
        list_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for videos
        columns = ('Title', 'Link', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.tree.heading('Title', text='Video Title')
        self.tree.heading('Link', text='YouTube Link')
        self.tree.heading('Status', text='Status')
        
        # Define column widths
        self.tree.column('Title', width=400)
        self.tree.column('Link', width=250)
        self.tree.column('Status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load CSV Button
        self.load_btn = ttk.Button(main_frame, text="Load Videos from CSV", 
                                   command=self.load_csv, state='disabled')
        self.load_btn.grid(row=4, column=0, pady=(0, 10))
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="gray")
        self.status_label.grid(row=6, column=0, pady=(0, 10))
        
        # Download Button
        self.download_btn = ttk.Button(main_frame, text="Start Download", 
                                       command=self.start_download, state='disabled')
        self.download_btn.grid(row=7, column=0)
        
    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_file_path = file_path
            self.csv_path_var.set(file_path)
            self.load_btn.config(state='normal')
            
    def browse_output_dir(self):
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if directory:
            self.output_dir = directory
            self.output_path_var.set(directory)
            self.update_download_button_state()
            
    def load_csv(self):
        if not self.csv_file_path:
            messagebox.showerror("Error", "Please select a CSV file first!")
            return
            
        try:
            # Read CSV file
            df = pd.read_csv(self.csv_file_path)
            
            # Check required columns
            if 'Title' not in df.columns or 'Video Link' not in df.columns:
                messagebox.showerror("Error", 
                                   "CSV must contain 'Title' and 'Video Link' columns!")
                return
                
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Store videos data
            self.videos_data = []
            for _, row in df.iterrows():
                title = str(row['Title']).strip()
                link = str(row['Video Link']).strip()
                if link and link != 'nan':  # Check if link exists
                    self.videos_data.append({
                        'title': title,
                        'link': link,
                        'status': 'Pending'
                    })
                    self.tree.insert('', tk.END, values=(title, link, 'Pending'))
                    
            if not self.videos_data:
                messagebox.showwarning("Warning", "No valid video links found in CSV!")
                return
                
            self.status_label.config(text=f"Loaded {len(self.videos_data)} videos", 
                                    foreground="green")
            self.update_download_button_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def update_download_button_state(self):
        if self.output_dir and self.videos_data and not self.downloading:
            self.download_btn.config(state='normal')
        else:
            self.download_btn.config(state='disabled')
            
    def start_download(self):
        if not self.output_dir:
            messagebox.showerror("Error", "Please select output directory!")
            return
            
        if not self.videos_data:
            messagebox.showerror("Error", "No videos to download!")
            return
            
        # Start download in separate thread to keep UI responsive
        self.downloading = True
        self.download_btn.config(state='disabled')
        self.load_btn.config(state='disabled')
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.download_videos)
        thread.daemon = True
        thread.start()
        
    def download_videos(self):
        total_videos = len(self.videos_data)
        
        # yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }
        
        for idx, video in enumerate(self.videos_data):
            try:
                # Update status
                self.root.after(0, self.update_video_status, idx, "Downloading...")
                
                # Download video
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['link']])
                    
                # Update status to completed
                self.root.after(0, self.update_video_status, idx, "Completed")
                self.root.after(0, self.update_progress, ((idx + 1) / total_videos) * 100)
                self.root.after(0, self.update_status_label, 
                              f"Downloaded {idx + 1}/{total_videos}: {video['title']}")
                
            except Exception as e:
                # Update status to failed
                self.root.after(0, self.update_video_status, idx, f"Failed: {str(e)[:30]}")
                self.root.after(0, self.update_status_label, 
                              f"Failed: {video['title']}")
                
        # Download complete
        self.root.after(0, self.download_complete)
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                # Optionally update a more detailed progress
                
    def update_video_status(self, index, status):
        # Update treeview item status
        item = self.tree.get_children()[index]
        values = list(self.tree.item(item, 'values'))
        values[2] = status
        self.tree.item(item, values=values)
        
        # Change color based on status
        if status == "Completed":
            self.tree.tag_configure('completed', foreground='green')
            self.tree.item(item, tags=('completed',))
        elif "Failed" in status:
            self.tree.tag_configure('failed', foreground='red')
            self.tree.item(item, tags=('failed',))
            
    def update_progress(self, value):
        self.progress_var.set(value)
        
    def update_status_label(self, message):
        self.status_label.config(text=message, foreground="blue")
        
    def download_complete(self):
        self.downloading = False
        self.download_btn.config(state='disabled')
        self.load_btn.config(state='normal')
        self.status_label.config(text="Download completed!", foreground="green")
        messagebox.showinfo("Success", "All videos have been downloaded successfully!")

def main():
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()