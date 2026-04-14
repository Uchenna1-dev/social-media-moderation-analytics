import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd
from datetime import datetime

#Constants 
BACKUP_PATH = "output/backup.json"
AUDIT_PATH  = "output/audit_log.json"

#Load Data
def load_data():
    """Load cleaned data from JSON backup."""
    if not os.path.exists(BACKUP_PATH):
        return None
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_dataframes(data):
    """Flatten JSON structure back into DataFrames for analysis."""
    users = pd.DataFrame([
        {k: v for k, v in u.items() if k != "posts"}
        for u in data["users"]
    ])

    posts_list = []
    interactions_list = []

    for user in data["users"]:
        for post in user.get("posts", []):
            post_data = {k: v for k, v in post.items() if k != "interactions"}
            posts_list.append(post_data)
            for interaction in post.get("interactions", []):
                interaction["post_id"] = post["post_id"]
                interactions_list.append(interaction)

    posts        = pd.DataFrame(posts_list)
    interactions = pd.DataFrame(interactions_list)

    return users, posts, interactions

def log_gui_action(action, detail):
    """Append a GUI action to the audit log file."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "detail": detail,
        "source": "GUI"
    }
    log = []
    if os.path.exists(AUDIT_PATH):
        with open(AUDIT_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)
    log.append(entry)
    with open(AUDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

#Main Application
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Moderation Analytics")
        self.geometry("900x650")
        self.resizable(True, True)
        self.data        = None
        self.users       = None
        self.posts       = None
        self.interactions = None
        self._build_ui()

    def _build_ui(self):
        """Build the main tabbed interface."""
        # Header
        header = tk.Frame(self, bg="#2c3e50", pady=10)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Social Media Moderation Analytics",
            bg="#2c3e50", fg="white",
            font=("Arial", 16, "bold")
        ).pack()

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_load      = ttk.Frame(self.notebook)
        self.tab_stats     = ttk.Frame(self.notebook)
        self.tab_audit     = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_load,  text="  Load Data  ")
        self.notebook.add(self.tab_stats, text="  Statistics  ")
        self.notebook.add(self.tab_audit, text="  Audit Log  ")

        self._build_load_tab()
        self._build_stats_tab()
        self._build_audit_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready — please load data to begin.")
        status_bar = tk.Label(
            self, textvariable=self.status_var,
            anchor="w", bg="#ecf0f1",
            font=("Arial", 9), pady=4, padx=8
        )
        status_bar.pack(fill="x", side="bottom")

    #Tab 1: Load Data
    def _build_load_tab(self):
        frame = ttk.LabelFrame(self.tab_load, text="Data Management", padding=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(
            frame,
            text="Load the cleaned dataset from the JSON backup produced by the notebook.",
            wraplength=600
        ).pack(pady=(0, 15))

        ttk.Button(
            frame,
            text="Load Data from Backup",
            command=self._load_data
        ).pack(pady=5)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)

        ttk.Label(frame, text="Dataset Summary", font=("Arial", 11, "bold")).pack(anchor="w")

        self.summary_text = tk.Text(frame, height=12, state="disabled",
                                     font=("Courier", 10), bg="#f8f9fa")
        self.summary_text.pack(fill="both", expand=True, pady=5)

    def _load_data(self):
        """Load JSON backup and populate dataframes."""
        self.data = load_data()
        if self.data is None:
            messagebox.showerror(
                "Error",
                f"No backup found at {BACKUP_PATH}.\n"
                "Please run the notebook first to generate the backup."
            )
            self.status_var.set("Error: backup not found.")
            return

        self.users, self.posts, self.interactions = build_dataframes(self.data)
        log_gui_action("LOAD", "Data loaded from JSON backup via GUI")

        meta = self.data["metadata"]
        summary = (
            f"Data loaded successfully ✓\n\n"
            f"  Created:        {meta['created']}\n"
            f"  Total users:    {meta['total_users']}\n"
            f"  Total posts:    {meta['total_posts']}\n"
            f"  Total interactions: {meta['total_interactions']}\n"
            f"  Total topics:   {meta['total_topics']}\n\n"
            f"  Account types:\n"
        )

        for acc_type, count in self.users['account_type'].value_counts().items():
            summary += f"    {acc_type}: {count}\n"

        summary += f"\n  Interaction types:\n"
        for i_type, count in self.interactions['interaction_type'].value_counts().items():
            summary += f"    {i_type}: {count}\n"

        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", summary)
        self.summary_text.config(state="disabled")

        self.status_var.set("Data loaded successfully ✓")
        messagebox.showinfo("Success", "Data loaded successfully!")

    #Tab 2: Statistics
    def _build_stats_tab(self):
        frame = ttk.LabelFrame(self.tab_stats, text="Engagement Statistics", padding=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(
            frame,
            text="Select an engagement metric to calculate mean, mode and median.",
            wraplength=600
        ).pack(pady=(0, 10))

        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", pady=5)

        ttk.Label(control_frame, text="Metric:").pack(side="left", padx=(0, 8))

        self.metric_var = tk.StringVar(value="like")
        metric_dropdown = ttk.Combobox(
            control_frame,
            textvariable=self.metric_var,
            values=["like", "comment", "share", "save", "report"],
            state="readonly",
            width=15
        )
        metric_dropdown.pack(side="left", padx=(0, 15))

        ttk.Button(
            control_frame,
            text="Calculate",
            command=self._calculate_stats
        ).pack(side="left")

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        self.stats_text = tk.Text(frame, height=15, state="disabled",
                                   font=("Courier", 11), bg="#f8f9fa")
        self.stats_text.pack(fill="both", expand=True)

    def _calculate_stats(self):
        """Calculate mean, mode, median for selected engagement metric."""
        if self.interactions is None:
            messagebox.showwarning("No Data", "Please load data first.")
            return

        metric = self.metric_var.get()

        # Filter for selected metric and count per post
        filtered = self.interactions[
            self.interactions['interaction_type'] == metric
        ]
        counts = filtered.groupby('post_id').size()

        # Include posts with zero interactions
        all_posts = self.posts['post_id'].unique()
        counts = counts.reindex(all_posts, fill_value=0)

        mean   = round(counts.mean(), 2)
        median = round(counts.median(), 2)
        mode   = round(counts.mode().iloc[0], 2)
        total  = int(counts.sum())
        max_v  = int(counts.max())
        min_v  = int(counts.min())

        result = (
            f"Engagement Statistics — {metric.upper()}\n"
            f"{'─' * 40}\n\n"
            f"  Mean:    {mean}\n"
            f"  Median:  {median}\n"
            f"  Mode:    {mode}\n\n"
            f"{'─' * 40}\n"
            f"  Total {metric}s:  {total}\n"
            f"  Max per post:    {max_v}\n"
            f"  Min per post:    {min_v}\n"
            f"  Posts analysed:  {len(counts)}\n"
        )

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", result)
        self.stats_text.config(state="disabled")

        log_gui_action("STATS", f"Statistics calculated for metric: {metric}")
        self.status_var.set(f"Statistics calculated for: {metric}")

    #Tab 3: Audit Log
    def _build_audit_tab(self):
        frame = ttk.LabelFrame(self.tab_audit, text="Audit Log", padding=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(
            frame,
            text="Complete record of all data transformations and analysis decisions.",
            wraplength=600
        ).pack(pady=(0, 10))

        ttk.Button(
            frame,
            text="Refresh Audit Log",
            command=self._load_audit_log
        ).pack(pady=5)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        # Treeview for audit log
        columns = ("timestamp", "action", "detail", "records")
        self.audit_tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)

        self.audit_tree.heading("timestamp", text="Timestamp")
        self.audit_tree.heading("action",    text="Action")
        self.audit_tree.heading("detail",    text="Detail")
        self.audit_tree.heading("records",   text="Records")

        self.audit_tree.column("timestamp", width=160)
        self.audit_tree.column("action",    width=120)
        self.audit_tree.column("detail",    width=400)
        self.audit_tree.column("records",   width=80)

        scrollbar = ttk.Scrollbar(frame, orient="vertical",
                                   command=self.audit_tree.yview)
        self.audit_tree.configure(yscrollcommand=scrollbar.set)

        self.audit_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _load_audit_log(self):
        """Load and display the audit log."""
        if not os.path.exists(AUDIT_PATH):
            messagebox.showwarning("No Log", "No audit log found. Run the notebook first.")
            return

        with open(AUDIT_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)

        # Clear existing rows
        for row in self.audit_tree.get_children():
            self.audit_tree.delete(row)

        # Populate treeview
        for entry in log:
            self.audit_tree.insert("", "end", values=(
                entry.get("timestamp", ""),
                entry.get("action", ""),
                entry.get("detail", ""),
                entry.get("records_affected", "")
            ))

        self.status_var.set(f"Audit log loaded — {len(log)} entries")
        log_gui_action("VIEW", "Audit log viewed via GUI")

#Entry Poin
if __name__ == "__main__":
    app = App()
    app.mainloop()