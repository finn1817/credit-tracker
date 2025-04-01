# poe_tracker.py
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from tkcalendar import Calendar
import numpy as np

class PoeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Poe Premium Credit Tracker - Created by Dan")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f5f5f5")
        self.root.iconbitmap("poe_icon.ico") if os.path.exists("poe_icon.ico") else None
        
        # set theme colors
        self.colors = {
            "primary": "#2196F3",  # blue
            "secondary": "#4CAF50",  # green
            "accent": "#FF9800",  # orange
            "warning": "#f44336",  # red
            "background": "#f5f5f5",  # light gray
            "text": "#333333",  # dark gray
            "good": "#4CAF50",  # green
            "warning": "#FF9800",  # orange
            "danger": "#f44336",  # red
        }
        
        # initialize data file
        self.data_file = "poe_tracker_data.json"
        self.load_data()
        
        # create the 'style'
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background=self.colors["background"])
        self.style.configure('TNotebook.Tab', padding=[12, 6], font=('Arial', 10))
        self.style.configure('TFrame', background=self.colors["background"])
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
        # make tabs
        self.tab_control = ttk.Notebook(root)
        
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.calendar_tab = ttk.Frame(self.tab_control)
        self.history_tab = ttk.Frame(self.tab_control)
        self.analytics_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.calendar_tab, text="Calendar View")
        self.tab_control.add(self.history_tab, text="History")
        self.tab_control.add(self.analytics_tab, text="Analytics")
        self.tab_control.add(self.settings_tab, text="Settings")
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        # set up each tab
        self.setup_dashboard()
        self.setup_calendar_view()
        self.setup_history()
        self.setup_analytics()
        self.setup_settings()
        
        # update the display
        self.update_dashboard_display()
        
        # bind tab change event
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # create status bar
        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                
                # make sure all required fields exist
                if "theme" not in self.data:
                    self.data["theme"] = "light"
                if "show_projections" not in self.data:
                    self.data["show_projections"] = True
                if "notifications" not in self.data:
                    self.data["notifications"] = True
                if "low_credit_threshold" not in self.data:
                    self.data["low_credit_threshold"] = 20  # percentage
            except json.JSONDecodeError:
                self.initialize_default_data()
        else:
            self.initialize_default_data()

    def initialize_default_data(self):
        today = datetime.now()
        reset_day = 29
        
        # calculate next reset date
        if today.day <= reset_day:
            next_reset = datetime(today.year, today.month, reset_day)
        else:
            if today.month == 12:
                next_reset = datetime(today.year + 1, 1, reset_day)
            else:
                next_reset = datetime(today.year, today.month + 1, reset_day)
        
        self.data = {
            "total_credits": 1000000,
            "remaining_credits": 1000000,
            "reset_day": reset_day,
            "next_reset": next_reset.strftime("%Y-%m-%d"),
            "daily_usage": {},
            "last_updated": today.strftime("%Y-%m-%d"),
            "theme": "light",
            "show_projections": True,
            "notifications": True,
            "low_credit_threshold": 20,  # percentage
            "notes": {}  # store notes for specific dates
        }
        self.save_data()

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
        self.status_bar.config(text=f"Data saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def on_tab_change(self, event):
        tab_id = self.tab_control.select()
        tab_name = self.tab_control.tab(tab_id, "text")
        
        if tab_name == "Calendar View":
            self.update_calendar_display()
        elif tab_name == "History":
            self.update_history_display()
        elif tab_name == "Analytics":
            self.update_analytics_display()

    def setup_dashboard(self):
        frame = self.dashboard_tab
        
        # title with logo
        header_frame = tk.Frame(frame, bg=self.colors["background"])
        header_frame.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        title_label = tk.Label(header_frame, text="Poe Premium Credit Dashboard", 
                              font=("Arial", 20, "bold"), bg=self.colors["background"])
        title_label.pack(side=tk.LEFT)
        
        # main content frame
        content_frame = tk.Frame(frame, bg=self.colors["background"])
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        # left column - credit summary
        left_frame = tk.Frame(content_frame, bg=self.colors["background"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # credit summary frame
        summary_frame = tk.LabelFrame(left_frame, text="Credit Summary", font=("Arial", 12, "bold"), 
                                     padx=20, pady=20, bg=self.colors["background"])
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        # total credits with progress bar
        tk.Label(summary_frame, text="Total Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=0, column=0, sticky="w", pady=5)
        self.total_label = tk.Label(summary_frame, text="1,000,000", font=("Arial", 11, "bold"), 
                                   bg=self.colors["background"])
        self.total_label.grid(row=0, column=1, sticky="e", pady=5)
        
        # remaining credits with progress bar
        tk.Label(summary_frame, text="Remaining Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=5)
        self.remaining_label = tk.Label(summary_frame, text="1,000,000", font=("Arial", 11, "bold"), 
                                       bg=self.colors["background"])
        self.remaining_label.grid(row=1, column=1, sticky="e", pady=5)
        
        # progress bar frame
        progress_frame = tk.Frame(summary_frame, bg=self.colors["background"])
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="0% Used", font=("Arial", 10), 
                                      bg=self.colors["background"])
        self.progress_label.pack()
        
        # used credits
        tk.Label(summary_frame, text="Used Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=3, column=0, sticky="w", pady=5)
        self.used_label = tk.Label(summary_frame, text="0", font=("Arial", 11, "bold"), 
                                  bg=self.colors["background"])
        self.used_label.grid(row=3, column=1, sticky="e", pady=5)
        
        # next reset
        tk.Label(summary_frame, text="Next Reset Date:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=4, column=0, sticky="w", pady=5)
        self.reset_label = tk.Label(summary_frame, text="Apr 29, 2025", font=("Arial", 11, "bold"), 
                                   bg=self.colors["background"])
        self.reset_label.grid(row=4, column=1, sticky="e", pady=5)
        
        # days remaining
        tk.Label(summary_frame, text="Days Until Reset:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=5, column=0, sticky="w", pady=5)
        self.days_remaining_label = tk.Label(summary_frame, text="30", font=("Arial", 11, "bold"), 
                                           bg=self.colors["background"])
        self.days_remaining_label.grid(row=5, column=1, sticky="e", pady=5)
        
        # daily average
        tk.Label(summary_frame, text="Daily Target:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=6, column=0, sticky="w", pady=5)
        self.daily_avg_label = tk.Label(summary_frame, text="33,333.33", font=("Arial", 11, "bold"), 
                                       bg=self.colors["background"])
        self.daily_avg_label.grid(row=6, column=1, sticky="e", pady=5)
        
        # weekly average
        tk.Label(summary_frame, text="Weekly Target:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=7, column=0, sticky="w", pady=5)
        self.weekly_avg_label = tk.Label(summary_frame, text="233,333.33", font=("Arial", 11, "bold"), 
                                        bg=self.colors["background"])
        self.weekly_avg_label.grid(row=7, column=1, sticky="e", pady=5)
        
        # extra credits available
        tk.Label(summary_frame, text="Extra Credits Available:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=8, column=0, sticky="w", pady=5)
        self.extra_credits_label = tk.Label(summary_frame, text="0", font=("Arial", 11, "bold"), 
                                          bg=self.colors["background"])
        self.extra_credits_label.grid(row=8, column=1, sticky="e", pady=5)
        
        # right column - usage entry and quick stats
        right_frame = tk.Frame(content_frame, bg=self.colors["background"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # usage entry frame
        entry_frame = tk.LabelFrame(right_frame, text="Record Usage", font=("Arial", 12, "bold"), 
                                   padx=20, pady=20, bg=self.colors["background"])
        entry_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # date selection with calendar button
        date_frame = tk.Frame(entry_frame, bg=self.colors["background"])
        date_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        tk.Label(date_frame, text="Date:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = tk.Entry(date_frame, textvariable=self.date_var, font=("Arial", 11), width=12)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        cal_button = tk.Button(date_frame, text="📅", command=self.show_calendar_picker, 
                              font=("Arial", 11), bg=self.colors["primary"], fg="white")
        cal_button.pack(side=tk.LEFT)
        
        # remaining credits entry
        tk.Label(entry_frame, text="Remaining Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=5)
        self.remaining_entry_var = tk.StringVar()
        self.remaining_entry = tk.Entry(entry_frame, textvariable=self.remaining_entry_var, 
                                       font=("Arial", 11), width=12)
        self.remaining_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # note entry
        tk.Label(entry_frame, text="Note (optional):", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=2, column=0, sticky="w", pady=5)
        self.note_entry_var = tk.StringVar()
        self.note_entry = tk.Entry(entry_frame, textvariable=self.note_entry_var, 
                                  font=("Arial", 11), width=25)
        self.note_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # update button
        update_btn = tk.Button(entry_frame, text="Update", command=self.update_usage, 
                              font=("Arial", 11, "bold"), bg=self.colors["secondary"], fg="white", padx=15)
        update_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
        # quick stats frame
        stats_frame = tk.LabelFrame(right_frame, text="Quick Stats", font=("Arial", 12, "bold"), 
                                   padx=20, pady=20, bg=self.colors["background"])
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # today's usage
        tk.Label(stats_frame, text="Today's Usage:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=0, column=0, sticky="w", pady=5)
        self.today_usage_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                         bg=self.colors["background"])
        self.today_usage_label.grid(row=0, column=1, sticky="e", pady=5)
        
        # yesterday's usage
        tk.Label(stats_frame, text="Yesterday's Usage:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=5)
        self.yesterday_usage_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                             bg=self.colors["background"])
        self.yesterday_usage_label.grid(row=1, column=1, sticky="e", pady=5)
        
        # last 7 days average
        tk.Label(stats_frame, text="Last 7 Days Avg:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=2, column=0, sticky="w", pady=5)
        self.week_avg_usage_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                            bg=self.colors["background"])
        self.week_avg_usage_label.grid(row=2, column=1, sticky="e", pady=5)
        
        # status indicator
        tk.Label(stats_frame, text="Current Status:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=3, column=0, sticky="w", pady=5)
        self.status_indicator = tk.Canvas(stats_frame, width=20, height=20, bg=self.colors["background"], 
                                         highlightthickness=0)
        self.status_indicator.grid(row=3, column=1, sticky="e", pady=5)
        self.status_text = tk.Label(stats_frame, text="On Track", font=("Arial", 11, "bold"), 
                                   bg=self.colors["background"])
        self.status_text.grid(row=3, column=2, sticky="w", pady=5)
        
        # graph frame
        graph_frame = tk.LabelFrame(frame, text="Usage Visualization", font=("Arial", 12, "bold"), 
                                   padx=10, pady=10, bg=self.colors["background"])
        graph_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(20, 0))
        
        # create matplotlib figure
        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=1)

    def setup_calendar_view(self):
        frame = self.calendar_tab
        
        # title
        title_label = tk.Label(frame, text="Calendar View", font=("Arial", 18, "bold"), 
                              bg=self.colors["background"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20), sticky="w")
        
        # left panel - month view
        left_frame = tk.Frame(frame, bg=self.colors["background"])
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        # month navigation
        nav_frame = tk.Frame(left_frame, bg=self.colors["background"])
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.prev_month_btn = tk.Button(nav_frame, text="◀", command=self.prev_month, 
                                       font=("Arial", 12), bg=self.colors["primary"], fg="white")
        self.prev_month_btn.pack(side=tk.LEFT)
        
        self.month_year_label = tk.Label(nav_frame, text="April 2025", font=("Arial", 14, "bold"), 
                                        width=20, bg=self.colors["background"])
        self.month_year_label.pack(side=tk.LEFT, padx=10)
        
        self.next_month_btn = tk.Button(nav_frame, text="▶", command=self.next_month, 
                                       font=("Arial", 12), bg=self.colors["primary"], fg="white")
        self.next_month_btn.pack(side=tk.LEFT)
        
        # calendar grid
        self.calendar_frame = tk.Frame(left_frame, bg=self.colors["background"])
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        # days of week header
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"), width=10, 
                    bg=self.colors["primary"], fg="white").grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # calendar cells (will be populated dynamically)
        self.calendar_cells = []
        for row in range(6):
            cell_row = []
            for col in range(7):
                cell_frame = tk.Frame(self.calendar_frame, bg="white", bd=1, relief="solid", 
                                     width=100, height=80)
                cell_frame.grid(row=row+1, column=col, sticky="nsew", padx=1, pady=1)
                cell_frame.grid_propagate(False)
                
                date_label = tk.Label(cell_frame, text="", font=("Arial", 10, "bold"), 
                                     bg="white", anchor="nw")
                date_label.place(x=5, y=5)
                
                usage_label = tk.Label(cell_frame, text="", font=("Arial", 9), bg="white", anchor="nw")
                usage_label.place(x=5, y=25)
                
                cell_row.append({
                    "frame": cell_frame,
                    "date_label": date_label,
                    "usage_label": usage_label,
                    "date": None
                })
            self.calendar_cells.append(cell_row)
        
        # configure grid weights for calendar cells
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(7):
            self.calendar_frame.rowconfigure(i, weight=1)
        
        # right panel - day details
        right_frame = tk.LabelFrame(frame, text="Day Details", font=("Arial", 12, "bold"), 
                                   padx=20, pady=20, bg=self.colors["background"])
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        
        # selected date
        tk.Label(right_frame, text="Selected Date:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=0, column=0, sticky="w", pady=5)
        self.selected_date_label = tk.Label(right_frame, text="None", font=("Arial", 11, "bold"), 
                                           bg=self.colors["background"])
        self.selected_date_label.grid(row=0, column=1, sticky="w", pady=5)
        
        # remaining credits
        tk.Label(right_frame, text="Remaining Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=5)
        self.cal_remaining_label = tk.Label(right_frame, text="N/A", font=("Arial", 11, "bold"), 
                                           bg=self.colors["background"])
        self.cal_remaining_label.grid(row=1, column=1, sticky="w", pady=5)
        
        # used credits
        tk.Label(right_frame, text="Used Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=2, column=0, sticky="w", pady=5)
        self.cal_used_label = tk.Label(right_frame, text="N/A", font=("Arial", 11, "bold"), 
                                      bg=self.colors["background"])
        self.cal_used_label.grid(row=2, column=1, sticky="w", pady=5)
        
        # target
        tk.Label(right_frame, text="Daily Target:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=3, column=0, sticky="w", pady=5)
        self.cal_target_label = tk.Label(right_frame, text="N/A", font=("Arial", 11, "bold"), 
                                        bg=self.colors["background"])
        self.cal_target_label.grid(row=3, column=1, sticky="w", pady=5)
        
        # status
        tk.Label(right_frame, text="Status:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=4, column=0, sticky="w", pady=5)
        self.cal_status_frame = tk.Frame(right_frame, bg=self.colors["background"])
        self.cal_status_frame.grid(row=4, column=1, sticky="w", pady=5)
        
        self.cal_status_indicator = tk.Canvas(self.cal_status_frame, width=15, height=15, 
                                             bg=self.colors["background"], highlightthickness=0)
        self.cal_status_indicator.pack(side=tk.LEFT)
        
        self.cal_status_text = tk.Label(self.cal_status_frame, text="N/A", font=("Arial", 11, "bold"), 
                                       bg=self.colors["background"])
        self.cal_status_text.pack(side=tk.LEFT, padx=5)
        
        # note
        tk.Label(right_frame, text="Note:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=5, column=0, sticky="w", pady=5)
        self.cal_note_text = tk.Text(right_frame, height=4, width=30, font=("Arial", 11), wrap=tk.WORD)
        self.cal_note_text.grid(row=5, column=1, sticky="w", pady=5)
        
        # edit buttons
        button_frame = tk.Frame(right_frame, bg=self.colors["background"])
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        self.save_note_btn = tk.Button(button_frame, text="Save Note", command=self.save_day_note, 
                                      font=("Arial", 11), bg=self.colors["primary"], fg="white", padx=10)
        self.save_note_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_usage_btn = tk.Button(button_frame, text="Edit Usage", command=self.edit_day_usage, 
                                       font=("Arial", 11), bg=self.colors["secondary"], fg="white", padx=10)
        self.edit_usage_btn.pack(side=tk.LEFT, padx=5)
        
        # set current month
        self.current_calendar_date = datetime.now()
        
        # configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def setup_history(self):
        frame = self.history_tab
        
        # title
        title_label = tk.Label(frame, text="Usage History", font=("Arial", 18, "bold"), 
                              bg=self.colors["background"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20), sticky="w")
        
        # filter frame
        filter_frame = tk.Frame(frame, bg=self.colors["background"])
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        
        # date range filter
        tk.Label(filter_frame, text="Date Range:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT, padx=(0, 5))
        
        self.date_range_var = tk.StringVar(value="All Time")
        date_range_options = ["All Time", "Current Month", "Previous Month", "Last 7 Days", "Last 30 Days", "Custom"]
        date_range_menu = ttk.Combobox(filter_frame, textvariable=self.date_range_var, 
                                      values=date_range_options, state="readonly", width=15)
        date_range_menu.pack(side=tk.LEFT, padx=5)
        date_range_menu.bind("<<ComboboxSelected>>", self.on_date_range_change)
        
        # custom date range (initially hidden)
        self.custom_range_frame = tk.Frame(filter_frame, bg=self.colors["background"])
        
        tk.Label(self.custom_range_frame, text="From:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT, padx=(10, 5))
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        from_date_entry = tk.Entry(self.custom_range_frame, textvariable=self.from_date_var, 
                                  font=("Arial", 11), width=10)
        from_date_entry.pack(side=tk.LEFT)
        
        tk.Label(self.custom_range_frame, text="To:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT, padx=(10, 5))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date_entry = tk.Entry(self.custom_range_frame, textvariable=self.to_date_var, 
                                font=("Arial", 11), width=10)
        to_date_entry.pack(side=tk.LEFT)
        
        apply_btn = tk.Button(self.custom_range_frame, text="Apply", command=self.update_history_display, 
                             font=("Arial", 10), bg=self.colors["primary"], fg="white")
        apply_btn.pack(side=tk.LEFT, padx=10)
        
        # search frame (right aligned)
        search_frame = tk.Frame(filter_frame, bg=self.colors["background"])
        search_frame.pack(side=tk.RIGHT)
        
        tk.Label(search_frame, text="Search:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 11), width=15)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.update_history_display())
        
        # export button
        export_btn = tk.Button(filter_frame, text="Export Data", command=self.export_history, 
                              font=("Arial", 11), bg=self.colors["accent"], fg="white")
        export_btn.pack(side=tk.RIGHT, padx=10)
        
        # create treeview for history
        columns = ("date", "remaining", "used_today", "daily_target", "status", "note")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        # define headings
        self.history_tree.heading("date", text="Date", command=lambda: self.sort_history_by_column("date"))
        self.history_tree.heading("remaining", text="Remaining Credits", 
                                 command=lambda: self.sort_history_by_column("remaining"))
        self.history_tree.heading("used_today", text="Used Today", 
                                 command=lambda: self.sort_history_by_column("used_today"))
        self.history_tree.heading("daily_target", text="Daily Target", 
                                 command=lambda: self.sort_history_by_column("daily_target"))
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("note", text="Note")
        
        # define columns
        self.history_tree.column("date", width=100, anchor="center")
        self.history_tree.column("remaining", width=120, anchor="center")
        self.history_tree.column("used_today", width=100, anchor="center")
        self.history_tree.column("daily_target", width=100, anchor="center")
        self.history_tree.column("status", width=100, anchor="center")
        self.history_tree.column("note", width=250, anchor="w")
        
        # add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # place treeview and scrollbar
        self.history_tree.grid(row=2, column=0, sticky="nsew", padx=(20, 0), pady=(10, 20))
        scrollbar.grid(row=2, column=1, sticky="ns", padx=(0, 20), pady=(10, 20))
        
        # bind double-click to edit
        self.history_tree.bind("<Double-1>", self.edit_history_item)
        
        # right-click menu
        self.history_context_menu = tk.Menu(self.history_tree, tearoff=0)
        self.history_context_menu.add_command(label="Edit Entry", command=self.edit_history_item)
        self.history_context_menu.add_command(label="Delete Entry", command=self.delete_history_item)
        self.history_context_menu.add_separator()
        self.history_context_menu.add_command(label="Add Note", command=self.add_history_note)
        
        self.history_tree.bind("<Button-3>", self.show_history_context_menu)
        
        # configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

    def setup_analytics(self):
        frame = self.analytics_tab
        
        # title
        title_label = tk.Label(frame, text="Usage Analytics", font=("Arial", 18, "bold"), 
                              bg=self.colors["background"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20), sticky="w")
        
        # left panel - charts
        left_frame = tk.Frame(frame, bg=self.colors["background"])
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        # chart type selector
        chart_selector_frame = tk.Frame(left_frame, bg=self.colors["background"])
        chart_selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(chart_selector_frame, text="Chart Type:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT, padx=(0, 5))
        
        self.chart_type_var = tk.StringVar(value="Daily Usage")
        chart_options = ["Daily Usage", "Usage vs Target", "Remaining Credits", "Usage Heatmap"]
        chart_type_menu = ttk.Combobox(chart_selector_frame, textvariable=self.chart_type_var, 
                                      values=chart_options, state="readonly", width=15)
        chart_type_menu.pack(side=tk.LEFT, padx=5)
        chart_type_menu.bind("<<ComboboxSelected>>", lambda e: self.update_analytics_display())
        
        # time range selector
        tk.Label(chart_selector_frame, text="Time Range:", font=("Arial", 11), 
                bg=self.colors["background"]).pack(side=tk.LEFT, padx=(20, 5))
        
        self.chart_range_var = tk.StringVar(value="Current Month")
        range_options = ["Current Month", "Previous Month", "Last 30 Days", "Last 90 Days", "All Time"]
        chart_range_menu = ttk.Combobox(chart_selector_frame, textvariable=self.chart_range_var, 
                                       values=range_options, state="readonly", width=15)
        chart_range_menu.pack(side=tk.LEFT, padx=5)
        chart_range_menu.bind("<<ComboboxSelected>>", lambda e: self.update_analytics_display())
        
        # chart frame
        chart_frame = tk.Frame(left_frame, bg="white", bd=1, relief="solid")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.analytics_fig = Figure(figsize=(8, 6), dpi=100)
        self.analytics_canvas = FigureCanvasTkAgg(self.analytics_fig, master=chart_frame)
        self.analytics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # right panel - stats
        right_frame = tk.Frame(frame, bg=self.colors["background"])
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        
        # usage statistics
        stats_frame = tk.LabelFrame(right_frame, text="Usage Statistics", font=("Arial", 12, "bold"), 
                                   padx=20, pady=20, bg=self.colors["background"])
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # total used
        tk.Label(stats_frame, text="Total Credits Used:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=0, column=0, sticky="w", pady=5)
        self.analytics_total_used = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                            bg=self.colors["background"])
        self.analytics_total_used.grid(row=0, column=1, sticky="e", pady=5)
        
        # average daily usage
        tk.Label(stats_frame, text="Average Daily Usage:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=5)
        self.analytics_avg_daily = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                           bg=self.colors["background"])
        self.analytics_avg_daily.grid(row=1, column=1, sticky="e", pady=5)
        
        # highest usage day
        tk.Label(stats_frame, text="Highest Usage Day:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=2, column=0, sticky="w", pady=5)
        self.analytics_highest_day = tk.Label(stats_frame, text="None", font=("Arial", 11, "bold"), 
                                             bg=self.colors["background"])
        self.analytics_highest_day.grid(row=2, column=1, sticky="e", pady=5)
        
        # lowest usage day
        tk.Label(stats_frame, text="Lowest Usage Day:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=3, column=0, sticky="w", pady=5)
        self.analytics_lowest_day = tk.Label(stats_frame, text="None", font=("Arial", 11, "bold"), 
                                            bg=self.colors["background"])
        self.analytics_lowest_day.grid(row=3, column=1, sticky="e", pady=5)
        
        # days over target
        tk.Label(stats_frame, text="Days Over Target:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=4, column=0, sticky="w", pady=5)
        self.analytics_over_target = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                             bg=self.colors["background"])
        self.analytics_over_target.grid(row=4, column=1, sticky="e", pady=5)
        
        # days under target
        tk.Label(stats_frame, text="Days Under Target:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=5, column=0, sticky="w", pady=5)
        self.analytics_under_target = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), 
                                              bg=self.colors["background"])
        self.analytics_under_target.grid(row=5, column=1, sticky="e", pady=5)
        
        # projection frame
        projection_frame = tk.LabelFrame(right_frame, text="Usage Projections", font=("Arial", 12, "bold"), 
                                        padx=20, pady=20, bg=self.colors["background"])
        projection_frame.pack(fill=tk.BOTH, expand=True)
        
        # projected end of month
        tk.Label(projection_frame, text="Projected End of Month:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=0, column=0, sticky="w", pady=5)
        self.analytics_projected_eom = tk.Label(projection_frame, text="0", font=("Arial", 11, "bold"), 
                                               bg=self.colors["background"])
        self.analytics_projected_eom.grid(row=0, column=1, sticky="e", pady=5)
        
        # Projected usage
        tk.Label(projection_frame, text="Projected Total Usage:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=5)
        self.analytics_projected_usage = tk.Label(projection_frame, text="0", font=("Arial", 11, "bold"), 
                                                 bg=self.colors["background"])
        self.analytics_projected_usage.grid(row=1, column=1, sticky="e", pady=5)
        
        # Recommended daily limit
        tk.Label(projection_frame, text="Recommended Daily Limit:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=2, column=0, sticky="w", pady=5)
        self.analytics_recommended = tk.Label(projection_frame, text="0", font=("Arial", 11, "bold"), 
                                             bg=self.colors["background"])
        self.analytics_recommended.grid(row=2, column=1, sticky="e", pady=5)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def setup_settings(self):
        frame = self.settings_tab
        
        # Title
        title_label = tk.Label(frame, text="Settings", font=("Arial", 18, "bold"), 
                              bg=self.colors["background"])
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20), sticky="w")
        
        # Settings frame
        settings_frame = tk.LabelFrame(frame, text="Tracker Settings", font=("Arial", 12, "bold"), 
                                      padx=20, pady=20, bg=self.colors["background"])
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Total credits
        tk.Label(settings_frame, text="Total Monthly Credits:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=0, column=0, sticky="w", pady=10)
        self.total_credits_var = tk.StringVar(value=str(self.data["total_credits"]))
        total_entry = tk.Entry(settings_frame, textvariable=self.total_credits_var, font=("Arial", 11), width=12)
        total_entry.grid(row=0, column=1, sticky="w", pady=10)
        
        # Reset day
        tk.Label(settings_frame, text="Reset Day of Month:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=1, column=0, sticky="w", pady=10)
        self.reset_day_var = tk.StringVar(value=str(self.data["reset_day"]))
        reset_day_entry = tk.Entry(settings_frame, textvariable=self.reset_day_var, font=("Arial", 11), width=12)
        reset_day_entry.grid(row=1, column=1, sticky="w", pady=10)
        
        # Low credit threshold
        tk.Label(settings_frame, text="Low Credit Alert (%):", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=2, column=0, sticky="w", pady=10)
        self.threshold_var = tk.StringVar(value=str(self.data["low_credit_threshold"]))
        threshold_entry = tk.Entry(settings_frame, textvariable=self.threshold_var, font=("Arial", 11), width=12)
        threshold_entry.grid(row=2, column=1, sticky="w", pady=10)
        
        # Theme selection
        tk.Label(settings_frame, text="Theme:", font=("Arial", 11), 
                bg=self.colors["background"]).grid(row=3, column=0, sticky="w", pady=10)
        
        self.theme_var = tk.StringVar(value=self.data["theme"])
        themes_frame = tk.Frame(settings_frame, bg=self.colors["background"])
        themes_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        tk.Radiobutton(themes_frame, text="Light", variable=self.theme_var, value="light", 
                      bg=self.colors["background"]).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(themes_frame, text="Dark", variable=self.theme_var, value="dark", 
                      bg=self.colors["background"]).pack(side=tk.LEFT)
        
        # Show projections
        self.show_projections_var = tk.BooleanVar(value=self.data["show_projections"])
        show_projections_check = tk.Checkbutton(settings_frame, text="Show Usage Projections", 
                                               variable=self.show_projections_var, 
                                               bg=self.colors["background"])
        show_projections_check.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)
        
        # Enable notifications
        self.notifications_var = tk.BooleanVar(value=self.data["notifications"])
        notifications_check = tk.Checkbutton(settings_frame, text="Enable Notifications", 
                                            variable=self.notifications_var, 
                                            bg=self.colors["background"])
        notifications_check.grid(row=5, column=0, columnspan=2, sticky="w", pady=10)
        
        # Save button
        save_btn = tk.Button(settings_frame, text="Save Settings", command=self.save_settings, 
                            font=("Arial", 11, "bold"), bg=self.colors["primary"], fg="white", padx=15)
        save_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Data management frame
        data_frame = tk.LabelFrame(frame, text="Data Management", font=("Arial", 12, "bold"), 
                                  padx=20, pady=20, bg=self.colors["background"])
        data_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Backup data
        backup_btn = tk.Button(data_frame, text="Backup Data", command=self.backup_data, 
                              font=("Arial", 11), bg=self.colors["accent"], fg="white", padx=15)
        backup_btn.grid(row=0, column=0, pady=10, padx=10)
        
        # Restore data
        restore_btn = tk.Button(data_frame, text="Restore Data", command=self.restore_data, 
                               font=("Arial", 11), bg=self.colors["accent"], fg="white", padx=15)
        restore_btn.grid(row=0, column=1, pady=10, padx=10)
        
        # Export data
        export_btn = tk.Button(data_frame, text="Export to CSV", command=self.export_data, 
                              font=("Arial", 11), bg=self.colors["accent"], fg="white", padx=15)
        export_btn.grid(row=1, column=0, pady=10, padx=10)
        
        # Import data
        import_btn = tk.Button(data_frame, text="Import from CSV", command=self.import_data, 
                              font=("Arial", 11), bg=self.colors["accent"], fg="white", padx=15)
        import_btn.grid(row=1, column=1, pady=10, padx=10)
        
        # Reset data button with confirmation
        reset_frame = tk.Frame(data_frame, bg=self.colors["background"])
        reset_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        reset_btn = tk.Button(reset_frame, text="Reset All Data", command=self.confirm_reset_data, 
                             font=("Arial", 11), bg=self.colors["warning"], fg="white", padx=15)
        reset_btn.pack()
        
        # About section
        about_frame = tk.LabelFrame(frame, text="About", font=("Arial", 12, "bold"), 
                                   padx=20, pady=20, bg=self.colors["background"])
        about_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        
        about_text = "Poe Premium Credit Tracker\nVersion 2.0\nCreated by Dan\n\n" + \
                     "This application helps you track and manage your Poe Premium credits."
        about_label = tk.Label(about_frame, text=about_text, font=("Arial", 11), 
                              bg=self.colors["background"], justify=tk.LEFT)
        about_label.pack(pady=10)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=1)

    def update_dashboard_display(self):
        # Update summary labels
        self.total_label.config(text=f"{self.data['total_credits']:,}")
        self.remaining_label.config(text=f"{self.data['remaining_credits']:,}")
        
        used = self.data["total_credits"] - self.data["remaining_credits"]
        self.used_label.config(text=f"{used:,}")
        
        # Update progress bar
        usage_percentage = (used / self.data["total_credits"]) * 100
        self.progress_bar["value"] = usage_percentage
        self.progress_label.config(text=f"{usage_percentage:.1f}% Used")
        
        # Format next reset date
        next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d")
        self.reset_label.config(text=next_reset.strftime("%b %d, %Y"))
        
        # Calculate days until reset
        today = datetime.now().date()
        days_until_reset = (next_reset.date() - today).days
        self.days_remaining_label.config(text=str(days_until_reset))
        
        # Calculate averages
        days_in_month = calendar.monthrange(next_reset.year, next_reset.month)[1]
        daily_avg = self.data["total_credits"] / days_in_month
        self.daily_avg_label.config(text=f"{daily_avg:,.2f}")
        
        weekly_avg = daily_avg * 7
        self.weekly_avg_label.config(text=f"{weekly_avg:,.2f}")
        
        # Calculate extra credits available
        ideal_usage = self.calculate_ideal_usage(today)
        actual_usage = self.data["total_credits"] - self.data["remaining_credits"]
        extra_available = ideal_usage - actual_usage
        
        if extra_available > 0:
            self.extra_credits_label.config(text=f"{extra_available:,.2f}")
        else:
            self.extra_credits_label.config(text="0")
        
        # Update today's usage
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        today_usage = 0
        if today_str in self.data["daily_usage"]:
            today_usage = self.data["daily_usage"][today_str].get("used", 0)
        self.today_usage_label.config(text=f"{today_usage:,}")
        
        # Update yesterday's usage
        yesterday_usage = 0
        if yesterday_str in self.data["daily_usage"]:
            yesterday_usage = self.data["daily_usage"][yesterday_str].get("used", 0)
        self.yesterday_usage_label.config(text=f"{yesterday_usage:,}")
        
        # Calculate last 7 days average
        last_7_days = []
        for i in range(7):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if day in self.data["daily_usage"]:
                last_7_days.append(self.data["daily_usage"][day].get("used", 0))
        
        if last_7_days:
            week_avg = sum(last_7_days) / len(last_7_days)
            self.week_avg_usage_label.config(text=f"{week_avg:,.2f}")
        else:
            self.week_avg_usage_label.config(text="0")
        
        # Update status indicator
        status, color = self.get_usage_status(extra_available, daily_avg)
        
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline="")
        self.status_text.config(text=status)
        
        # Update graph
        self.update_dashboard_graph()
        
        # Update remaining credits entry with current value
        self.remaining_entry_var.set(str(self.data["remaining_credits"]))

    def update_dashboard_graph(self):
        self.fig.clear()
        
        # Create two subplots
        gs = self.fig.add_gridspec(1, 2, width_ratios=[2, 1])
        ax1 = self.fig.add_subplot(gs[0])
        ax2 = self.fig.add_subplot(gs[1])
        
        # Get the last 14 days of data
        today = datetime.now().date()
        dates = []
        usage_data = []
        remaining_data = []
        target_data = []
        
        # Calculate daily target
        next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d").date()
        days_in_month = calendar.monthrange(next_reset.year, next_reset.month)[1]
        daily_target = self.data["total_credits"] / days_in_month
        
        for i in range(13, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            dates.append(date)
            
            if date_str in self.data["daily_usage"]:
                entry = self.data["daily_usage"][date_str]
                usage_data.append(entry.get("used", 0))
                remaining_data.append(entry["remaining"])
            else:
                usage_data.append(0)
                # For remaining, use the last known value or total
                if remaining_data:
                    remaining_data.append(remaining_data[-1])
                else:
                    remaining_data.append(self.data["total_credits"])
            
            target_data.append(daily_target)
        
        # Plot 1: Daily usage vs target
        bar_colors = []
        for usage in usage_data:
            if usage > daily_target * 1.2:
                bar_colors.append(self.colors["danger"])
            elif usage > daily_target:
                bar_colors.append(self.colors["warning"])
            else:
                bar_colors.append(self.colors["good"])
        
        bars = ax1.bar([d.strftime("%m/%d") for d in dates], usage_data, color=bar_colors, alpha=0.7)
        ax1.axhline(y=daily_target, color='r', linestyle='--', alpha=0.7, label='Daily Target')
        
        # Add value labels to bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height + 5000,
                        f'{height:,.0f}', ha='center', va='bottom', rotation=90, fontsize=8)
        
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Credits Used')
        ax1.set_title('Daily Usage vs Target')
        ax1.legend()
        
        # Rotate x-axis labels for better readability
        ax1.set_xticklabels([d.strftime("%m/%d") for d in dates], rotation=45, ha='right')
        
        # Plot 2: Credits remaining
        remaining_percentage = (self.data["remaining_credits"] / self.data["total_credits"]) * 100
        
        # Create a pie chart for remaining credits
        if remaining_percentage <= self.data["low_credit_threshold"]:
            colors = [self.colors["danger"], '#e0e0e0']
        elif remaining_percentage <= 50:
            colors = [self.colors["warning"], '#e0e0e0']
        else:
            colors = [self.colors["good"], '#e0e0e0']
        
        ax2.pie([remaining_percentage, 100-remaining_percentage], 
               colors=colors, 
               startangle=90, 
               counterclock=False,
               wedgeprops={'width': 0.3, 'edgecolor': 'w'})
        
        # Add text in center
        ax2.text(0, 0, f"{remaining_percentage:.1f}%\nRemaining", 
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        ax2.set_title('Remaining Credits')
        ax2.axis('equal')
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Update canvas
        self.canvas.draw()

    def update_calendar_display(self):
        # Get current month and year
        year = self.current_calendar_date.year
        month = self.current_calendar_date.month
        
        # Update month/year label
        self.month_year_label.config(text=self.current_calendar_date.strftime("%B %Y"))
        
        # Get first day of month and number of days
        first_day = datetime(year, month, 1)
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Calculate daily target
        next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d")
        month_days = calendar.monthrange(next_reset.year, next_reset.month)[1]
        daily_target = self.data["total_credits"] / month_days
        
        # Clear all cells
        for row in self.calendar_cells:
            for cell in row:
                cell["frame"].config(bg="white")
                cell["date_label"].config(text="", bg="white")
                cell["usage_label"].config(text="", bg="white")
                cell["date"] = None
        
        # Calculate offset (0 = Monday in calendar.monthrange)
        first_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
        
        # Fill the calendar
        day = 1
        for row in range(6):
            for col in range(7):
                if (row == 0 and col < first_weekday) or day > days_in_month:
                    # Empty cell
                    continue
                
                # Set date
                date = datetime(year, month, day)
                date_str = date.strftime("%Y-%m-%d")
                
                cell = self.calendar_cells[row][col]
                cell["date"] = date_str
                cell["date_label"].config(text=str(day))
                
                # Check if we have data for this day
                if date_str in self.data["daily_usage"]:
                    entry = self.data["daily_usage"][date_str]
                    used = entry.get("used", 0)
                    
                    # Set usage text
                    cell["usage_label"].config(text=f"Used: {used:,}")
                    
                    # Color code based on usage vs target
                    if used > daily_target * 1.2:
                        bg_color = "#ffcccc"  # Light red
                    elif used > daily_target:
                        bg_color = "#fff2cc"  # Light yellow
                    else:
                        bg_color = "#d9f2d9"  # Light green
                    
                    cell["frame"].config(bg=bg_color)
                    cell["date_label"].config(bg=bg_color)
                    cell["usage_label"].config(bg=bg_color)
                
                # Highlight today
                if date.date() == datetime.now().date():
                    cell["date_label"].config(font=("Arial", 10, "bold"), fg="blue")
                
                # Highlight reset day
                if day == self.data["reset_day"]:
                    cell["date_label"].config(font=("Arial", 10, "bold"), fg="purple")
                
                # Bind click event
                cell["frame"].bind("<Button-1>", lambda e, d=date_str: self.select_calendar_day(d))
                cell["date_label"].bind("<Button-1>", lambda e, d=date_str: self.select_calendar_day(d))
                cell["usage_label"].bind("<Button-1>", lambda e, d=date_str: self.select_calendar_day(d))
                
                day += 1

    def select_calendar_day(self, date_str):
        # Update selected date
        self.selected_date_label.config(text=datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y"))
        
        # Calculate daily target
        next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d")
        days_in_month = calendar.monthrange(next_reset.year, next_reset.month)[1]
        daily_target = self.data["total_credits"] / days_in_month
        
        # Update day details
        if date_str in self.data["daily_usage"]:
            entry = self.data["daily_usage"][date_str]
            remaining = entry["remaining"]
            used = entry.get("used", 0)
            
            self.cal_remaining_label.config(text=f"{remaining:,}")
            self.cal_used_label.config(text=f"{used:,}")
            self.cal_target_label.config(text=f"{daily_target:,.2f}")
            
            # Update status
            if used > daily_target * 1.2:
                status = "Over Budget"
                color = self.colors["danger"]
            elif used > daily_target:
                status = "Warning"
                color = self.colors["warning"]
            else:
                status = "On Track"
                color = self.colors["good"]
            
            self.cal_status_indicator.delete("all")
            self.cal_status_indicator.create_oval(2, 2, 13, 13, fill=color, outline="")
            self.cal_status_text.config(text=status)
            
            # Update note
            if date_str in self.data.get("notes", {}):
                self.cal_note_text.delete(1.0, tk.END)
                self.cal_note_text.insert(tk.END, self.data["notes"][date_str])
            else:
                self.cal_note_text.delete(1.0, tk.END)
        else:
            self.cal_remaining_label.config(text="N/A")
            self.cal_used_label.config(text="N/A")
            self.cal_target_label.config(text=f"{daily_target:,.2f}")
            
            self.cal_status_indicator.delete("all")
            self.cal_status_text.config(text="No Data")
            
            self.cal_note_text.delete(1.0, tk.END)
            if date_str in self.data.get("notes", {}):
                self.cal_note_text.insert(tk.END, self.data["notes"][date_str])

    def prev_month(self):
        # Move to previous month
        year = self.current_calendar_date.year
        month = self.current_calendar_date.month
        
        if month == 1:
            self.current_calendar_date = datetime(year - 1, 12, 1)
        else:
            self.current_calendar_date = datetime(year, month - 1, 1)
        
        self.update_calendar_display()

    def next_month(self):
        # Move to next month
        year = self.current_calendar_date.year
        month = self.current_calendar_date.month
        
        if month == 12:
            self.current_calendar_date = datetime(year + 1, 1, 1)
        else:
            self.current_calendar_date = datetime(year, month + 1, 1)
        
        self.update_calendar_display()

    def save_day_note(self):
        # Get selected date
        selected_date = self.selected_date_label.cget("text")
        if selected_date == "None":
            messagebox.showwarning("No Date Selected", "Please select a date first.")
            return
        
        # Convert display date back to YYYY-MM-DD
        date_obj = datetime.strptime(selected_date, "%B %d, %Y")
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Get note text
        note = self.cal_note_text.get(1.0, tk.END).strip()
        
        # Initialize notes dict if it doesn't exist
        if "notes" not in self.data:
            self.data["notes"] = {}
        
        # Save note
        if note:
            self.data["notes"][date_str] = note
        else:
            # Remove note if empty
            if date_str in self.data["notes"]:
                del self.data["notes"][date_str]
        
        self.save_data()
        messagebox.showinfo("Note Saved", f"Note for {selected_date} has been saved.")

    def edit_day_usage(self):
        # Get selected date
        selected_date = self.selected_date_label.cget("text")
        if selected_date == "None":
            messagebox.showwarning("No Date Selected", "Please select a date first.")
            return
        
        # Convert display date back to YYYY-MM-DD
        date_obj = datetime.strptime(selected_date, "%B %d, %Y")
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Usage - {selected_date}")
        edit_window.geometry("300x200")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Center window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create form
        tk.Label(edit_window, text=f"Edit Usage for {selected_date}", font=("Arial", 12, "bold")).pack(pady=(10, 20))
        
        form_frame = tk.Frame(edit_window)
        form_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(form_frame, text="Remaining Credits:").grid(row=0, column=0, sticky="w", pady=5)
        remaining_var = tk.StringVar()
        
        if date_str in self.data["daily_usage"]:
            remaining_var.set(str(self.data["daily_usage"][date_str]["remaining"]))
        
        remaining_entry = tk.Entry(form_frame, textvariable=remaining_var, width=15)
        remaining_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # Buttons
        button_frame = tk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", 
                            command=lambda: self.save_edited_usage(date_str, remaining_var.get(), edit_window),
                            bg=self.colors["secondary"], fg="white", width=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=edit_window.destroy, width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button (if entry exists)
        if date_str in self.data["daily_usage"]:
            delete_btn = tk.Button(edit_window, text="Delete Entry", 
                                  command=lambda: self.delete_usage_entry(date_str, edit_window),
                                  bg=self.colors["warning"], fg="white")
            delete_btn.pack(pady=10)

    def save_edited_usage(self, date_str, remaining_str, window):
        try:
            remaining = int(remaining_str.replace(',', ''))
            
            # Calculate usage
            if date_str not in self.data["daily_usage"]:
                # First entry of the day
                prev_date = self.get_previous_date(date_str)
                if prev_date:
                    prev_remaining = self.data["daily_usage"][prev_date]["remaining"]
                    used_today = prev_remaining - remaining
                else:
                    # No previous data, assume starting from total
                    used_today = self.data["total_credits"] - remaining
            else:
                # Update existing entry
                prev_date = self.get_previous_date(date_str)
                if prev_date:
                    prev_remaining = self.data["daily_usage"][prev_date]["remaining"]
                    used_today = prev_remaining - remaining
                else:
                    # No previous data, calculate from total
                    used_today = self.data["total_credits"] - remaining
            
            # Update data
            self.data["daily_usage"][date_str] = {
                "remaining": remaining,
                "used": used_today,
                "date": date_str
            }
            
            # If this is the most recent entry, update remaining credits
            latest_date = max(self.data["daily_usage"].keys()) if self.data["daily_usage"] else None
            if latest_date == date_str:
                self.data["remaining_credits"] = remaining
            
            # Save and update displays
            self.save_data()
            self.update_dashboard_display()
            self.update_calendar_display()
            self.select_calendar_day(date_str)
            
            window.destroy()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for remaining credits")

    def delete_usage_entry(self, date_str, window):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the entry for {date_str}?"):
            if date_str in self.data["daily_usage"]:
                del self.data["daily_usage"][date_str]
                
                # Update remaining credits if this was the latest entry
                if self.data["daily_usage"]:
                    latest_date = max(self.data["daily_usage"].keys())
                    self.data["remaining_credits"] = self.data["daily_usage"][latest_date]["remaining"]
                else:
                    self.data["remaining_credits"] = self.data["total_credits"]
                
                self.save_data()
                self.update_dashboard_display()
                self.update_calendar_display()
                
                window.destroy()

    def update_history_display(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get daily target
        next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d")
        days_in_month = calendar.monthrange(next_reset.year, next_reset.month)[1]
        daily_target = self.data["total_credits"] / days_in_month
        
        # Filter by date range
        date_range = self.date_range_var.get()
        today = datetime.now().date()
        
        if date_range == "Current Month":
            start_date = datetime(today.year, today.month, 1).date()
            end_date = today
        elif date_range == "Previous Month":
            if today.month == 1:
                start_date = datetime(today.year - 1, 12, 1).date()
                end_date = datetime(today.year - 1, 12, 31).date()
            else:
                start_date = datetime(today.year, today.month - 1, 1).date()
                last_day = calendar.monthrange(today.year, today.month - 1)[1]
                end_date = datetime(today.year, today.month - 1, last_day).date()
        elif date_range == "Last 7 Days":
            start_date = today - timedelta(days=6)
            end_date = today
        elif date_range == "Last 30 Days":
            start_date = today - timedelta(days=29)
            end_date = today
        elif date_range == "Custom":
            try:
                start_date = datetime.strptime(self.from_date_var.get(), "%Y-%m-%d").date()
                end_date = datetime.strptime(self.to_date_var.get(), "%Y-%m-%d").date()
                
                # Show custom range frame
                self.custom_range_frame.pack(side=tk.LEFT)
            except ValueError:
                messagebox.showerror("Date Error", "Invalid date format. Use YYYY-MM-DD.")
                return
        else:  # All Time
            start_date = datetime(1900, 1, 1).date()
            end_date = today
            
            # Hide custom range frame
            self.custom_range_frame.pack_forget()
        
        # Filter by search text
        search_text = self.search_var.get().lower()
        
        # Sort dates and add to treeview
        sorted_dates = sorted(self.data["daily_usage"].keys(), 
                             key=lambda x: datetime.strptime(x, "%Y-%m-%d"), 
                             reverse=True)
        
        for date_str in sorted_dates:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Apply date filter
            if entry_date < start_date or entry_date > end_date:
                continue
            
            entry = self.data["daily_usage"][date_str]
            used = entry.get("used", 0)
            
            # Get note if exists
            note = self.data.get("notes", {}).get(date_str, "")
            
            # Apply search filter
            if search_text and search_text not in date_str.lower() and search_text not in note.lower():
                continue
            
            # Determine status
            if used > daily_target * 1.2:
                status = "Over Budget"
            elif used > daily_target:
                status = "Warning"
            else:
                status = "On Track"
            
            self.history_tree.insert("", "end", values=(
                date_str,
                f"{entry['remaining']:,}",
                f"{used:,}",
                f"{daily_target:,.2f}",
                status,
                note[:50] + ("..." if len(note) > 50 else "")
            ))

    def sort_history_by_column(self, column):
        # Get all items
        items = [(self.history_tree.set(item, column), item) for item in self.history_tree.get_children('')]
        
        # Sort items
        items.sort(reverse=True)
        
        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.history_tree.move(item, '', index)

    def edit_history_item(self, event=None):
        # Get selected item
        selected = self.history_tree.selection()
        if not selected:
            return
        
        # Get date from selected item
        date_str = self.history_tree.item(selected[0], "values")[0]
        
        # Convert to calendar date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Switch to calendar tab and select date
        self.tab_control.select(self.calendar_tab)
        
        # Set calendar to correct month
        self.current_calendar_date = datetime(date_obj.year, date_obj.month, 1)
        self.update_calendar_display()
        
        # Select the day
        self.select_calendar_day(date_str)
        
        # Open edit dialog
        self.edit_day_usage()

    def delete_history_item(self):
        # Get selected item
        selected = self.history_tree.selection()
        if not selected:
            return
        
        # Get date from selected item
        date_str = self.history_tree.item(selected[0], "values")[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the entry for {date_str}?"):
            if date_str in self.data["daily_usage"]:
                del self.data["daily_usage"][date_str]
                
                # Update remaining credits if this was the latest entry
                if self.data["daily_usage"]:
                    latest_date = max(self.data["daily_usage"].keys())
                    self.data["remaining_credits"] = self.data["daily_usage"][latest_date]["remaining"]
                else:
                    self.data["remaining_credits"] = self.data["total_credits"]
                
                self.save_data()
                self.update_dashboard_display()
                self.update_history_display()

    def add_history_note(self):
        # Get selected item
        selected = self.history_tree.selection()
        if not selected:
            return
        
        # Get date from selected item
        date_str = self.history_tree.item(selected[0], "values")[0]
        
        # Create note dialog
        note_window = tk.Toplevel(self.root)
        note_window.title(f"Add Note - {date_str}")
        note_window.geometry("400x250")
        note_window.resizable(False, False)
        note_window.transient(self.root)
        note_window.grab_set()
        
        # Center window
        note_window.update_idletasks()
        width = note_window.winfo_width()
        height = note_window.winfo_height()
        x = (note_window.winfo_screenwidth() // 2) - (width // 2)
        y = (note_window.winfo_screenheight() // 2) - (height // 2)
        note_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create form
        tk.Label(note_window, text=f"Add Note for {date_str}", font=("Arial", 12, "bold")).pack(pady=(10, 20))
        
        # Note text
        note_text = tk.Text(note_window, height=6, width=40, font=("Arial", 11), wrap=tk.WORD)
        note_text.pack(padx=20, fill=tk.X)
        
        # Get existing note if any
        if "notes" in self.data and date_str in self.data["notes"]:
            note_text.insert(tk.END, self.data["notes"][date_str])
        
        # Buttons
        button_frame = tk.Frame(note_window)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", 
                            command=lambda: self.save_history_note(date_str, note_text.get(1.0, tk.END).strip(), note_window),
                            bg=self.colors["secondary"], fg="white", width=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=note_window.destroy, width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def save_history_note(self, date_str, note, window):
        # Initialize notes dict if it doesn't exist
        if "notes" not in self.data:
            self.data["notes"] = {}
        
        # Save note
        if note:
            self.data["notes"][date_str] = note
        else:
            # Remove note if empty
            if date_str in self.data["notes"]:
                del self.data["notes"][date_str]
        
        self.save_data()
        self.update_history_display()
        window.destroy()

    def show_history_context_menu(self, event):
        # Get selected item
        selected = self.history_tree.identify_row(event.y)
        if not selected:
            return
        
        # Select the item
        self.history_tree.selection_set(selected)
        
        # Show context menu
        self.history_context_menu.post(event.x_root, event.y_root)

    def on_date_range_change(self, event):
        if self.date_range_var.get() == "Custom":
            self.custom_range_frame.pack(side=tk.LEFT)
        else:
            self.custom_range_frame.pack_forget()
            self.update_history_display()

    def export_history(self):
        import csv
        from tkinter import filedialog
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export History"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Date", "Remaining Credits", "Used Today", "Daily Target", "Status", "Note"])
                
                # Get daily target
                next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d")
                days_in_month = calendar.monthrange(next_reset.year, next_reset.month)[1]
                daily_target = self.data["total_credits"] / days_in_month
                
                # Sort dates
                sorted_dates = sorted(self.data["daily_usage"].keys(), 
                                     key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
                
                for date_str in sorted_dates:
                    entry = self.data["daily_usage"][date_str]
                    used = entry.get("used", 0)
                    
                    # Get note if exists
                    note = self.data.get("notes", {}).get(date_str, "")
                    
                    # Determine status
                    if used > daily_target * 1.2:
                        status = "Over Budget"
                    elif used > daily_target:
                        status = "Warning"
                    else:
                        status = "On Track"
                    
                    writer.writerow([
                        date_str,
                        entry['remaining'],
                        used,
                        f"{daily_target:.2f}",
                        status,
                        note
                    ])
            
            messagebox.showinfo("Export Successful", f"History exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {str(e)}")

    def update_analytics_display(self):
        chart_type = self.chart_type_var.get()
        time_range = self.chart_range_var.get()
        
        # Clear figure
        self.analytics_fig.clear()
        
        # Get date range
        today = datetime.now().date()
        
        if time_range == "Current Month":
            start_date = datetime(today.year, today.month, 1).date()
            end_date = today
        elif time_range == "Previous Month":
            if today.month == 1:
                start_date = datetime(today.year - 1, 12, 1).date()
                end_date = datetime(today.year - 1, 12, 31).date()
            else:
                start_date = datetime(today.year, today.month - 1, 1).date()
                last_day = calendar.monthrange(today.year, today.month - 1)[1]
                end_date = datetime(today.year, today.month - 1, last_day).date()
        elif time_range == "Last 30 Days":
            start_date = today - timedelta(days=29)
            end_date = today
        elif time_range == "Last 90 Days":
            start_date = today - timedelta(days=89)
            end_date = today
        else:  # All Time
            if self.data["daily_usage"]:
                earliest_date = min(datetime.strptime(d, "%Y-%m-%d").date() for d in self.data["daily_usage"].keys())
                start_date = earliest_date
                end_date = today
            else:
                start_date = today - timedelta(days=30)
                end_date = today
        
        # Get daily target
        next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d")
        days_in_month = calendar.monthrange(next_reset.year, next_reset.month)[1]
        daily_target = self.data["total_credits"] / days_in_month
        
        # Prepare data
        dates = []
        usage_data = []
        remaining_data = []
        
        # Create date range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(current_date)
            
            if date_str in self.data["daily_usage"]:
                entry = self.data["daily_usage"][date_str]
                usage_data.append(entry.get("used", 0))
                remaining_data.append(entry["remaining"])
            else:
                usage_data.append(0)
                
                # For remaining, use the last known value or total
                if remaining_data:
                    remaining_data.append(remaining_data[-1])
                elif current_date > start_date:
                    # Look for earlier entries
                    prev_date = current_date - timedelta(days=1)
                    while prev_date >= start_date:
                        prev_str = prev_date.strftime("%Y-%m-%d")
                        if prev_str in self.data["daily_usage"]:
                            remaining_data.append(self.data["daily_usage"][prev_str]["remaining"])
                            break
                        prev_date -= timedelta(days=1)
                    else:
                        remaining_data.append(self.data["total_credits"])
                else:
                    remaining_data.append(self.data["total_credits"])
            
            current_date += timedelta(days=1)
        
        # Create appropriate chart based on selection
        if chart_type == "Daily Usage":
            self.create_daily_usage_chart(dates, usage_data, daily_target)
        elif chart_type == "Usage vs Target":
            self.create_usage_vs_target_chart(dates, usage_data, daily_target)
        elif chart_type == "Remaining Credits":
            self.create_remaining_credits_chart(dates, remaining_data)
        elif chart_type == "Usage Heatmap":
            self.create_usage_heatmap(dates, usage_data, daily_target)
        
        # Update canvas
        self.analytics_canvas.draw()
        
        # Update statistics
        self.update_analytics_stats(dates, usage_data, remaining_data, daily_target)

    def create_daily_usage_chart(self, dates, usage_data, daily_target):
        ax = self.analytics_fig.add_subplot(111)
        
        # Create bar colors based on usage vs target
        bar_colors = []
        for usage in usage_data:
            if usage > daily_target * 1.2:
                bar_colors.append(self.colors["danger"])
            elif usage > daily_target:
                bar_colors.append(self.colors["warning"])
            else:
                bar_colors.append(self.colors["good"])
        
        # Plot bars
        bars = ax.bar([d.strftime("%m/%d") for d in dates], usage_data, color=bar_colors, alpha=0.8)
        
        # Add target line
        ax.axhline(y=daily_target, color='r', linestyle='--', alpha=0.7, label='Daily Target')
        
        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Credits Used')
        ax.set_title('Daily Credit Usage')
        
        # Add legend
        ax.legend()
        
        # Rotate x-axis labels for better readability
        if len(dates) > 10:
            # Show fewer x-ticks for readability
            step = max(1, len(dates) // 10)
            ax.set_xticks([d.strftime("%m/%d") for d in dates[::step]])
            ax.set_xticklabels([d.strftime("%m/%d") for d in dates[::step]], rotation=45, ha='right')
        else:
            ax.set_xticklabels([d.strftime("%m/%d") for d in dates], rotation=45, ha='right')
        
        # Adjust layout
        self.analytics_fig.tight_layout()

    def create_usage_vs_target_chart(self, dates, usage_data, daily_target):
        ax = self.analytics_fig.add_subplot(111)
        
        # Calculate cumulative usage
        cumulative_usage = np.cumsum(usage_data)
        
        # Calculate ideal usage line
        ideal_usage = [daily_target * (i+1) for i in range(len(dates))]
        
        # Plot lines
        ax.plot([d.strftime("%m/%d") for d in dates], cumulative_usage, 'b-', marker='o', 
               linewidth=2, label='Actual Usage')
        ax.plot([d.strftime("%m/%d") for d in dates], ideal_usage, 'r--', 
               linewidth=2, label='Target Usage')
        
        # Fill between
        ax.fill_between([d.strftime("%m/%d") for d in dates], cumulative_usage, ideal_usage, 
                       where=np.array(cumulative_usage) > np.array(ideal_usage), 
                       color=self.colors["danger"], alpha=0.3, interpolate=True)
        ax.fill_between([d.strftime("%m/%d") for d in dates], cumulative_usage, ideal_usage, 
                       where=np.array(cumulative_usage) <= np.array(ideal_usage), 
                       color=self.colors["good"], alpha=0.3, interpolate=True)
        
        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Credits Used')
        ax.set_title('Cumulative Usage vs Target')
        
        # Add legend
        ax.legend()
        
        # Rotate x-axis labels for better readability
        if len(dates) > 10:
            # Show fewer x-ticks for readability
            step = max(1, len(dates) // 10)
            ax.set_xticks([d.strftime("%m/%d") for d in dates[::step]])
            ax.set_xticklabels([d.strftime("%m/%d") for d in dates[::step]], rotation=45, ha='right')
        else:
            ax.set_xticklabels([d.strftime("%m/%d") for d in dates], rotation=45, ha='right')
        
        # Adjust layout
        self.analytics_fig.tight_layout()

    def create_remaining_credits_chart(self, dates, remaining_data):
        ax = self.analytics_fig.add_subplot(111)
        
        # Plot line
        ax.plot([d.strftime("%m/%d") for d in dates], remaining_data, 'b-', marker='o', 
               linewidth=2, label='Remaining Credits')
        
        # Add ideal remaining line
        total_credits = self.data["total_credits"]
        days_total = (datetime.strptime(self.data["next_reset"], "%Y-%m-%d").date() - 
                     datetime.strptime(self.data["next_reset"], "%Y-%m-%d").replace(day=1).date()).days + 1
        
        ideal_remaining = []
        for i, date in enumerate(dates):
            days_passed = (date - datetime.strptime(self.data["next_reset"], "%Y-%m-%d").replace(day=1).date()).days
            if days_passed < 0:
                ideal_remaining.append(total_credits)
            else:
                ideal_remaining.append(total_credits - (total_credits / days_total) * days_passed)
        
        ax.plot([d.strftime("%m/%d") for d in dates], ideal_remaining, 'r--', 
               linewidth=2, label='Ideal Remaining')
        
        # Fill between
        ax.fill_between([d.strftime("%m/%d") for d in dates], remaining_data, ideal_remaining, 
                       where=np.array(remaining_data) < np.array(ideal_remaining), 
                       color=self.colors["danger"], alpha=0.3, interpolate=True)
        ax.fill_between([d.strftime("%m/%d") for d in dates], remaining_data, ideal_remaining, 
                       where=np.array(remaining_data) >= np.array(ideal_remaining), 
                       color=self.colors["good"], alpha=0.3, interpolate=True)
        
        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Remaining Credits')
        ax.set_title('Remaining Credits Over Time')
        
        # Add legend
        ax.legend()
        
        # Rotate x-axis labels for better readability
        if len(dates) > 10:
            # Show fewer x-ticks for readability
            step = max(1, len(dates) // 10)
            ax.set_xticks([d.strftime("%m/%d") for d in dates[::step]])
            ax.set_xticklabels([d.strftime("%m/%d") for d in dates[::step]], rotation=45, ha='right')
        else:
            ax.set_xticklabels([d.strftime("%m/%d") for d in dates], rotation=45, ha='right')
        
        # Adjust layout
        self.analytics_fig.tight_layout()

    def create_usage_heatmap(self, dates, usage_data, daily_target):
        # Create month-based heatmap
        if not dates:
            # No data to display
            ax = self.analytics_fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data available for selected period", 
                   horizontalalignment='center', verticalalignment='center')
            return
        
        # Group data by month and day
        month_data = {}
        for i, date in enumerate(dates):
            month_key = date.strftime("%Y-%m")
            day = date.day
            
            if month_key not in month_data:
                month_data[month_key] = {}
            
            month_data[month_key][day] = usage_data[i]
        
        # Sort months
        sorted_months = sorted(month_data.keys())
        
        # Create a grid of subplots
        rows = (len(sorted_months) + 2) // 3  # 3 months per row
        cols = min(3, len(sorted_months))
        
        # Create figure with subplots
        for i, month_key in enumerate(sorted_months):
            ax = self.analytics_fig.add_subplot(rows, cols, i+1)
            
            # Get month data
            month_dict = month_data[month_key]
            
            # Create calendar grid
            year, month = map(int, month_key.split('-'))
            _, days_in_month = calendar.monthrange(year, month)
            
            first_day = datetime(year, month, 1).weekday()  # 0 = Monday, 6 = Sunday
            
            # Create 7x6 grid (weekdays x weeks)
            data = np.zeros((6, 7))
            data.fill(np.nan)  # Fill with NaN for empty cells
            
            # Fill in the data
            day = 1
            for week in range(6):
                for weekday in range(7):
                    if (week == 0 and weekday < first_day) or day > days_in_month:
                        continue
                    
                    if day in month_dict:
                        # Normalize by daily target for color coding
                        data[week, weekday] = month_dict[day] / daily_target
                    else:
                        data[week, weekday] = 0
                    
                    day += 1
            
            # Create heatmap
            cmap = plt.cm.RdYlGn_r  # Red for high usage, green for low
            im = ax.imshow(data, cmap=cmap, vmin=0, vmax=2)
            
            # Add day numbers to cells
            day = 1
            for week in range(6):
                for weekday in range(7):
                    if (week == 0 and weekday < first_day) or day > days_in_month:
                        day_text = ""
                    else:
                        day_text = str(day)
                        day += 1
                    
                    ax.text(weekday, week, day_text, ha='center', va='center', 
                           color='black' if not np.isnan(data[week, weekday]) and data[week, weekday] < 1.5 else 'white')
            
            # Set title and labels
            ax.set_title(datetime(year, month, 1).strftime("%B %Y"))
            ax.set_xticks(range(7))
            ax.set_xticklabels(['M', 'T', 'W', 'T', 'F', 'S', 'S'])
            ax.set_yticks([])
            
            # Remove axis
            for spine in ax.spines.values():
                spine.set_visible(False)
        
        # Add colorbar
        cbar_ax = self.analytics_fig.add_axes([0.92, 0.15, 0.02, 0.7])
        cbar = self.analytics_fig.colorbar(im, cax=cbar_ax)
        cbar.set_label('Usage Ratio (Actual/Target)')
        
        # Adjust layout
        self.analytics_fig.tight_layout(rect=[0, 0, 0.9, 1])

    def update_analytics_stats(self, dates, usage_data, remaining_data, daily_target):
        if not usage_data:
            # No data to analyze
            self.analytics_total_used.config(text="No data")
            self.analytics_avg_daily.config(text="No data")
            self.analytics_highest_day.config(text="No data")
            self.analytics_lowest_day.config(text="No data")
            self.analytics_over_target.config(text="No data")
            self.analytics_under_target.config(text="No data")
            self.analytics_projected_eom.config(text="No data")
            self.analytics_projected_usage.config(text="No data")
            self.analytics_recommended.config(text="No data")
            return
        
        # Calculate statistics
        total_used = sum(usage_data)
        self.analytics_total_used.config(text=f"{total_used:,}")
        
        avg_daily = total_used / len([u for u in usage_data if u > 0]) if any(usage_data) else 0
        self.analytics_avg_daily.config(text=f"{avg_daily:,.2f}")
        
        # Find highest and lowest usage days
        if any(usage_data):
            max_index = usage_data.index(max(usage_data))
            min_index = next((i for i, u in enumerate(usage_data) if u > 0), 0)
            for i, u in enumerate(usage_data):
                if u > 0 and u < usage_data[min_index]:
                    min_index = i
            
            self.analytics_highest_day.config(
                text=f"{dates[max_index].strftime('%Y-%m-%d')} ({usage_data[max_index]:,})")
            self.analytics_lowest_day.config(
                text=f"{dates[min_index].strftime('%Y-%m-%d')} ({usage_data[min_index]:,})")
        else:
            self.analytics_highest_day.config(text="No usage data")
            self.analytics_lowest_day.config(text="No usage data")
        
        # Count days over/under target
        days_over = sum(1 for u in usage_data if u > daily_target)
        days_under = sum(1 for u in usage_data if 0 < u <= daily_target)
        
        self.analytics_over_target.config(text=str(days_over))
        self.analytics_under_target.config(text=str(days_under))
        
        # Calculate projections
        if remaining_data:
            # Get days until reset
            today = datetime.now().date()
            next_reset = datetime.strptime(self.data["next_reset"], "%Y-%m-%d").date()
            days_until_reset = (next_reset - today).days
            
            if days_until_reset > 0:
                # Calculate recent average daily usage (last 7 days or all if less)
                recent_usage = [u for u in usage_data[-7:] if u > 0]
                if recent_usage:
                    recent_avg = sum(recent_usage) / len(recent_usage)
                    projected_usage = recent_avg * days_until_reset
                    projected_remaining = remaining_data[-1] - projected_usage
                    
                    if projected_remaining < 0:
                        projected_remaining = 0
                    
                    self.analytics_projected_eom.config(text=f"{projected_remaining:,.0f}")
                    self.analytics_projected_usage.config(text=f"{(total_used + projected_usage):,.0f}")
                    
                    # Calculate recommended daily limit
                    recommended = remaining_data[-1] / days_until_reset
                    self.analytics_recommended.config(text=f"{recommended:,.2f}")
                else:
                    self.analytics_projected_eom.config(text="Insufficient data")
                    self.analytics_projected_usage.config(text="Insufficient data")
                    self.analytics_recommended.config(text=f"{daily_target:,.2f}")
            else:
                self.analytics_projected_eom.config(text=f"{remaining_data[-1]:,.0f}")
                self.analytics_projected_usage.config(text=f"{total_used:,.0f}")
                self.analytics_recommended.config(text="Reset day reached")
        else:
            self.analytics_projected_eom.config(text="No data")
            self.analytics_projected_usage.config(text="No data")
            self.analytics_recommended.config(text="No data")

    def update_usage(self):
        try:
            date_str = self.date_var.get()
            remaining = int(self.remaining_entry_var.get().replace(',', ''))
            note = self.note_entry_var.get().strip()
            
            # Validate date format
            date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Calculate usage
            if date_str not in self.data["daily_usage"]:
                # First entry of the day
                prev_date = self.get_previous_date(date_str)
                if prev_date:
                    prev_remaining = self.data["daily_usage"][prev_date]["remaining"]
                    used_today = prev_remaining - remaining
                else:
                    # No previous data, assume starting from total
                    used_today = self.data["total_credits"] - remaining
            else:
                # Update existing entry
                prev_date = self.get_previous_date(date_str)
                if prev_date:
                    prev_remaining = self.data["daily_usage"][prev_date]["remaining"]
                    used_today = prev_remaining - remaining
                else:
                    # No previous data, calculate from total
                    used_today = self.data["total_credits"] - remaining
            
            # Update data
            self.data["daily_usage"][date_str] = {
                "remaining": remaining,
                "used": used_today,
                "date": date_str
            }
            
            self.data["remaining_credits"] = remaining
            self.data["last_updated"] = date_str
            
            # Save note if provided
            if note:
                if "notes" not in self.data:
                    self.data["notes"] = {}
                self.data["notes"][date_str] = note
            
            # Save and update display
            self.save_data()
            self.update_dashboard_display()
            
            # Clear note field
            self.note_entry_var.set("")
            
            messagebox.showinfo("Success", f"Usage updated for {date_str}")
            
        except ValueError as e:
            messagebox.showerror("Input Error", "Please enter valid date (YYYY-MM-DD) and numeric values for credits")

    def get_previous_date(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        prev_date = date - timedelta(days=1)
        prev_date_str = prev_date.strftime("%Y-%m-%d")
        
        if prev_date_str in self.data["daily_usage"]:
            return prev_date_str
        
        # If no direct previous day, find the most recent date before this one
        dates = sorted([d for d in self.data["daily_usage"].keys() 
                       if datetime.strptime(d, "%Y-%m-%d") < date])
        
        if dates:
            return dates[-1]  # Return the most recent date
        
        return None

    def calculate_ideal_usage(self, current_date):
        # Calculate how much should have been used by current date
        reset_day = self.data["reset_day"]
        
        # Get the start of the current period
        if current_date.day < reset_day:
            # We're before the reset day, so the period started in the previous month
            if current_date.month == 1:
                period_start = datetime(current_date.year - 1, 12, reset_day)
            else:
                period_start = datetime(current_date.year, current_date.month - 1, reset_day)
        else:
            # We're after the reset day, so the period started this month
            period_start = datetime(current_date.year, current_date.month, reset_day)
        
        # Calculate days passed in the period
        days_passed = (current_date - period_start.date()).days
        
        # Calculate next reset date
        if current_date.day < reset_day:
            next_reset = datetime(current_date.year, current_date.month, reset_day)
        else:
            if current_date.month == 12:
                next_reset = datetime(current_date.year + 1, 1, reset_day)
            else:
                next_reset = datetime(current_date.year, current_date.month + 1, reset_day)
        
        # Calculate total days in period
        total_days = (next_reset.date() - period_start.date()).days
        
        # Calculate ideal usage
        ideal_usage = (self.data["total_credits"] / total_days) * days_passed
        
        return ideal_usage

    def get_usage_status(self, extra_available, daily_target):
        if extra_available < -daily_target * 5:
            return "Critical", self.colors["danger"]
        elif extra_available < 0:
            return "Over Budget", self.colors["warning"]
        elif extra_available < daily_target * 3:
            return "On Track", self.colors["good"]
        else:
            return "Under Budget", "#3f51b5"  # Indigo

    def show_calendar_picker(self):
        # Create a toplevel window
        top = tk.Toplevel(self.root)
        top.title("Select Date")
        top.geometry("300x250")
        top.transient(self.root)
        top.grab_set()
        
        # Center window
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add calendar
        current_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d") if self.date_var.get() else datetime.now()
        cal = Calendar(top, selectmode='day', year=current_date.year, month=current_date.month, day=current_date.day)
        cal.pack(padx=10, pady=10)
        
        # Add button
        def set_date():
            selected_date = cal.selection_get()
            self.date_var.set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()
        
        button = tk.Button(top, text="Select", command=set_date, bg=self.colors["primary"], fg="white")
        button.pack(pady=10)

    def save_settings(self):
        try:
            total_credits = int(self.total_credits_var.get().replace(',', ''))
            reset_day = int(self.reset_day_var.get())
            threshold = int(self.threshold_var.get())
            
            # Validate reset day
            if reset_day < 1 or reset_day > 31:
                messagebox.showerror("Input Error", "Reset day must be between 1 and 31")
                return
            
            # Validate threshold
            if threshold < 0 or threshold > 100:
                messagebox.showerror("Input Error", "Low credit threshold must be between 0 and 100")
                return
            
            # Update data
            self.data["total_credits"] = total_credits
            self.data["reset_day"] = reset_day
            self.data["low_credit_threshold"] = threshold
            self.data["theme"] = self.theme_var.get()
            self.data["show_projections"] = self.show_projections_var.get()
            self.data["notifications"] = self.notifications_var.get()
            
            # Recalculate next reset date
            today = datetime.now()
            if today.day <= reset_day:
                next_reset = datetime(today.year, today.month, reset_day)
            else:
                if today.month == 12:
                    next_reset = datetime(today.year + 1, 1, reset_day)
                else:
                    next_reset = datetime(today.year, today.month + 1, reset_day)
            
            self.data["next_reset"] = next_reset.strftime("%Y-%m-%d")
            
            # Save and update display
            self.save_data()
            self.update_dashboard_display()
            
            # Apply theme changes
            self.apply_theme()
            
            messagebox.showinfo("Success", "Settings updated successfully")
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values")

    def apply_theme(self):
        # Apply theme colors based on settings
        if self.data["theme"] == "dark":
            self.colors = {
                "primary": "#2196F3",  # Blue
                "secondary": "#4CAF50",  # Green
                "accent": "#FF9800",  # Orange
                "warning": "#f44336",  # Red
                "background": "#333333",  # Dark gray
                "text": "#f5f5f5",  # Light gray
                "good": "#4CAF50",  # Green
                "warning": "#FF9800",  # Orange
                "danger": "#f44336",  # Red
            }
        else:
            self.colors = {
                "primary": "#2196F3",  # Blue
                "secondary": "#4CAF50",  # Green
                "accent": "#FF9800",  # Orange
                "warning": "#f44336",  # Red
                "background": "#f5f5f5",  # Light gray
                "text": "#333333",  # Dark gray
                "good": "#4CAF50",  # Green
                "warning": "#FF9800",  # Orange
                "danger": "#f44336",  # Red
            }
        
        # Update UI colors (would need to update all widgets)
        # This is a simplified version - a full implementation would update all widgets
        self.root.configure(bg=self.colors["background"])

    def confirm_reset_data(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data? This cannot be undone."):
            self.reset_data()

    def reset_data(self):
        # Keep settings but reset usage data
        today = datetime.now()
        reset_day = self.data["reset_day"]
        
        # Calculate next reset date
        if today.day <= reset_day:
            next_reset = datetime(today.year, today.month, reset_day)
        else:
            if today.month == 12:
                next_reset = datetime(today.year + 1, 1, reset_day)
            else:
                next_reset = datetime(today.year, today.month + 1, reset_day)
        
        # Save settings before reset
        settings = {
            "total_credits": self.data["total_credits"],
            "reset_day": reset_day,
            "theme": self.data.get("theme", "light"),
            "show_projections": self.data.get("show_projections", True),
            "notifications": self.data.get("notifications", True),
            "low_credit_threshold": self.data.get("low_credit_threshold", 20)
        }
        
        # Reset data
        self.data = {
            "total_credits": settings["total_credits"],
            "remaining_credits": settings["total_credits"],
            "reset_day": settings["reset_day"],
            "next_reset": next_reset.strftime("%Y-%m-%d"),
            "daily_usage": {},
            "last_updated": today.strftime("%Y-%m-%d"),
            "theme": settings["theme"],
            "show_projections": settings["show_projections"],
            "notifications": settings["notifications"],
            "low_credit_threshold": settings["low_credit_threshold"],
            "notes": {}
        }
        
        self.save_data()
        self.update_dashboard_display()
        self.update_calendar_display()
        
        messagebox.showinfo("Success", "All data has been reset")

    def backup_data(self):
        from tkinter import filedialog
        import shutil
        
        # Ask for backup location
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Backup Data"
        )
        
        if not backup_path:
            return
        
        try:
            # Copy the data file to backup location
            shutil.copy2(self.data_file, backup_path)
            messagebox.showinfo("Backup Successful", f"Data backed up to {backup_path}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"An error occurred: {str(e)}")

    def restore_data(self):
        from tkinter import filedialog
        import shutil
        
        # Ask for backup file
        backup_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Restore Data"
        )
        
        if not backup_path:
            return
        
        try:
            # Validate the backup file
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
                
                # Check if it has the required fields
                required_fields = ["total_credits", "remaining_credits", "reset_day", "next_reset"]
                if not all(field in backup_data for field in required_fields):
                    messagebox.showerror("Invalid Backup", "The selected file is not a valid backup.")
                    return
            
            # Confirm restore
            if messagebox.askyesno("Confirm Restore", "This will overwrite your current data. Continue?"):
                # Copy the backup file to data file location
                shutil.copy2(backup_path, self.data_file)
                
                # Reload data
                self.load_data()
                self.update_dashboard_display()
                self.update_calendar_display()
                
                messagebox.showinfo("Restore Successful", "Data has been restored from backup.")
        except Exception as e:
            messagebox.showerror("Restore Error", f"An error occurred: {str(e)}")

    def export_data(self):
        import csv
        from tkinter import filedialog
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Data"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Date", "Remaining Credits", "Used Today", "Note"])
                
                # Sort dates
                sorted_dates = sorted(self.data["daily_usage"].keys(), 
                                     key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
                
                for date_str in sorted_dates:
                    entry = self.data["daily_usage"][date_str]
                    used = entry.get("used", 0)
                    
                    # Get note if exists
                    note = self.data.get("notes", {}).get(date_str, "")
                    
                    writer.writerow([
                        date_str,
                        entry['remaining'],
                        used,
                        note
                    ])
            
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {str(e)}")

    def import_data(self):
        import csv
        from tkinter import filedialog
        
        # Ask for file location
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Data"
        )
        
        if not file_path:
            return
        
        try:
            # Confirm import
            if not messagebox.askyesno("Confirm Import", 
                                      "This will add the imported data to your current data. Continue?"):
                return
            
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip header
                next(reader)
                
                # Initialize notes dict if it doesn't exist
                if "notes" not in self.data:
                    self.data["notes"] = {}
                
                # Read data
                for row in reader:
                    if len(row) >= 3:
                        date_str = row[0]
                        try:
                            remaining = int(row[1])
                            used = int(row[2])
                            
                            # Add to data
                            self.data["daily_usage"][date_str] = {
                                "remaining": remaining,
                                "used": used,
                                "date": date_str
                            }
                            
                            # Add note if exists
                            if len(row) >= 4 and row[3]:
                                self.data["notes"][date_str] = row[3]
                            
                            # Update remaining credits if this is the latest entry
                            latest_date = max(self.data["daily_usage"].keys()) if self.data["daily_usage"] else None
                            if latest_date == date_str:
                                self.data["remaining_credits"] = remaining
                                
                        except ValueError:
                            continue
            
            # Save and update displays
            self.save_data()
            self.update_dashboard_display()
            self.update_calendar_display()
            
            messagebox.showinfo("Import Successful", "Data has been imported successfully.")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PoeTracker(root)
    root.mainloop()
