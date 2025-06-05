import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos de YouTube")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Puedes usar: 'clam', 'alt', 'default', 'classic'
        
        # Variables
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar()
        self.save_path_var.set(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para descargar")
        self.format_var = tk.StringVar()
        self.format_var.set("mp4")  # Formato por defecto
        
        # Crear widgets
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL del video
        ttk.Label(main_frame, text="URL del video:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        url_entry.focus()
        
        # Ruta para guardar
        ttk.Label(main_frame, text="Guardar en:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        path_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, width=40)
        path_entry.pack(side=tk.LEFT)
        
        browse_btn = ttk.Button(path_frame, text="Explorar", command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Formato
        ttk.Label(main_frame, text="Formato:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(format_frame, text="MP4 (Video)", variable=self.format_var, value="mp4").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="MP3 (Audio)", variable=self.format_var, value="mp3").pack(side=tk.LEFT)
        
        # Barra de progreso
        ttk.Label(main_frame, text="Progreso:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=400, mode="determinate")
        progress_bar.grid(row=3, column=1, sticky=tk.W, pady=(10, 5))
        
        # Estado
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 20))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2)
        
        download_btn = ttk.Button(btn_frame, text="Descargar", command=self.start_download, width=15)
        download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(btn_frame, text="Limpiar", command=self.clear_fields, width=15)
        clear_btn.pack(side=tk.LEFT)
    
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if directory:
            self.save_path_var.set(directory)
    
    def clear_fields(self):
        self.url_var.set("")
        self.progress_var.set(0)
        self.status_var.set("Listo para descargar")
    
    def check_yt_dlp(self):
        """Verifica si yt-dlp está instalado, y si no, intenta instalarlo."""
        try:
            # Intentar ejecutar yt-dlp --version para ver si está instalado
            subprocess.run(["yt-dlp", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            # yt-dlp no está instalado o no se puede ejecutar
            try:
                self.status_var.set("Instalando yt-dlp...")
                self.root.update_idletasks()
                
                # Instalar yt-dlp usando pip
                subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.status_var.set("yt-dlp instalado correctamente")
                return True
            except subprocess.SubprocessError as e:
                messagebox.showerror("Error de Instalación", 
                                    f"No se pudo instalar yt-dlp. Por favor, instálalo manualmente con 'pip install yt-dlp'.\nError: {str(e)}")
                return False
    
    def download_video(self):
        try:
            url = self.url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Por favor, ingresa una URL de YouTube.")
                return
            
            save_path = self.save_path_var.get()
            format_type = self.format_var.get()
            
            # Verificar que yt-dlp está instalado
            if not self.check_yt_dlp():
                return
            
            self.status_var.set("Iniciando descarga...")
            self.root.update_idletasks()
            
            # Construir el comando de yt-dlp dependiendo del formato seleccionado
            if format_type == "mp4":
                # Para video MP4
                output_template = os.path.join(save_path, "%(title)s.%(ext)s")
                cmd = [
                    "yt-dlp", url,
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "-o", output_template,
                    "--no-warnings"
                ]
            else:
                # Para audio MP3
                output_template = os.path.join(save_path, "%(title)s.%(ext)s")
                cmd = [
                    "yt-dlp", url,
                    "-x", "--audio-format", "mp3",
                    "-o", output_template,
                    "--no-warnings"
                ]
            
            # Ejecutar el comando
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Leer la salida línea por línea y actualizar la interfaz
            downloaded_file = None
            for line in process.stdout:
                # Actualizar el estado con la línea actual
                self.status_var.set(line.strip())
                self.root.update_idletasks()
                
                # Intentar extraer el progreso si la línea contiene información de porcentaje
                if "[download]" in line and "%" in line:
                    try:
                        percent_text = line.split("%")[0].split()[-1]
                        percent = float(percent_text)
                        self.progress_var.set(percent)
                    except (ValueError, IndexError):
                        pass
                
                # Capturar el nombre del archivo descargado
                if "Destination:" in line:
                    downloaded_file = line.split("Destination:", 1)[1].strip()
            
            # Esperar a que termine el proceso
            process.wait()
            
            # Verificar si hubo algún error
            if process.returncode != 0:
                error_output = process.stderr.read()
                raise Exception(f"Error en yt-dlp: {error_output}")
            
            # Mensaje de éxito
            self.status_var.set("Descarga completada")
            self.progress_var.set(100)
            
            if downloaded_file:
                messagebox.showinfo("Descarga Completada", f"El archivo se ha guardado como:\n{downloaded_file}")
            else:
                messagebox.showinfo("Descarga Completada", "El archivo se ha descargado correctamente.")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Ocurrio un error durante la descarga:\n{str(e)}")
        
        finally:
            self.progress_var.set(0)
    
    def start_download(self):
        # Ejecutar la descarga en un hilo separado para no bloquear la interfaz
        threading.Thread(target=self.download_video, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()