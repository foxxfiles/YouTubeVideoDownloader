import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys
import tempfile
import shutil
import time
import queue

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos de YouTube")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Colores del tema oscuro
        self.bg_color = "#2A2A2E"
        self.fg_color = "#E4E4E7"
        self.accent_blue = "#4A9BFF"
        self.accent_orange = "#FF8C38"
        self.accent_green = "#4CD964"
        self.accent_red = "#FF5157"
        self.accent_violet = "#B57EDC"
        self.input_bg = "#36363A"
        self.border_color = "#4D4D50"
        
        # Inicializar el estilo
        self.style = ttk.Style()
        self.setup_theme()
        
        # Variables de control
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar()
        self.save_path_var.set(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Listo para descargar")
        self.format_var = tk.StringVar(value="mp4")
        self.custom_format_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="normal")
        self.available_formats = []
        self.format_map = {}
        
        self.current_process = None
        self.download_active = False
        self.post_process = False
        
        # Configurar fondo
        self.root.configure(background=self.bg_color)
        
        # Crear la interfaz
        self.create_widgets()
    
    def setup_theme(self):
        """Configura el tema oscuro en ttk."""
        self.style.theme_use("clam")
        self.style.configure(".",
                             background=self.bg_color,
                             foreground=self.fg_color,
                             borderwidth=1,
                             bordercolor=self.border_color,
                             darkcolor=self.bg_color,
                             lightcolor=self.bg_color,
                             troughcolor=self.input_bg,
                             focuscolor=self.accent_blue,
                             font=('Segoe UI', 10))
        
        self.style.configure("TButton",
                             padding=(10, 5),
                             background=self.input_bg,
                             foreground=self.fg_color,
                             borderwidth=0)
        self.style.map("TButton",
                       background=[('active', self.border_color),
                                   ('pressed', self.border_color)],
                       foreground=[('active', self.fg_color)])
        
        self.style.configure("Download.TButton",
                             background=self.accent_orange,
                             foreground="#FFFFFF")
        self.style.map("Download.TButton",
                       background=[('active', "#FF9F5F"),
                                   ('pressed', "#E67D29")],
                       foreground=[('active', "#FFFFFF")])
        
        self.style.configure("Stop.TButton",
                             background=self.accent_red,
                             foreground="#FFFFFF")
        self.style.map("Stop.TButton",
                       background=[('active', "#FF6A70"),
                                   ('pressed', "#E6484E")],
                       foreground=[('active', "#FFFFFF")])
        
        self.style.configure("Format.TButton",
                             background=self.accent_blue,
                             foreground="#FFFFFF")
        self.style.map("Format.TButton",
                       background=[('active', "#6BABFF"),
                                   ('pressed', "#3A8AEE")],
                       foreground=[('active', "#FFFFFF")])
        
        self.style.configure("Clear.TButton",
                             background=self.accent_violet,
                             foreground="#FFFFFF")
        self.style.map("Clear.TButton",
                       background=[('active', "#C58FE6"),
                                   ('pressed', "#A46DCB")],
                       foreground=[('active', "#FFFFFF")])
        
        self.style.configure("TEntry",
                             fieldbackground=self.input_bg,
                             foreground=self.fg_color,
                             bordercolor=self.border_color,
                             lightcolor=self.border_color,
                             darkcolor=self.border_color)
        
        self.style.configure("TCombobox",
                             fieldbackground=self.input_bg,
                             background=self.input_bg,
                             foreground=self.fg_color,
                             selectbackground=self.accent_blue,
                             selectforeground="#FFFFFF",
                             arrowcolor=self.fg_color)
        self.style.map("TCombobox",
                       fieldbackground=[('readonly', self.input_bg)],
                       selectbackground=[('readonly', self.accent_blue)])
        
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TRadiobutton",
                             background=self.bg_color,
                             foreground=self.fg_color,
                             indicatorcolor=self.input_bg)
        self.style.map("TRadiobutton",
                       indicatorcolor=[('selected', self.accent_orange)])
        
        self.style.configure("TProgressbar",
                             background=self.accent_green,
                             troughcolor=self.input_bg,
                             bordercolor=self.border_color)
        
        self.style.configure("Title.TLabel",
                             font=('Segoe UI', 12, 'bold'),
                             foreground=self.accent_orange)
        
        self.style.configure("Status.TLabel",
                             font=('Segoe UI', 9),
                             foreground=self.accent_blue)

    def create_widgets(self):
        """Crea y organiza todos los widgets en la interfaz."""
        main_frame = ttk.Frame(self.root, padding="7 7 7 7")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Descargador de Videos de YouTube", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # URL
        ttk.Label(main_frame, text="URL del video:").grid(row=1, column=0, sticky=tk.W, pady=(0, 6))
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=38)
        url_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=(0, 6), padx=(5, 0))
        url_entry.focus()
        
        # Ruta de guardado
        ttk.Label(main_frame, text="Guardar en:").grid(row=2, column=0, sticky=tk.W, pady=(0, 6))
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=1, sticky=tk.W+tk.E, pady=(0, 6), padx=(5, 0))
        
        path_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, width=28)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(path_frame, text="Explorar", command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Formato (RadioButtons)
        ttk.Label(main_frame, text="Formato:").grid(row=3, column=0, sticky=tk.W, pady=(0, 6))
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=3, column=1, sticky=tk.W, pady=(0, 6), padx=(5, 0))
        
        ttk.Radiobutton(format_frame, text="MP4 (Video)", variable=self.format_var, value="mp4").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="MP3 (Audio)", variable=self.format_var, value="mp3").pack(side=tk.LEFT)
        
        # Formato personalizado
        ttk.Label(main_frame, text="Formato personalizado:").grid(row=4, column=0, sticky=tk.W, pady=(0, 6))
        format_input_frame = ttk.Frame(main_frame)
        format_input_frame.grid(row=4, column=1, sticky=tk.W+tk.E, pady=(0, 6), padx=(5, 0))
        
        self.format_combo = ttk.Combobox(format_input_frame, textvariable=self.custom_format_var, width=28)
        self.format_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        hint_label = ttk.Label(main_frame, text="(Ej: 'bestaudio[ext=m4a]' o '137+140')")
        hint_label.grid(row=5, column=1, sticky=tk.W, pady=(0, 6), padx=(5, 0))
        
        # Barra de progreso
        ttk.Label(main_frame, text="Progreso:").grid(row=6, column=0, sticky=tk.W, pady=(1, 1))
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=300, mode="determinate")
        progress_bar.grid(row=6, column=1, sticky=tk.W+tk.E, pady=(1, 1), padx=(5, 0))
        
        # Estado
        status_label = ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel")
        status_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(1, 8))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=2)
        
        self.download_btn = ttk.Button(btn_frame, text="Descargar", command=self.start_download, width=8, style="Download.TButton")
        self.download_btn.pack(side=tk.LEFT, padx=(0, 3))
        
        self.stop_btn = ttk.Button(btn_frame, text="Detener", command=self.stop_download, width=8, style="Stop.TButton", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 3))
        
        formats_btn = ttk.Button(btn_frame, text="Ver Formatos", command=self.show_available_formats, width=9, style="Format.TButton")
        formats_btn.pack(side=tk.LEFT, padx=(0, 3))
        
        clear_btn = ttk.Button(btn_frame, text="Limpiar", command=self.clear_fields, width=8, style="Clear.TButton")
        clear_btn.pack(side=tk.LEFT)
    
    def browse_directory(self):
        """Abre un cuadro de diálogo para seleccionar la carpeta de destino."""
        directory = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if directory:
            self.save_path_var.set(directory)
    
    def clear_fields(self):
        """Limpia los campos de entrada y la barra de progreso."""
        self.url_var.set("")
        self.progress_var.set(0)
        self.status_var.set("Listo para descargar")
        self.custom_format_var.set("")
    
    def on_format_selected(self, event):
        """Actualiza el campo de formato personalizado cuando se elige un valor en el ComboBox."""
        selected = self.format_combo.get()
        if selected in self.format_map:
            self.custom_format_var.set(self.format_map[selected])
    
    def show_available_formats(self):
        """Obtiene los formatos disponibles para la URL y los carga en el ComboBox."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor, ingrese una URL de YouTube.")
            return
        
        self.status_var.set("Obteniendo formatos disponibles...")
        self.root.update_idletasks()
        
        try:
            cmd = ["yt-dlp", "-F", url]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, error = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Error al obtener formatos: {error}")
            
            self.available_formats = []
            format_ids = []
            
            best_video_id = None
            best_video_desc = None
            best_audio_id = None
            integrated_formats = []
            
            lines = output.split('\n')
            for line in lines:
                if line.strip() and line[0].isdigit():
                    parts = line.split()
                    if len(parts) >= 2:
                        format_id = parts[0]
                        # Detección de formatos integrados (video+audio en un solo archivo)
                        if "video only" not in line and "audio only" not in line and len(parts) > 4:
                            resolution = next((p for p in parts if "x" in p), "")
                            if resolution:
                                desc = f"{format_id} - Video+Audio: {resolution}"
                                if "mp4" in line:
                                    desc += " (MP4)"
                                elif "webm" in line:
                                    desc += " (WEBM)"
                                integrated_formats.append((format_id, desc))
                        # Mejor video
                        if "1080" in line and "video only" in line:
                            if not best_video_id or int(format_id) > int(best_video_id):
                                best_video_id = format_id
                                best_video_desc = next((p for p in parts if "x" in p), "")
                        elif "720" in line and "video only" in line and not best_video_id:
                            if not best_video_id or int(format_id) > int(best_video_id):
                                best_video_id = format_id
                                best_video_desc = next((p for p in parts if "x" in p), "")
                        # Mejor audio (m4a)
                        if "audio only" in line and "m4a" in line:
                            if not best_audio_id or (best_audio_id and "m4a" not in best_audio_id):
                                best_audio_id = format_id
            
            # Añadir formatos integrados
            for fmt_id, fmt_desc in sorted(integrated_formats, key=lambda x: x[0], reverse=True):
                self.available_formats.append(f"{fmt_desc} (UN ARCHIVO)")
                format_ids.append(fmt_id)
            
            # Insertar la combinación de mejor video + mejor audio
            if best_video_id and best_audio_id:
                combo_desc = f"{best_video_id}+{best_audio_id} - Mejor Video ({best_video_desc}) + Mejor Audio (ALTA CALIDAD)"
                self.available_formats.insert(0, combo_desc)
                format_ids.insert(0, f"{best_video_id}+{best_audio_id}")
                                
            # Añadir otros formatos
            for line in lines:
                if line.strip() and line[0].isdigit():
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            format_id = parts[0]
                            if (format_id in format_ids 
                                or f"{format_id}+" in ''.join(format_ids) 
                                or f"+{format_id}" in ''.join(format_ids)):
                                continue
                            # Audio only
                            if "audio only" in line:
                                desc = f"{format_id} - Audio: {' '.join([p for p in parts if 'k' in p and 'Hz' not in p])}"
                                if "m4a" in line:
                                    desc += " (M4A)"
                                elif "webm" in line:
                                    desc += " (WEBM)"
                                elif "mp3" in line:
                                    desc += " (MP3)"
                                self.available_formats.append(desc)
                                format_ids.append(format_id)
                            # Video only
                            elif "video only" in line:
                                resolution = next((p for p in parts if "x" in p), "")
                                desc = f"{format_id} - Video: {resolution}"
                                if "mp4" in line:
                                    desc += " (MP4)"
                                elif "webm" in line:
                                    desc += " (WEBM)"
                                self.available_formats.append(desc)
                                format_ids.append(format_id)
                    except:
                        pass
            
            # Añadir predefinidos
            self.available_formats.append("bestaudio[ext=m4a] - Mejor audio M4A")
            format_ids.append("bestaudio[ext=m4a]")
            
            self.available_formats.append("bestaudio[ext=webm] - Mejor audio WEBM")
            format_ids.append("bestaudio[ext=webm]")
            
            self.available_formats.append("best - Mejor formato UN ARCHIVO")
            format_ids.append("best")
            
            self.format_combo['values'] = self.available_formats
            self.format_map = dict(zip(self.available_formats, format_ids))
            self.format_combo.bind("<<ComboboxSelected>>", self.on_format_selected)
            
            self.status_var.set("Formatos obtenidos y cargados")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"No se pudieron obtener los formatos: {str(e)}")
    
    def check_yt_dlp(self):
        """Verifica si yt-dlp está instalado; si no, intenta instalarlo."""
        try:
            subprocess.run(["yt-dlp", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            try:
                self.status_var.set("Instalando yt-dlp...")
                self.root.update_idletasks()
                subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.status_var.set("yt-dlp instalado correctamente")
                return True
            except subprocess.SubprocessError as e:
                messagebox.showerror("Error de Instalacion",
                                     f"No se pudo instalar yt-dlp. Instale manualmente con 'pip install yt-dlp'.\nError: {str(e)}")
                return False
    
    def download_audio_and_convert_to_mp3(self, url, save_path):
        """Descarga solo audio y lo copia a .mp3 sin usar ffmpeg."""
        try:
            cmd = ["yt-dlp", "--get-title", url]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            title, error = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Error al obtener el título: {error}")
            
            title = title.strip()
            title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
            output_file = os.path.join(save_path, f"{title}.mp3")
            
            self.status_var.set("Descargando audio...")
            self.progress_var.set(10)
            self.root.update_idletasks()
            
            temp_file = os.path.join(tempfile.gettempdir(), f"{title}.m4a")
            cmd = ["yt-dlp", "-f", "bestaudio[ext=m4a]", "-o", temp_file, url]
            
            self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            for line in self.current_process.stdout:
                if not self.download_active:
                    return
                self.status_var.set(line.strip())
                self.root.update_idletasks()
                if "[download]" in line and "%" in line:
                    try:
                        percent_text = line.split("%")[0].split()[-1]
                        percent = float(percent_text)
                        self.progress_var.set(percent * 0.8)
                    except (ValueError, IndexError):
                        pass
            
            self.current_process.wait()
            
            # Si no se pudo con m4a, intentamos con webm
            if self.current_process.returncode != 0 or not os.path.exists(temp_file):
                temp_file = os.path.join(tempfile.gettempdir(), f"{title}.webm")
                cmd = ["yt-dlp", "-f", "bestaudio[ext=webm]", "-o", temp_file, url]
                
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                
                for line in self.current_process.stdout:
                    if not self.download_active:
                        return
                    self.status_var.set(line.strip())
                    self.root.update_idletasks()
                    if "[download]" in line and "%" in line:
                        try:
                            percent_text = line.split("%")[0].split()[-1]
                            percent = float(percent_text)
                            self.progress_var.set(percent * 0.8)
                        except (ValueError, IndexError):
                            pass
                
                self.current_process.wait()
                if self.current_process.returncode != 0:
                    error_output = self.current_process.stderr.read()
                    raise Exception(f"Error al descargar el audio: {error_output}")
            
            if not os.path.exists(temp_file):
                raise Exception("No se pudo descargar el archivo de audio")
                
            self.status_var.set("Convirtiendo a MP3...")
            self.progress_var.set(90)
            self.root.update_idletasks()
            
            import shutil
            shutil.copy2(temp_file, output_file)
            
            try:
                os.remove(temp_file)
            except:
                pass
                
            return output_file
            
        except Exception as e:
            raise Exception(f"Error en la descarga y conversión: {str(e)}")
    
    def merge_video_audio(self, video_file, audio_file, output_file):
        """
        Combina video y audio con ffmpeg local, mostrando depuración en la consola
        en tiempo real (tanto stdout como stderr). Además, se incluye '-y' para
        forzar la sobreescritura y evitar bloqueos.
        """
        print("\n---- INICIO DEL PROCESO DE UNIÓN DE ARCHIVOS ----")
        print("DEBUG: Archivo de video: " + video_file)
        print("DEBUG: Archivo de audio: " + audio_file)
        print("DEBUG: Archivo de salida: " + output_file)
        try:
            import platform
            if platform.system() == "Windows":
                ffmpeg_path = os.path.join(".", "ffmpeg", "bin", "ffmpeg.exe")
            else:
                ffmpeg_path = os.path.join(".", "ffmpeg", "ffmpeg")
            
            print("DEBUG: Buscando ffmpeg en: " + ffmpeg_path)
            
            if not os.path.exists(ffmpeg_path):
                print("DEBUG: ffmpeg no encontrado en la ruta inicial.")
                if platform.system() == "Windows":
                    possible_paths = [
                        os.path.join(".", "ffmpeg", "ffmpeg.exe"),
                        os.path.join(".", "ffmpeg", "bin", "ffmpeg.exe")
                    ]
                else:
                    possible_paths = [
                        os.path.join(".", "ffmpeg", "ffmpeg"),
                        os.path.join(".", "ffmpeg", "bin", "ffmpeg")
                    ]
                for path in possible_paths:
                    print("DEBUG: Verificando ruta: " + path)
                    if os.path.exists(path):
                        ffmpeg_path = path
                        print("DEBUG: ffmpeg encontrado en: " + ffmpeg_path)
                        break
                else:
                    print("DEBUG: No se encontró ffmpeg en rutas comunes, buscando en subdirectorios...")
                    for root_dir, dirs, files in os.walk(os.path.join(".", "ffmpeg")):
                        for file in files:
                            if file.startswith("ffmpeg") and (file.endswith(".exe") or "." not in file):
                                ffmpeg_path = os.path.join(root_dir, file)
                                print("DEBUG: ffmpeg encontrado en subdirectorio: " + ffmpeg_path)
                                break
                        if os.path.exists(ffmpeg_path):
                            break
            
            if not os.path.exists(ffmpeg_path):
                print("ERROR: ffmpeg no se encontró en ninguna ubicación.")
                raise Exception("No se pudo encontrar el ejecutable de ffmpeg")
            
            print("DEBUG: Usando ffmpeg desde: " + ffmpeg_path)
            
            # Agregamos -y para forzar la sobreescritura sin que ffmpeg se quede esperando
            cmd = [
                ffmpeg_path,
                "-y",
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_file
            ]
            print("DEBUG: Comando ffmpeg: " + " ".join(cmd))
            
            # Para leer stdout y stderr en tiempo real, creamos hilos y colas
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            q = queue.Queue()
            
            def read_stream(stream, tag):
                for line in iter(stream.readline, ''):
                    q.put((tag, line))
                stream.close()
            
            # Hilos para leer stdout y stderr
            t_out = threading.Thread(target=read_stream, args=(process.stdout, "stdout"), daemon=True)
            t_err = threading.Thread(target=read_stream, args=(process.stderr, "stderr"), daemon=True)
            t_out.start()
            t_err.start()
            
            # Leemos de la cola hasta que el proceso termine y no haya más datos
            while True:
                if process.poll() is not None and q.empty():
                    break
                try:
                    tag, line = q.get(timeout=0.1)
                    line_str = line.strip()
                    if tag == "stdout":
                        print(f"DEBUG [FFmpeg stdout]: {line_str}")
                    else:
                        print(f"DEBUG [FFmpeg stderr]: {line_str}")
                except queue.Empty:
                    pass
            
            returncode = process.wait()
            print("DEBUG: Código de retorno de ffmpeg: " + str(returncode))
            
            if returncode != 0:
                print("ERROR: ffmpeg terminó con errores.")
                raise Exception("Error al combinar con ffmpeg.")
            
            if os.path.exists(output_file):
                output_size = os.path.getsize(output_file)
                print("DEBUG: Tamaño del archivo de salida: " + str(output_size) + " bytes")
                if output_size > 1000:
                    print("DEBUG: Unión de archivos completada exitosamente.")
                    return output_file
                else:
                    print("ERROR: El archivo combinado tiene un tamaño insuficiente: " + str(output_size) + " bytes")
                    raise Exception("El archivo combinado tiene un tamaño insuficiente.")
            else:
                print("ERROR: El archivo de salida no fue creado.")
                raise Exception("El archivo combinado no se creó correctamente.")
        
        except Exception as e:
            print("DEBUG: Excepción en la unión de archivos: " + str(e))
            self.status_var.set("Error al usar ffmpeg local: " + str(e))
            print("DEBUG: Intentando métodos alternativos...")
            self.status_var.set("Intentando métodos alternativos...")
            
            # Método 1: MoviePy
            try:
                print("DEBUG: Método alternativo 1: MoviePy")
                try:
                    import moviepy.editor as mp
                except ImportError:
                    print("DEBUG: MoviePy no está instalado. Instalando...")
                    self.status_var.set("Instalando MoviePy para combinar archivos...")
                    self.root.update_idletasks()
                    subprocess.run([sys.executable, "-m", "pip", "install", "moviepy"],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    import moviepy.editor as mp
                
                print("DEBUG: Cargando video con MoviePy: " + video_file)
                video_clip = mp.VideoFileClip(video_file)
                print("DEBUG: Cargando audio con MoviePy: " + audio_file)
                audio_clip = mp.AudioFileClip(audio_file)
                print("DEBUG: Combinando clips con MoviePy...")
                final_clip = video_clip.set_audio(audio_clip)
                print("DEBUG: Guardando resultado en: " + output_file)
                final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
                
                video_clip.close()
                audio_clip.close()
                final_clip.close()
                
                print("DEBUG: Unión con MoviePy completada exitosamente.")
                return output_file
            
            except Exception as e2:
                print("ERROR: Excepción en MoviePy: " + str(e2))
                self.status_var.set("Error con MoviePy: " + str(e2) + ". Intentando método alternativo...")
                self.root.update_idletasks()
            
            # Método 2: yt-dlp
            try:
                print("DEBUG: Método alternativo 2: yt-dlp")
                self.status_var.set("Intentando combinar con yt-dlp...")
                self.root.update_idletasks()
                
                cmd = ["yt-dlp", "--merge-output-format", "mp4", "-o", output_file, "--merge-files", video_file, audio_file]
                print("DEBUG: Comando yt-dlp: " + " ".join(cmd))
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                stdout, stderr = process.communicate()
                print("DEBUG [yt-dlp stdout]: " + stdout.strip())
                print("DEBUG [yt-dlp stderr]: " + stderr.strip())
                print("DEBUG: Código de retorno de yt-dlp: " + str(process.returncode))
                
                if os.path.exists(output_file):
                    output_size = os.path.getsize(output_file)
                    print("DEBUG: Tamaño del archivo combinado por yt-dlp: " + str(output_size) + " bytes")
                    if output_size > 0:
                        print("DEBUG: Unión con yt-dlp completada exitosamente.")
                        return output_file
                    else:
                        print("ERROR: El archivo combinado por yt-dlp tiene tamaño 0.")
                        raise Exception("El archivo de salida no se creó correctamente.")
                else:
                    print("ERROR: El archivo de salida con yt-dlp no fue creado.")
                    raise Exception("El archivo de salida no se creó correctamente.")
            
            except Exception as e3:
                print("ERROR: Excepción en yt-dlp: " + str(e3))
                self.status_var.set("Error con yt-dlp: " + str(e3) + ". Guardando archivos por separado...")
                self.root.update_idletasks()
            
            # Si todos los métodos fallan, guardamos los archivos separados
            print("DEBUG: Guardando archivos por separado.")
            video_filename = os.path.basename(video_file)
            audio_filename = os.path.basename(audio_file)
            video_dest = os.path.join(os.path.dirname(output_file), video_filename)
            audio_dest = os.path.join(os.path.dirname(output_file), audio_filename)
            
            print("DEBUG: Copiando video a: " + video_dest)
            if video_file != video_dest:
                shutil.copy2(video_file, video_dest)
            
            print("DEBUG: Copiando audio a: " + audio_dest)
            if audio_file != audio_dest:
                shutil.copy2(audio_file, audio_dest)
            
            print("DEBUG: Proceso de unión fallido. Archivos guardados por separado.")
            self.status_var.set("No se pudo combinar. Archivos guardados por separado.")
            messagebox.showinfo("Archivos Guardados",
                                f"No se pudieron combinar los archivos.\n\nSe han guardado por separado:\n- Video: {video_filename}\n- Audio: {audio_filename}")
            print("DEBUG: FIN DEL PROCESO DE UNIÓN DE ARCHIVOS")
            return video_dest
    
    def download_separate_and_merge(self, url, custom_format, save_path):
        """
        Descarga video y audio por separado cuando se detecta un '+' en el formato
        y luego llama a merge_video_audio para unirlos.
        """
        try:
            # Separar las dos partes: video_id + audio_id
            parts = custom_format.split("+", 1)
            if len(parts) < 2:
                raise Exception("Formato inválido para descarga separada. Debe contener '+' (ej: 137+140).")
            
            video_id = parts[0]
            audio_id = parts[1]
            
            # Obtener título para usarlo en nombres de archivo
            cmd_title = ["yt-dlp", "--get-title", url]
            process = subprocess.Popen(cmd_title, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            title, error = process.communicate()
            if process.returncode != 0:
                raise Exception(f"Error al obtener el título: {error}")
            
            title = title.strip()
            title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
            
            # Archivos temporales
            temp_dir = tempfile.gettempdir()
            video_temp = os.path.join(temp_dir, f"{title}_video.temp")
            audio_temp = os.path.join(temp_dir, f"{title}_audio.temp")
            
            # Descargar video
            self.status_var.set("Descargando video...")
            self.root.update_idletasks()
            
            cmd_video = ["yt-dlp", "-f", video_id, "-o", video_temp, url]
            self.current_process = subprocess.Popen(cmd_video, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
            
            for line in self.current_process.stdout:
                if not self.download_active:
                    return
                self.status_var.set(line.strip())
                self.root.update_idletasks()
                if "[download]" in line and "%" in line:
                    try:
                        percent_text = line.split("%")[0].split()[-1]
                        percent = float(percent_text)
                        self.progress_var.set(percent * 0.5)  # 50% para el video
                    except (ValueError, IndexError):
                        pass
            
            self.current_process.wait()
            if self.current_process.returncode != 0 and self.download_active:
                error_output = self.current_process.stderr.read()
                raise Exception(f"Error al descargar el video: {error_output}")
            
            # Descargar audio
            self.status_var.set("Descargando audio...")
            self.root.update_idletasks()
            
            cmd_audio = ["yt-dlp", "-f", audio_id, "-o", audio_temp, url]
            self.current_process = subprocess.Popen(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
            
            for line in self.current_process.stdout:
                if not self.download_active:
                    return
                self.status_var.set(line.strip())
                self.root.update_idletasks()
                if "[download]" in line and "%" in line:
                    try:
                        percent_text = line.split("%")[0].split()[-1]
                        percent = float(percent_text)
                        # Aquí sumamos otro 50% del total, para completar 100%
                        self.progress_var.set(50 + percent * 0.5)
                    except (ValueError, IndexError):
                        pass
            
            self.current_process.wait()
            if self.current_process.returncode != 0 and self.download_active:
                error_output = self.current_process.stderr.read()
                raise Exception(f"Error al descargar el audio: {error_output}")
            
            # Archivo final
            ext_final = ".mp4"  # Asumimos mp4 para la combinación
            final_output = os.path.join(save_path, f"{title}{ext_final}")
            
            # Llamar a merge_video_audio para unir
            self.status_var.set("Uniendo video y audio con ffmpeg...")
            self.progress_var.set(80)
            self.root.update_idletasks()
            
            merged_file = self.merge_video_audio(video_temp, audio_temp, final_output)
            
            if merged_file and os.path.exists(merged_file):
                self.status_var.set("Descarga completada")
                self.progress_var.set(100)
                messagebox.showinfo("Descarga Completada", f"El archivo se ha guardado como:\n{merged_file}")
            
            # Eliminar temporales
            if os.path.exists(video_temp):
                os.remove(video_temp)
            if os.path.exists(audio_temp):
                os.remove(audio_temp)
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error durante la descarga:\n{str(e)}")
        finally:
            self.progress_var.set(0)
    
    def download_video(self):
        """Administra la lógica de descarga según las opciones seleccionadas."""
        try:
            url = self.url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Por favor, ingrese una URL de YouTube.")
                return
            
            save_path = self.save_path_var.get()
            format_type = self.format_var.get()
            custom_format = self.custom_format_var.get().strip()
            
            # Verificar yt-dlp
            if not self.check_yt_dlp():
                return
            
            self.status_var.set("Iniciando descarga...")
            self.root.update_idletasks()
            
            downloaded_file = None
            output_template = os.path.join(save_path, "%(title)s.%(ext)s")
            
            # Caso 1: MP3 sin formato personalizado
            if format_type == "mp3" and not custom_format:
                self.status_var.set("Descargando audio en MP3...")
                cmd_title = ["yt-dlp", "--get-title", url]
                process = subprocess.Popen(cmd_title, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                title, error = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Error al obtener el título: {error}")
                
                title = title.strip()
                title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
                
                temp_file = os.path.join(tempfile.gettempdir(), f"{title}.m4a")
                final_mp3 = os.path.join(save_path, f"{title}.mp3")
                
                cmd = ["yt-dlp", url, "-f", "bestaudio[ext=m4a]/bestaudio", "-o", temp_file, "--no-warnings"]
                self.current_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in self.current_process.stdout:
                    if not self.download_active:
                        return
                    self.status_var.set(line.strip())
                    self.root.update_idletasks()
                    if "[download]" in line and "%" in line:
                        try:
                            percent_text = line.split("%")[0].split()[-1]
                            percent = float(percent_text)
                            self.progress_var.set(percent)
                        except (ValueError, IndexError):
                            pass
                
                self.current_process.wait()
                
                if self.current_process.returncode != 0 and self.download_active:
                    error_output = self.current_process.stderr.read()
                    raise Exception(f"Error en yt-dlp: {error_output}")
                
                if not os.path.exists(temp_file):
                    raise Exception("No se pudo descargar el audio")
                
                self.status_var.set("Renombrando a MP3...")
                shutil.copy2(temp_file, final_mp3)
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                downloaded_file = final_mp3
            
            # Caso 2: Formato personalizado con '+', se fuerza descarga separada y merge
            elif "+" in custom_format:
                # Llamamos a la función que descarga separado y luego mergea
                self.download_separate_and_merge(url, custom_format, save_path)
                return  # Importante: retornamos para no continuar con la lógica de "else"
            
            # Caso 3: Formato personalizado (sin '+') o MP4 normal
            else:
                cmd = ["yt-dlp", url, "-o", output_template, "--no-warnings"]
                if custom_format:
                    cmd.extend(["-f", custom_format])
                    self.status_var.set(f"Usando formato personalizado: {custom_format}")
                else:
                    cmd.extend(["-f", "best[ext=mp4]/best"])
                
                self.current_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in self.current_process.stdout:
                    if not self.download_active:
                        return
                    self.status_var.set(line.strip())
                    self.root.update_idletasks()
                    if "[download]" in line and "%" in line:
                        try:
                            percent_text = line.split("%")[0].split()[-1]
                            percent = float(percent_text)
                            self.progress_var.set(percent)
                        except (ValueError, IndexError):
                            pass
                    if "Destination:" in line:
                        downloaded_file = line.split("Destination:", 1)[1].strip()
                
                self.current_process.wait()
                
                if self.current_process.returncode != 0 and self.download_active:
                    error_output = self.current_process.stderr.read()
                    raise Exception(f"Error en yt-dlp: {error_output}")
            
            # Si la descarga no fue detenida y no hubo error, informamos
            if self.download_active:
                self.status_var.set("Descarga completada")
                self.progress_var.set(100)
                
                if downloaded_file:
                    messagebox.showinfo("Descarga Completada", f"El archivo se ha guardado como:\n{downloaded_file}")
                else:
                    messagebox.showinfo("Descarga Completada", "El archivo se ha descargado correctamente.")
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error durante la descarga:\n{str(e)}")
        
        finally:
            self.progress_var.set(0)
    
    def stop_download(self):
        """Detiene la descarga en curso, si existe."""
        if self.current_process and self.download_active:
            try:
                self.current_process.terminate()
                if os.name == 'nt':
                    import ctypes
                    PROCESS_TERMINATE = 1
                    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, self.current_process.pid)
                    ctypes.windll.kernel32.TerminateProcess(handle, -1)
                    ctypes.windll.kernel32.CloseHandle(handle)
                
                self.status_var.set("Descarga detenida por el usuario")
                self.progress_var.set(0)
                self.download_active = False
                self.download_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                
                # Limpiar archivos temporales
                try:
                    temp_dir = tempfile.gettempdir()
                    for file in os.listdir(temp_dir):
                        if file.endswith(".part") or file.endswith(".ytdl"):
                            os.remove(os.path.join(temp_dir, file))
                except:
                    pass
                
            except Exception as e:
                self.status_var.set(f"Error al detener la descarga: {str(e)}")
    
    def start_download(self):
        """Inicia la descarga en un hilo separado."""
        if self.download_active:
            messagebox.showinfo("En progreso", "Ya hay una descarga en progreso")
            return
        
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.download_active = True
        
        threading.Thread(target=self._download_thread, daemon=True).start()
    
    def _download_thread(self):
        """Hilo que gestiona la llamada a download_video."""
        try:
            self.download_video()
        finally:
            self.download_active = False
            self.download_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
