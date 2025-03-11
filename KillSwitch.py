import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
import socket
import subprocess
import re
import platform
from threading import Thread
import time

class KillSwitch:
    def __init__(self, root):
        self.root = root
        self.root.title("KillSwitch - Operation Blackout")
        self.root.geometry("1250x600")
        self.root.configure(bg='black')  # Main window background
        self.root.resizable(False, False)
        
        # Configure a "dark hacker" style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # General style settings for frames, labels, buttons, etc.
        self.style.configure("TFrame", background="black")
        self.style.configure("TLabel", background="black", foreground="lime", font=("Courier", 10))
        self.style.configure("TButton", background="black", foreground="lime", font=("Courier", 10))
        self.style.configure(
            "Treeview",
            background="black",
            fieldbackground="black",
            foreground="lime",
            font=("Courier", 10)
        )
        self.style.configure(
            "Treeview.Heading",
            background="black",
            foreground="cyan",
            font=("Courier", 10, "bold")
        )
        
        # Status and version
        self.status = "Idle"
        self.version = "1.0"
        
        self.credentials = {'username': 'admin', 'password': 'your_password'}  # Replace with actual credentials
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container frames
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left section (ASCII art + TreeView + Buttons)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(0,10))

        # Right section (Time, Status, Version)
        right_frame = ttk.Frame(main_frame, width=200)
        right_frame.pack(side=tk.RIGHT, fill='y')
        right_frame.pack_propagate(False)

        # --- TOP: ASCII Art ---
        ascii_art = (
            "                                                                                                                               \n"
            "88      a8P   88  88           88           ad88888ba   I8,        8        ,8I  88  888888888888  ,ad8888ba,   88        88  \n"
            "88    ,88'    88  88           88          d8\"     \"8b  `8b       d8b       d8'  88       88      d8\"'    `\"8b  88        88  \n"
            "88  ,88\"      88  88           88          Y8,           \"8,     ,8\"8,     ,8\"   88       88     d8'            88        88  \n"
            "88,d88'       88  88           88          `Y8aaaaa,      Y8     8P Y8     8P    88       88     88             88aaaaaaaa88  \n"
            "8888\"88,      88  88           88            `\"\"\"\"\"8b,    `8b   d8' `8b   d8'    88       88     88             88\"\"\"\"\"\"\"\"88  \n"
            "88P   Y8b     88  88           88                  `8b     `8a a8'   `8a a8'     88       88     Y8,            88        88  \n"
            "88     \"88,   88  88           88          Y8a     a8P      `8a8'     `8a8'      88       88      Y8a.    .a8P  88        88  \n"
            "88       Y8b  88  88888888888  88888888888  \"Y88888P\"        `8'       `8'       88       88       `\"Y8888Y\"'   88        88  \n"
            "                                                                                                                               "
        )
        ascii_label = tk.Label(left_frame, text=ascii_art, bg='black', fg='lime', font=("Courier", 8))
        ascii_label.pack(pady=(0,10))

        # --- MIDDLE: TreeView ---
        self.device_tree = ttk.Treeview(
            left_frame,
            columns=('IP', 'Hostname', 'Manufacturer', 'Model', 'OS'),
            show='headings'
        )
        
        self.device_tree.heading('IP', text='IP Address')
        self.device_tree.heading('Hostname', text='Hostname')
        self.device_tree.heading('Manufacturer', text='Manufacturer')
        self.device_tree.heading('Model', text='Model')
        self.device_tree.heading('OS', text='OS Type')
        
        self.device_tree.column('IP', width=120)
        self.device_tree.column('Hostname', width=150)
        self.device_tree.column('Manufacturer', width=150)
        self.device_tree.column('Model', width=150)
        self.device_tree.column('OS', width=100)
        
        self.device_tree.pack(fill='both', expand=True)

        # --- BOTTOM: Buttons ---
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Scan Network", command=self.start_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Force Shutdown", command=self.initiate_shutdown).pack(side=tk.LEFT, padx=5)

        # --- RIGHT FRAME: Info labels ---
        self.time_label = tk.Label(right_frame, text="", bg='black', fg='lime', font=("Courier", 10))
        self.time_label.pack(pady=10)

        self.status_label = tk.Label(right_frame, text=f"Status: {self.status}", bg='black', fg='lime', font=("Courier", 10))
        self.status_label.pack(pady=10)

        self.version_label = tk.Label(right_frame, text=f"Version: {self.version}", bg='black', fg='lime', font=("Courier", 10))
        self.version_label.pack(pady=10)

        # Begin updating local time display
        self.update_time()

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=f"Local Time:\n{current_time}")
        self.root.after(1000, self.update_time)

    def start_scan(self):
        self.status = "Scanning..."
        self.status_label.config(text=f"Status: {self.status}")
        Thread(target=self.scan_network).start()

    def scan_network(self):
        self.device_tree.delete(*self.device_tree.get_children())
        local_ip = socket.gethostbyname(socket.gethostname())
        network_prefix = '.'.join(local_ip.split('.')[:3]) + '.'

        try:
            arp_command = ['arp', '-a'] if platform.system() == 'Windows' else ['arp', '-n']
            result = subprocess.run(arp_command, capture_output=True, text=True)
            ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

            for line in result.stdout.split('\n'):
                ip_match = re.search(ip_pattern, line)
                if ip_match and ip_match.group(0).startswith(network_prefix):
                    ip = ip_match.group(0)
                    Thread(target=self.get_device_details, args=(ip,)).start()

            self.status = "Idle"
            self.status_label.config(text=f"Status: {self.status}")
        except Exception as e:
            self.status = "Error"
            self.status_label.config(text=f"Status: {self.status}")
            messagebox.showerror("Error", f"Scan failed: {str(e)}")

    def get_device_details(self, ip):
        try:
            manufacturer, model = self.get_windows_hardware_info(ip)
            os_type = "Windows"
        except Exception:
            try:
                manufacturer, model = self.get_linux_hardware_info(ip)
                os_type = "Linux"
            except Exception:
                manufacturer, model = "Unknown", "Unknown"
                os_type = "Unknown"

        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = "Unknown"

        self.device_tree.insert('', 'end', values=(ip, hostname, manufacturer, model, os_type))

    def get_windows_hardware_info(self, ip):
        command = f"wmic /node:{ip} computersystem get manufacturer,model /value"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        manufacturer = re.search(r'Manufacturer=(.+)', result.stdout).group(1).strip()
        model = re.search(r'Model=(.+)', result.stdout).group(1).strip()
        return manufacturer, model

    def get_linux_hardware_info(self, ip):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=self.credentials['username'], password=self.credentials['password'])
        
        stdin, stdout, stderr = ssh.exec_command("sudo dmidecode -s system-manufacturer")
        manufacturer = stdout.read().decode().strip()
        
        stdin, stdout, stderr = ssh.exec_command("sudo dmidecode -s system-product-name")
        model = stdout.read().decode().strip()
        
        ssh.close()
        return manufacturer, model

    def initiate_shutdown(self):
        selected = self.device_tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a device first")
            return

        item = self.device_tree.item(selected[0])
        ip, _, _, _, os_type = item['values']
        
        try:
            if os_type == "Windows":
                subprocess.run(f"shutdown /s /m \\\\{ip}", check=True, shell=True)
            elif os_type == "Linux":
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=self.credentials['username'], password=self.credentials['password'])
                ssh.exec_command("sudo shutdown now")
                ssh.close()
            else:
                messagebox.showinfo("Info", f"OS type unknown for {ip}; cannot issue shutdown command.")
                return
            
            messagebox.showinfo("Success", f"Shutdown command sent to {ip}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to shutdown {ip}: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KillSwitch(root)
    root.mainloop()
