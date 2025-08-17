import random
import string
import math
import os
import locale
import json
import sys
from colorama import Fore, Style, init

# === GUI ===
import tkinter as tk
from tkinter import messagebox, ttk

init(autoreset=True)

with open("lang.json", "r", encoding="utf-8") as f:
    LANGS = json.load(f)

def detect_lang():
    system_lang, _ = locale.getdefaultlocale()
    if system_lang and system_lang.lower().startswith("ru"):
        return "ru"
    else:
        return "en"

LANG_CODE = detect_lang()
LANG = LANGS[LANG_CODE]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def estimate_crack_time(password: str) -> float:
    if not password:
        return 0
    charset_size = 0
    if any(c.islower() for c in password): charset_size += 26
    if any(c.isupper() for c in password): charset_size += 26
    if any(c.isdigit() for c in password): charset_size += 10
    if any(c in string.punctuation for c in password): charset_size += len(string.punctuation)

    guesses_per_second = 1e9
    log10_combinations = len(password) * math.log10(charset_size)
    log10_seconds = log10_combinations - math.log10(guesses_per_second)
    return log10_seconds

def human_readable_time(log10_seconds: float) -> str:
    if log10_seconds < 0: return "< 1 sec"
    if log10_seconds < 2: return f"{10**log10_seconds:.2f} sec"
    if log10_seconds < 4: return f"{10**(log10_seconds-2):.2f} min"
    if log10_seconds < 6: return f"{10**(log10_seconds-4):.2f} h"
    if log10_seconds < 9: return f"{10**(log10_seconds-6):.2f} d"
    if log10_seconds < 12: return f"{10**(log10_seconds-9):.2f} y"
    if log10_seconds < 15: return f"{10**(log10_seconds-12):.2f} k y"
    if log10_seconds < 18: return f"{10**(log10_seconds-15):.2f} M y"
    if log10_seconds < 21: return f"{10**(log10_seconds-18):.2f} B y"
    return f"10^{log10_seconds:.0f} sec (astronomically long)"

def password_strength(password: str) -> str:
    log10_sec = estimate_crack_time(password)
    if log10_sec < 2:
        return "❌ Very Bad"
    elif log10_sec < 4:
        return "⚠️ Bad"
    elif log10_sec < 6:
        return "😐 Medium"
    elif log10_sec < 9:
        return "✅ Good"
    elif log10_sec < 12:
        return "💪 Great"
    else:
        return "🚀 NASA-level"

def generate_password(length: int = 16) -> str:
    if length <= 0:
        return ""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

# ======================
#         GUI
# ======================
def run_gui():
    root = tk.Tk()
    root.title("🔐 Password Generator & Checker")
    root.geometry("500x400")
    root.resizable(False, False)

    tab_control = ttk.Notebook(root)
    tab_gen = ttk.Frame(tab_control)
    tab_check = ttk.Frame(tab_control)
    tab_control.add(tab_gen, text="🔑 Generate")
    tab_control.add(tab_check, text="🕵️ Check")
    tab_control.pack(expand=1, fill="both")

    # === Tab 1: Generation ===
    lbl_len = ttk.Label(tab_gen, text="Password length:")
    lbl_len.pack(pady=5)
    entry_len = ttk.Entry(tab_gen)
    entry_len.insert(0, "16")
    entry_len.pack(pady=5)

    result_gen = tk.Text(tab_gen, height=6, width=50, wrap="word")
    result_gen.pack(pady=5)

    def gen_password():
        try:
            length = int(entry_len.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a number!")
            return
        pwd = generate_password(length)
        if not pwd:
            messagebox.showwarning("Warning", "Password length cannot be 0!")
            return
        log10_time = estimate_crack_time(pwd)
        result_gen.delete("1.0", tk.END)
        result_gen.insert(tk.END, f"Generated: {pwd}\n")
        result_gen.insert(tk.END, f"Time: {human_readable_time(log10_time)}\n")
        result_gen.insert(tk.END, f"Strength: {password_strength(pwd)}")

    ttk.Button(tab_gen, text="Generate", command=gen_password).pack(pady=5)

    # === Tab 2: Check ===
    lbl_pwd = ttk.Label(tab_check, text="Enter password:")
    lbl_pwd.pack(pady=5)
    entry_pwd = ttk.Entry(tab_check, show="*")
    entry_pwd.pack(pady=5)

    result_check = tk.Text(tab_check, height=6, width=50, wrap="word")
    result_check.pack(pady=5)

    def check_password():
        pwd = entry_pwd.get()
        if not pwd:
            messagebox.showerror("Error", "Password cannot be empty!")
            return
        log10_time = estimate_crack_time(pwd)
        result_check.delete("1.0", tk.END)
        result_check.insert(tk.END, f"Time: {human_readable_time(log10_time)}\n")
        result_check.insert(tk.END, f"Strength: {password_strength(pwd)}")

    ttk.Button(tab_check, text="Check", command=check_password).pack(pady=5)

    root.mainloop()

# ======================
#        CLI
# ======================
def generation_mode():
    while True:
        clear_screen()
        print(Fore.YELLOW + LANG["gen_mode"] + Style.RESET_ALL)
        length = input(LANG["input_length"])
        if length.lower() == "q": break
        if not length.isdigit():
            print(Fore.RED + LANG["error_number"] + Style.RESET_ALL)
            input("Enter..."); continue
        pwd = generate_password(int(length))
        if not pwd:
            print(Fore.RED + LANG["error_zero"] + Style.RESET_ALL)
            input("Enter..."); continue
        log10_time = estimate_crack_time(pwd)
        print(Fore.LIGHTBLACK_EX + "─"*50)
        print(Fore.YELLOW + f"\n{LANG['generated']}\n" + Fore.WHITE + pwd)
        print(Fore.BLUE + LANG["time"], Fore.WHITE + human_readable_time(log10_time))
        print(Fore.GREEN + LANG["strength"], password_strength(pwd))
        print(Fore.LIGHTBLACK_EX + "─"*50)
        input(Fore.CYAN + "\n" + LANG["new_gen"])

def check_mode():
    while True:
        clear_screen()
        print(Fore.YELLOW + LANG["check_mode"] + Style.RESET_ALL)
        pwd = input(LANG["input_password"])
        if pwd.lower() == "q": break
        if not pwd:
            print(Fore.RED + LANG["error_empty"] + Style.RESET_ALL)
            input("Enter..."); continue
        log10_time = estimate_crack_time(pwd)
        print(Fore.LIGHTBLACK_EX + "─"*50)
        print(Fore.BLUE + "\n" + LANG["time"], Fore.WHITE + human_readable_time(log10_time))
        print(Fore.GREEN + LANG["strength"], password_strength(pwd))
        print(Fore.LIGHTBLACK_EX + "─"*50)
        input(Fore.CYAN + "\n" + LANG["new_check"])

def main():
    if "-gui" in sys.argv:
        run_gui()
        return

    while True:
        clear_screen()
        print(Fore.CYAN + LANG["title"] + Style.RESET_ALL)
        print(Fore.LIGHTBLACK_EX + "═"*50 + Style.RESET_ALL)
        mode = input(LANG["menu"])
        if mode == "1": generation_mode()
        elif mode == "2": check_mode()
        elif mode.lower() == "q":
            clear_screen()
            print(Fore.MAGENTA + LANG["exit"] + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Wrong choice!" + Style.RESET_ALL)
            input("Enter...")

if __name__ == "__main__":
    main()
