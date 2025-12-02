#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import paramiko
import json
import os
import threading
import time
from datetime import datetime
import subprocess
import math

class UltraModernSSHConfigBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SSH Config Backup")
        self.root.geometry("1245x775")
        self.root.configure(bg='#000000')
        self.root.resizable(True, True)
        
        self.colors = {
            'bg_primary': '#000000',
            'bg_secondary': '#0a0a0a',
            'bg_card': '#1a1a1a',
            'bg_card_light': '#2a2a2a',
            'bg_hover': '#333333',
            'accent': '#007aff',
            'accent_hover': '#0056cc',
            'accent_light': '#409cff',
            'text_primary': '#ffffff',
            'text_secondary': '#8e8e93',
            'success': '#30d158',
            'warning': '#ff9f0a',
            'error': '#ff453a',
        }
        
        self.current_tab = 0
        self.tab_frames = []
        self.animation_running = False
        
        self.configs = []
        self.ssh_config = {}
        self.schedule_config = {}
        
        # Определяем домашнюю директорию и путь для бэкапов
        self.home_dir = os.path.expanduser("~")
        self.backup_base_dir = os.path.join(self.home_dir, "RemoteBackup", "backups")
        
        # Создаем базовую директорию если не существует
        os.makedirs(self.backup_base_dir, exist_ok=True)
        
        self.load_data()
        
        self.create_gui()
    
    def create_gui(self):
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_container.pack(fill='both', expand=True)
        
        self.create_header()
        
        self.content_frame = tk.Frame(self.main_container, bg=self.colors['bg_primary'])
        self.content_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        self.create_tab_system()
        
        self.show_tab(0)
    
    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.colors['bg_secondary'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        logo_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        logo_frame.pack(side='left', padx=30, pady=20)
        
        self.logo_label = tk.Label(logo_frame, text="⚡", font=('Arial', 24),
                                  bg=self.colors['bg_secondary'], fg=self.colors['accent'])
        self.logo_label.pack(side='left')
        
        self.title_label = tk.Label(logo_frame, text="SSH Backup", 
                                   font=('Arial', 22, 'bold'),
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.title_label.pack(side='left', padx=(10, 0))
        
        nav_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        nav_frame.pack(side='left', padx=50, pady=20)
        
        self.nav_buttons = []
        tabs = [
            ("📁 Конфиги", 0),
            ("  SSH Настройки", 1),
            ("⏰ Авто-копирование", 2),
            ("ℹ️ О программе", 3)
        ]
        
        for text, tab_index in tabs:
            btn = self.create_oval_nav_button(nav_frame, text, tab_index)
            btn.pack(side='left', padx=5)
            self.nav_buttons.append(btn)
        
        # Статус
        self.status_label = tk.Label(header_frame, text="Готов к работе", 
                                   font=('Arial', 11),
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_secondary'])
        self.status_label.pack(side='right', padx=30, pady=20)
    
    def create_oval_nav_button(self, parent, text, tab_index):
        btn_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        
        btn = tk.Label(btn_frame, text=text, font=('Arial', 11, 'bold'),
                      bg=self.colors['bg_card_light'], fg=self.colors['text_secondary'],
                      cursor='hand2', padx=20, pady=10, bd=0, relief='flat')
        
        def on_enter(e):
            if tab_index != self.current_tab and not self.animation_running:
                btn.config(bg=self.colors['bg_hover'], fg=self.colors['text_primary'])
        
        def on_leave(e):
            if tab_index != self.current_tab and not self.animation_running:
                btn.config(bg=self.colors['bg_card_light'], fg=self.colors['text_secondary'])
        
        def on_click(e):
            if not self.animation_running:
                self.animate_tab_change(tab_index)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        btn.pack()
        return btn_frame
    
    def animate_tab_change(self, new_tab):
        if new_tab == self.current_tab or self.animation_running:
            return
        
        self.animation_running = True
        
        for i, btn_frame in enumerate(self.nav_buttons):
            btn = btn_frame.winfo_children()[0]  # Получаем внутренний лейбл
            if i == new_tab:
                btn.config(bg=self.colors['accent'], fg=self.colors['text_primary'])
            else:
                btn.config(bg=self.colors['bg_card_light'], fg=self.colors['text_secondary'])
        
        self.ultra_smooth_animation(self.current_tab, new_tab)
    
    def ultra_smooth_animation(self, old_tab, new_tab):
        
        direction = 1 if new_tab > old_tab else -1
        
        self.tab_frames[new_tab].place(relx=direction, rely=0, relwidth=1, relheight=1)
        self.tab_frames[new_tab].lift()
        self.tab_frames[old_tab].place(relx=0, rely=0, relwidth=1, relheight=1)
        
        start_time = time.perf_counter()  # время
        duration = 0.5  
        
        old_frame = self.tab_frames[old_tab]
        new_frame = self.tab_frames[new_tab]
        
        def animate():
            current_time = time.perf_counter() - start_time
            progress = min(current_time / duration, 1.0)
            
            # cubic-bezier(0.16, 0.89, 0.32, 1.05) - старая
            bezier_progress = self.cubic_bezier_smooth(progress)
            
            old_x = -direction * bezier_progress
            new_x = direction - direction * bezier_progress
            
            old_frame.place(relx=old_x, rely=0, relwidth=1, relheight=1)
            new_frame.place(relx=new_x, rely=0, relwidth=1, relheight=1)
            
            if progress < 1.0:
                self.root.after(5, animate)
            else:
                old_frame.place_forget()
                new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                self.current_tab = new_tab
                self.animation_running = False
        
        animate()
    
    def cubic_bezier_smooth(self, t):
        # cubic-bezier(0.16, 0.89, 0.32, 1.05)
        if t <= 0:
            return 0
        if t >= 1:
            return 1
            
        p0 = 0
        p1 = 0.16
        p2 = 0.32
        p3 = 1.05
        
        t_final = t
        for _ in range(4):
            current = self.bezier_value(t_final, p0, p1, p2, p3)
            derivative = self.bezier_derivative(t_final, p0, p1, p2, p3)
            if abs(derivative) < 1e-6:
                break
            t_final = t_final - (current - t) / derivative
        
        return self.bezier_value(t_final, 0, 0.89, 1.0, 1.0)
    
    def bezier_value(self, t, p0, p1, p2, p3):
        u = 1 - t
        return (u*u*u*p0 + 3*u*u*t*p1 + 3*u*t*t*p2 + t*t*t*p3)
    
    def bezier_derivative(self, t, p0, p1, p2, p3):
        u = 1 - t
        return (3*u*u*(p1-p0) + 6*u*t*(p2-p1) + 3*t*t*(p3-p2))
    
    def create_tab_system(self):
        self.create_configs_tab()
        self.create_ssh_tab()
        self.create_schedule_tab()
        self.create_about_tab()
    
    def create_configs_tab(self):
        frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.tab_frames.append(frame)
        
        title = tk.Label(frame, text="Управление конфигурациями", 
                        font=('Arial', 28, 'bold'),
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'])
        title.pack(pady=(0, 20))
        
        subtitle = tk.Label(frame, text="Добавьте файлы для автоматического резервного копирования", 
                           font=('Arial', 14),
                           bg=self.colors['bg_primary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(pady=(0, 30))
        
        add_card = self.create_modern_card(frame)
        add_card.pack(fill='x', padx=0, pady=15)
        
        tk.Label(add_card, text="Новый путь к конфигу", 
                font=('Arial', 16, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 15), padx=25)
        
        input_frame = tk.Frame(add_card, bg=self.colors['bg_card'])
        input_frame.pack(fill='x', padx=25, pady=(0, 20))
        
        self.new_config_path = tk.Entry(input_frame, 
                                       bg=self.colors['bg_card_light'],
                                       fg=self.colors['text_primary'],
                                       font=('Arial', 12),
                                       insertbackground=self.colors['text_primary'],
                                       relief='flat')
        self.new_config_path.pack(side='left', fill='x', expand=True, padx=(0, 15), ipady=8)
        self.new_config_path.insert(0, "/etc/ssh/sshd_config")  # путь по умолчанию
        
        add_btn = self.create_modern_button(input_frame, "Добавить", self.add_config_path, accent=True)
        add_btn.pack(side='right')
        
        list_card = self.create_modern_card(frame)
        list_card.pack(fill='both', expand=True, padx=0, pady=15)
        
        header_frame = tk.Frame(list_card, bg=self.colors['bg_card'])
        header_frame.pack(fill='x', padx=25, pady=20)
        
        tk.Label(header_frame, text="Список конфигов", 
                font=('Arial', 16, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(side='left')
        
        btn_frame = tk.Frame(header_frame, bg=self.colors['bg_card'])
        btn_frame.pack(side='right')
        
        self.create_modern_button(btn_frame, "Проверить пути", self.test_remote_paths).pack(side='left', padx=5)
        self.create_modern_button(btn_frame, "Очистить все", self.clear_configs).pack(side='left', padx=5)
        
        # скроллбар
        list_container = tk.Frame(list_card, bg=self.colors['bg_card'])
        list_container.pack(fill='both', expand=True, padx=25, pady=(0, 20))
        
        self.configs_listbox = tk.Listbox(list_container, 
                                         bg=self.colors['bg_card_light'],
                                         fg=self.colors['text_primary'],
                                         selectbackground=self.colors['accent'],
                                         selectforeground=self.colors['text_primary'],
                                         font=('Arial', 12),
                                         relief='flat',
                                         bd=0,
                                         highlightthickness=0,
                                         activestyle='none')
        
        scrollbar = ttk.Scrollbar(list_container)
        
        self.configs_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.configs_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.configs_listbox.yview)
        
        self.configs_listbox.bind('<Double-Button-1>', lambda e: self.remove_config_path())
        
        self.update_configs_list()
    
    def create_ssh_tab(self):
        frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.tab_frames.append(frame)
        
        title = tk.Label(frame, text="SSH Настройки", 
                        font=('Arial', 28, 'bold'),
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'])
        title.pack(pady=(0, 20))
        
        subtitle = tk.Label(frame, text="Настройте подключение к удаленному серверу", 
                           font=('Arial', 14),
                           bg=self.colors['bg_primary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(pady=(0, 30))
        
        main_card = self.create_modern_card(frame)
        main_card.pack(fill='both', expand=True, padx=0, pady=15)
        
        form_frame = tk.Frame(main_card, bg=self.colors['bg_card'])
        form_frame.pack(fill='x', padx=30, pady=30)
        
        self.create_modern_form_field(form_frame, "IP Адрес сервера", "ssh_ip", 0)
        self.create_modern_form_field(form_frame, "SSH Порт", "ssh_port", 1, "22")
        self.create_modern_form_field(form_frame, "Имя пользователя", "ssh_user", 2)
        self.create_modern_form_field(form_frame, "Пароль", "ssh_password", 3, password=True)
        
        actions_frame = tk.Frame(main_card, bg=self.colors['bg_card'])
        actions_frame.pack(pady=(0, 30))
        
        self.create_modern_button(actions_frame, "Тестировать подключение", 
                                self.test_connection).pack(side='left', padx=8)
        self.create_modern_button(actions_frame, "Сохранить настройки", 
                                self.save_ssh_settings).pack(side='left', padx=8)
        self.create_modern_button(actions_frame, "Запустить копирование", 
                                self.start_backup, accent=True).pack(side='left', padx=8)
    
    def create_schedule_tab(self):
        frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.tab_frames.append(frame)
        
        title = tk.Label(frame, text="Автоматическое копирование", 
                        font=('Arial', 28, 'bold'),
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'])
        title.pack(pady=(0, 20))
        
        subtitle = tk.Label(frame, text="Настройте автоматическое резервное копирование по расписанию", 
                           font=('Arial', 14),
                           bg=self.colors['bg_primary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(pady=(0, 30))
        
        schedule_card = self.create_modern_card(frame)
        schedule_card.pack(fill='x', padx=0, pady=15)
        
        tk.Label(schedule_card, text="Настройки расписания", 
                font=('Arial', 16, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 15), padx=25)
        
        form_frame = tk.Frame(schedule_card, bg=self.colors['bg_card'])
        form_frame.pack(fill='x', padx=25, pady=(0, 20))
        
        time_frame = tk.Frame(form_frame, bg=self.colors['bg_card'])
        time_frame.pack(fill='x', pady=10)
        
        tk.Label(time_frame, text="Время (HH:MM):", 
                font=('Arial', 12),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(side='left')
        
        self.schedule_time = tk.Entry(time_frame, 
                                     bg=self.colors['bg_card_light'],
                                     fg=self.colors['text_primary'],
                                     font=('Arial', 12),
                                     insertbackground=self.colors['text_primary'],
                                     relief='flat',
                                     width=10)
        self.schedule_time.pack(side='left', padx=10, ipady=6)
        self.schedule_time.insert(0, self.schedule_config.get('time', '00:00'))
        
        interval_frame = tk.Frame(form_frame, bg=self.colors['bg_card'])
        interval_frame.pack(fill='x', pady=10)
        
        tk.Label(interval_frame, text="Интервал (дни):", 
                font=('Arial', 12),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(side='left')
        
        self.schedule_interval = tk.Entry(interval_frame, 
                                        bg=self.colors['bg_card_light'],
                                        fg=self.colors['text_primary'],
                                        font=('Arial', 12),
                                        insertbackground=self.colors['text_primary'],
                                        relief='flat',
                                        width=10)
        self.schedule_interval.pack(side='left', padx=10, ipady=6)
        self.schedule_interval.insert(0, self.schedule_config.get('interval', '1'))
        
        buttons_frame = tk.Frame(form_frame, bg=self.colors['bg_card'])
        buttons_frame.pack(fill='x', pady=20)
        
        self.create_modern_button(buttons_frame, "Добавить в Crontab", 
                                self.add_to_crontab, accent=True).pack(side='left', padx=5)
        self.create_modern_button(buttons_frame, "Удалить из Crontab", 
                                self.remove_from_crontab).pack(side='left', padx=5)
        
        log_card = self.create_modern_card(frame)
        log_card.pack(fill='both', expand=True, padx=0, pady=15)
        
        tk.Label(log_card, text="Лог выполнения", 
                font=('Arial', 16, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(20, 15), padx=25)
        
        self.log_text = scrolledtext.ScrolledText(log_card, 
                                                 bg=self.colors['bg_card_light'],
                                                 fg=self.colors['text_primary'],
                                                 font=('Arial', 10),
                                                 wrap=tk.WORD,
                                                 relief='flat',
                                                 bd=0,
                                                 padx=15,
                                                 pady=15)
        self.log_text.pack(fill='both', expand=True, padx=25, pady=(0, 20))
        self.log_text.config(state='disabled')
    
    def create_about_tab(self):
        frame = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.tab_frames.append(frame)
        
        content = self.create_modern_card(frame)
        content.pack(expand=True, fill='both', padx=80, pady=80)
        
        # Иконка приложения
        icon_frame = tk.Frame(content, bg=self.colors['bg_card'])
        icon_frame.pack(pady=(40, 20))
        
        icon_bg = tk.Frame(icon_frame, bg=self.colors['accent'], width=100, height=100)
        icon_bg.pack_propagate(False)
        icon_bg.pack()
        
        icon_label = tk.Label(icon_bg, text="⚡", font=('Arial', 40),
                             bg=self.colors['accent'], fg='#ffffff')
        icon_label.pack(expand=True)
        
        # Информация
        info_frame = tk.Frame(content, bg=self.colors['bg_card'])
        info_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        tk.Label(info_frame, text="SSH Config Backup", 
                font=('Arial', 28, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']).pack(pady=10)
        
        tk.Label(info_frame, text="Версия 1.0", 
                font=('Arial', 16),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(pady=5)
        
        tk.Label(info_frame, text="Создатель: @Rexilone", 
                font=('Arial', 14),
                bg=self.colors['bg_card'],
                fg=self.colors['accent_light']).pack(pady=15)
        
        desc_text = """Современное приложение для безопасного резервного копирования 
конфигурационных файлов через SSH соединение.
"""
        
        desc_label = tk.Label(info_frame, text=desc_text, font=('Arial', 12),
                            bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                            justify='center')
        desc_label.pack(pady=20)
    
    def create_modern_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=0)
        return card
    
    def create_modern_button(self, parent, text, command, accent=False):
        btn = tk.Label(parent, text=text, 
                      font=('Arial', 12, 'bold' if accent else 'normal'),
                      bg=self.colors['accent'] if accent else self.colors['bg_card_light'],
                      fg=self.colors['text_primary'],
                      cursor='hand2',
                      padx=20, pady=10)
        
        def on_enter(e):
            btn.config(bg=self.colors['accent_hover'] if accent else self.colors['bg_hover'])
        
        def on_leave(e):
            btn.config(bg=self.colors['accent'] if accent else self.colors['bg_card_light'])
        
        def on_click(e):
            command()
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return btn
    
    def create_modern_form_field(self, parent, label, field_name, row, default="", password=False):
        field_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        field_frame.pack(fill='x', pady=12)
        
        tk.Label(field_frame, text=label, font=('Arial', 12),
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 8))
        
        entry = tk.Entry(field_frame, 
                        bg=self.colors['bg_card_light'],
                        fg=self.colors['text_primary'],
                        font=('Arial', 12),
                        insertbackground=self.colors['text_primary'],
                        relief='flat')
        
        if password:
            entry.config(show='•')
        
        entry.pack(fill='x', ipady=8)
        entry.insert(0, self.ssh_config.get(field_name.split('_')[1], default))
        
        setattr(self, field_name, entry)
    
    def show_tab(self, tab_index):
        self.current_tab = tab_index
        for frame in self.tab_frames:
            frame.place_forget()
        
        self.tab_frames[tab_index].place(relx=0, rely=0, relwidth=1, relheight=1)
        
        for i, btn_frame in enumerate(self.nav_buttons):
            btn = btn_frame.winfo_children()[0]
            if i == tab_index:
                btn.config(bg=self.colors['accent'], fg=self.colors['text_primary'])
            else:
                btn.config(bg=self.colors['bg_card_light'], fg=self.colors['text_secondary'])
    
    def add_config_path(self):
        path = self.new_config_path.get().strip()
        if path and path not in self.configs:
            self.configs.append(path)
            self.new_config_path.delete(0, tk.END)
            self.update_configs_list()
            self.save_data()
            self.log_message(f"✅ Добавлен путь: {path}")
            self.set_status("Конфиг добавлен")
        elif not path:
            messagebox.showwarning("Предупреждение", "Введите путь к файлу")
        else:
            messagebox.showwarning("Предупреждение", "Этот путь уже добавлен")
    
    def remove_config_path(self):
        selection = self.configs_listbox.curselection()
        if selection:
            index = selection[0]
            removed = self.configs.pop(index)
            self.update_configs_list()
            self.save_data()
            self.log_message(f"🗑️ Удален путь: {removed}")
            self.set_status("Конфиг удален")
    
    def clear_configs(self):
        if self.configs:
            self.configs.clear()
            self.update_configs_list()
            self.save_data()
            self.log_message("🧹 Список конфигов очищен")
            self.set_status("Список очищен")
    
    def update_configs_list(self):
        self.configs_listbox.delete(0, tk.END)
        for config in self.configs:
            self.configs_listbox.insert(tk.END, config)
    
    def test_remote_paths(self):
        """Тестирование доступности путей на удаленном сервере"""
        if not self.validate_ssh_settings():
            messagebox.showwarning("Предупреждение", "Сначала заполните настройки SSH")
            return
        
        if not self.configs:
            messagebox.showwarning("Предупреждение", "Сначала добавьте пути для проверки")
            return
        
        threading.Thread(target=self._test_remote_paths_thread, daemon=True).start()
    
    def _test_remote_paths_thread(self):
        try:
            self.set_status("Проверка путей...")
            self.log_message("🔍 Начинаем проверку путей на сервере...")
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                self.ssh_config['ip'],
                port=int(self.ssh_config['port']),
                username=self.ssh_config['user'],
                password=self.ssh_config['password'],
                timeout=10
            )
            
            sftp = client.open_sftp()
            self.log_message("✅ Подключение к серверу установлено")
            
            for config_path in self.configs:
                try:
                    file_stat = sftp.stat(config_path)
                    if file_stat.st_mode & 0o170000 == 0o100000:  
                        file_type = "файл"
                    elif file_stat.st_mode & 0o170000 == 0o040000:  
                        file_type = "директория"
                    else:
                        file_type = "специальный файл"
                    
                    self.log_message(f"✅ {config_path} - {file_type} ({file_stat.st_size} байт)")
                except FileNotFoundError:
                    self.log_message(f"❌ {config_path} - файл не найден")
                except PermissionError:
                    self.log_message(f"🚫 {config_path} - нет прав доступа")
                except Exception as e:
                    self.log_message(f"⚠️ {config_path} - ошибка: {str(e)}")
            
            sftp.close()
            client.close()
            self.log_message("🔌 Подключение закрыто")
            self.set_status("Проверка путей завершена")
            
        except Exception as e:
            self.log_message(f"💥 Ошибка подключения: {str(e)}")
            self.set_status("Ошибка подключения")
    
    def save_ssh_settings(self):
        self.ssh_config = {
            'ip': self.ssh_ip.get(),
            'port': self.ssh_port.get(),
            'user': self.ssh_user.get(),
            'password': self.ssh_password.get()
        }
        self.save_data()
        self.log_message("💾 Настройки SSH сохранены")
        self.set_status("Настройки сохранены")
        messagebox.showinfo("Успех", "Настройки SSH сохранены!")
    
    def test_connection(self):
        if not self.validate_ssh_settings():
            return
        
        self.set_status("Тестирование подключения...")
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                self.ssh_config['ip'],
                port=int(self.ssh_config['port']),
                username=self.ssh_config['user'],
                password=self.ssh_config['password'],
                timeout=10
            )
            
            sftp = client.open_sftp()
            sftp.close()
            
            client.close()
            self.log_message("✅ Подключение успешно установлено")
            self.set_status("Подключение установлено")
            messagebox.showinfo("Успех", "Подключение успешно установлено!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка подключения: {str(e)}")
            self.set_status("Ошибка подключения")
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")
    
    def start_backup(self):
        if not self.validate_ssh_settings():
            messagebox.showwarning("Предупреждение", "Сначала заполните настройки SSH")
            return
        
        if not self.configs:
            messagebox.showwarning("Предупреждение", "Сначала добавьте конфиги для копирования")
            return
        
        threading.Thread(target=self.perform_backup, daemon=True).start()
    
    def copy_via_scp(self, remote_path, local_path, is_directory=False):
        """Копирование файла или директории через SCP"""
        try:
            scp_command = [
                'scp',
                '-P', str(self.ssh_config['port']),
                '-o', 'StrictHostKeyChecking=no',
                '-r' if is_directory else '',
                f"{self.ssh_config['user']}@{self.ssh_config['ip']}:{remote_path}",
                local_path
            ]
            
            scp_command = [arg for arg in scp_command if arg]
            
            if self.ssh_config.get('password'):
                scp_command = [
                    'sshpass',
                    '-p', self.ssh_config['password']
                ] + scp_command
            
            self.log_message(f"🔧 Выполняем SCP команду: {' '.join(scp_command)}")
            
            result = subprocess.run(
                scp_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True
            else:
                self.log_message(f"❌ SCP ошибка: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("❌ SCP таймаут")
            return False
        except Exception as e:
            self.log_message(f"❌ SCP исключение: {str(e)}")
            return False
    
    def copy_directory_via_sftp(self, sftp, remote_path, local_path):
        """Рекурсивное копирование директории через SFTP"""
        try:
            os.makedirs(local_path, exist_ok=True)
            
            files = sftp.listdir(remote_path)
            
            copied_files = 0
            for file in files:
                remote_file_path = os.path.join(remote_path, file).replace('\\', '/')
                local_file_path = os.path.join(local_path, file)
                
                try:
                    file_stat = sftp.stat(remote_file_path)
                    
                    if file_stat.st_mode & 0o170000 == 0o040000:
                        self.log_message(f"📁 Копируем поддиректорию: {file}")
                        if self.copy_directory_via_sftp(sftp, remote_file_path, local_file_path):
                            copied_files += 1
                    else:
                        self.log_message(f"📄 Копируем файл: {file}")
                        sftp.get(remote_file_path, local_file_path)
                        if os.path.exists(local_file_path):
                            copied_files += 1
                            
                except Exception as e:
                    self.log_message(f"❌ Ошибка копирования {file}: {str(e)}")
            
            return copied_files > 0
            
        except Exception as e:
            self.log_message(f"❌ Ошибка копирования директории {remote_path}: {str(e)}")
            return False
    
    def perform_backup(self):
        try:
            self.set_status("Запуск копирования...")
            self.log_message("🚀 Запуск резервного копирования...")
            
            # Используем домашнюю директорию для бэкапов
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.backup_base_dir, f"{self.ssh_config['ip']}_{timestamp}")
            
            os.makedirs(backup_dir, exist_ok=True)
            self.log_message(f"📁 Создана папка для бэкапов: {backup_dir}")
            
            success_count = 0
            failed_files = []
            
            file_types = {}
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    self.ssh_config['ip'],
                    port=int(self.ssh_config['port']),
                    username=self.ssh_config['user'],
                    password=self.ssh_config['password'],
                    timeout=10
                )
                sftp = client.open_sftp()
                
                for config_path in self.configs:
                    try:
                        file_stat = sftp.stat(config_path)
                        if file_stat.st_mode & 0o170000 == 0o040000:
                            file_types[config_path] = 'directory'
                        else:
                            file_types[config_path] = 'file'
                        self.log_message(f"📊 {config_path} - {file_types[config_path]}")
                    except Exception as e:
                        self.log_message(f"❌ Не удалось определить тип {config_path}: {str(e)}")
                        file_types[config_path] = 'unknown'
                
                sftp.close()
                client.close()
            except Exception as e:
                self.log_message(f"❌ Ошибка определения типов файлов: {str(e)}")
                for config_path in self.configs:
                    file_types[config_path] = 'file'
            
            for config_path in self.configs:
                try:
                    self.log_message(f"🔍 Обрабатываем: {config_path}")
                    
                    filename = os.path.basename(config_path)
                    local_path = os.path.join(backup_dir, filename)
                    
                    is_directory = file_types.get(config_path) == 'directory'
                    
                    if is_directory:
                        self.log_message(f"📁 Обнаружена директория, используем рекурсивное копирование")
                    
                    self.log_message("🔄 Метод 1: Пробуем SCP...")
                    if self.copy_via_scp(config_path, local_path, is_directory):
                        if os.path.exists(local_path):
                            if is_directory:
                                file_count = sum([len(files) for r, d, files in os.walk(local_path)])
                                self.log_message(f"✅ Успешно скопирована директория через SCP: {filename} ({file_count} файлов)")
                            else:
                                file_size = os.path.getsize(local_path)
                                self.log_message(f"✅ Успешно скопирован файл через SCP: {filename} ({file_size} байт)")
                            success_count += 1
                            continue
                    
                    if is_directory:
                        self.log_message("🔄 Метод 2: Пробуем рекурсивное SFTP для директории...")
                        try:
                            client = paramiko.SSHClient()
                            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            client.connect(
                                self.ssh_config['ip'],
                                port=int(self.ssh_config['port']),
                                username=self.ssh_config['user'],
                                password=self.ssh_config['password'],
                                timeout=10
                            )
                            sftp = client.open_sftp()
                            
                            if self.copy_directory_via_sftp(sftp, config_path, local_path):
                                file_count = sum([len(files) for r, d, files in os.walk(local_path)])
                                self.log_message(f"✅ Успешно скопирована директория через SFTP: {filename} ({file_count} файлов)")
                                success_count += 1
                                sftp.close()
                                client.close()
                                continue
                            else:
                                self.log_message(f"❌ Рекурсивное SFTP не удалось")
                            
                            sftp.close()
                            client.close()
                        except Exception as e:
                            self.log_message(f"❌ Ошибка рекурсивного SFTP: {str(e)}")
                    
                    if not is_directory:
                        self.log_message("🔄 Метод 3: Пробуем SFTP get...")
                        try:
                            client = paramiko.SSHClient()
                            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            client.connect(
                                self.ssh_config['ip'],
                                port=int(self.ssh_config['port']),
                                username=self.ssh_config['user'],
                                password=self.ssh_config['password'],
                                timeout=10
                            )
                            sftp = client.open_sftp()
                            sftp.get(config_path, local_path)
                            sftp.close()
                            client.close()
                            
                            if os.path.exists(local_path):
                                file_size = os.path.getsize(local_path)
                                self.log_message(f"✅ Успешно скопирован через SFTP: {filename} ({file_size} байт)")
                                success_count += 1
                                continue
                            else:
                                self.log_message(f"❌ SFTP: файл не создан")
                                
                        except Exception as e:
                            self.log_message(f"❌ SFTP ошибка: {str(e)}")
                    
                    self.log_message(f"❌ Все методы копирования не сработали для: {config_path}")
                    failed_files.append(config_path)
                        
                except Exception as e:
                    self.log_message(f"💥 Критическая ошибка обработки {config_path}: {str(e)}")
                    failed_files.append(config_path)
            
            abs_backup_dir = os.path.abspath(backup_dir)
            self.log_message(f"🎉 Резервное копирование завершено. Успешно: {success_count}/{len(self.configs)}")
            self.log_message(f"📂 Файлы сохранены в: {abs_backup_dir}")
            self.set_status(f"Копирование завершено ({success_count}/{len(self.configs)})")
            
            if success_count > 0:
                messagebox.showinfo("Завершено", 
                                  f"Резервное копирование завершено!\n\n"
                                  f"Успешно: {success_count}/{len(self.configs)}\n"
                                  f"Файлы сохранены в:\n{abs_backup_dir}")
            else:
                error_details = "Не удалось скопировать ни одного файла!\n\n"
                error_details += "Возможные причины:\n"
                error_details += "• Проверьте доступность SCP на сервере\n"
                error_details += "• Проверьте права доступа к файлам\n"
                error_details += "• Проверьте достаточно ли места на диске\n\n"
                error_details += "Подробности в логах."
                
                messagebox.showerror("Ошибка", error_details)
                
        except Exception as e:
            self.log_message(f"💥 Критическая ошибка: {str(e)}")
            self.set_status("Ошибка копирования")
            messagebox.showerror("Ошибка", f"Ошибка при резервном копировании: {str(e)}")
    
    def add_to_crontab(self):
        if not self.validate_ssh_settings() or not self.configs:
            messagebox.showwarning("Предупреждение", "Заполните настройки SSH и добавьте конфиги")
            return
        
        time_str = self.schedule_time.get()
        interval_days = self.schedule_interval.get()
        
        try:
            hours, minutes = map(int, time_str.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Неверный формат времени. Используйте HH:MM")
            return
        
        try:
            interval = int(interval_days)
            if interval < 1:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Интервал должен быть целым числом больше 0")
            return
        
        script_path = os.path.abspath(__file__)
        cron_command = f"{minutes} {hours} */{interval} * * cd {os.path.dirname(script_path)} && python {script_path} --auto-backup\n"
        
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            lines = current_crontab.split('\n')
            new_lines = [line for line in lines if script_path not in line]
            
            new_lines.append(cron_command)
            new_crontab = '\n'.join(new_lines)
            
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
            process.communicate(input=new_crontab.encode())
            
            self.schedule_config = {
                'time': time_str,
                'interval': interval_days,
                'enabled': True
            }
            self.save_data()
            
            self.log_message(f"✅ Задача добавлена в crontab: ежедневно в {time_str} каждые {interval_days} дней")
            self.set_status("Задача добавлена в crontab")
            messagebox.showinfo("Успех", f"Автоматическое копирование настроено!\nВремя: {time_str}\nИнтервал: {interval_days} дней")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка добавления в crontab: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось добавить задачу в crontab: {str(e)}")
    
    def remove_from_crontab(self):
        try:
            script_path = os.path.abspath(__file__)
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                new_lines = [line for line in lines if script_path not in line]
                new_crontab = '\n'.join(new_lines)
                
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                process.communicate(input=new_crontab.encode())
                
                self.schedule_config['enabled'] = False
                self.save_data()
                
                self.log_message("✅ Задача удалена из crontab")
                self.set_status("Задача удалена из crontab")
                messagebox.showinfo("Успех", "Автоматическое копирование отключено!")
            else:
                messagebox.showinfo("Информация", "Нет активных задач в crontab")
                
        except Exception as e:
            self.log_message(f"❌ Ошибка удаления из crontab: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось удалить задачу из crontab: {str(e)}")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def validate_ssh_settings(self):
        required_fields = ['ip', 'user', 'password']
        for field in required_fields:
            if not self.ssh_config.get(field):
                messagebox.showerror("Ошибка", f"Заполните поле: {field}")
                return False
        return True
    
    def set_status(self, message):
        self.status_label.config(text=message)
    
    def save_data(self):
        data = {
            'configs': self.configs,
            'ssh_config': self.ssh_config,
            'schedule_config': self.schedule_config
        }
        with open('ssh_backup_config.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        try:
            with open('ssh_backup_config.json', 'r') as f:
                data = json.load(f)
                self.configs = data.get('configs', [])
                self.ssh_config = data.get('ssh_config', {})
                self.schedule_config = data.get('schedule_config', {})
        except FileNotFoundError:
            self.configs = []
            self.ssh_config = {}
            self.schedule_config = {}

def main():
    root = tk.Tk()
    app = UltraModernSSHConfigBackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
