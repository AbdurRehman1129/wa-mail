import json
import subprocess
import platform
import smtplib
import random
import os
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from colorama import init, Fore, Style
import pyfiglet
import sys

# Initialize Colorama
init(autoreset=True)

# Load configuration from JSON
def load_config(file_name="config.json"):
    try:
        with open(file_name, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

# Function to clear the screen
def clear_screen():
    try:
        if platform.system() == "Windows":
            subprocess.run("cls", shell=True)
        else:
            subprocess.run("clear", shell=True)
    except Exception:
        # Fallback: Print 100 blank lines if clear command fails
        print("\n" * 100)

# Function to display the banner
def display_banner():
    banner = pyfiglet.Figlet(font="small")
    banner_text = banner.renderText("DARK DEVIL")
    
    # Calculate terminal width and center the banner text
    terminal_width = os.get_terminal_size().columns
    centered_banner = '\n'.join(line.center(terminal_width) for line in banner_text.splitlines())

    # Print the banner centered at the top in cyan color
    print(Fore.CYAN + centered_banner)

    # Author line
    author_line = f"{Fore.YELLOW}Author/Github: {Style.RESET_ALL}{Fore.GREEN}@AbdurRehman1129"
    print(author_line.center(terminal_width))

# Function to show the main menu
def show_menu(error_message=""):
    clear_screen()
    display_banner()  # Show the banner
    print(f"{Fore.BLUE}MENU:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1.{Style.RESET_ALL} AUTOMATIC SENDING (1ST NUMBER BY 1ST EMAIL)")
    print(f"{Fore.GREEN}2.{Style.RESET_ALL} MANUAL SENDING (CHOOSE EMAIL)")
    print(f"{Fore.GREEN}3.{Style.RESET_ALL} EXIT")
    if error_message:
        print(f"{Fore.RED}{error_message}{Style.RESET_ALL}")

# Countdown timer with consistent terminal behavior
def countdown_timer(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r{Fore.YELLOW}Waiting {remaining} seconds before sending the next email...{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(1)
    # Clear the line after countdown
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

# Function to send emails with delay and random user-agent
def send_emails(sender_emails, receiver_email, email_body, subject_template, phone_numbers):
    for i, phone_number in enumerate(phone_numbers):
        if not sender_emails:
            print(f"{Fore.RED}No sender emails available.{Style.RESET_ALL}")
            return

        sender = sender_emails.pop(0)  # Use the first sender and remove it from the list
        sender_email = sender["email"]
        sender_password = sender["password"]

        # Set the subject with the phone number placeholders
        subject = subject_template.format(phone_number)

        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.set_content(email_body)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print(f"EMAIL SENT FROM {Fore.GREEN}{sender_email}{Style.RESET_ALL} TO {Fore.BLUE}{receiver_email}{Style.RESET_ALL} WITH PHONE NUMBER {Fore.YELLOW}{phone_number}{Style.RESET_ALL} IN SUBJECT")
            
            # Record the email in the report.txt
            timestamp = datetime.now(timezone.utc).isoformat()  # Current UTC timestamp
            try:
                subprocess.run(
                    ["python3", "report.py", sender_email, phone_number, timestamp],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error executing report.py. Ensure it exists and is executable.{Style.RESET_ALL}")

        except Exception as e:
            print(f"Error sending email from {sender_email}: {e}")

        # Delay only if this is not the last email
        if i < len(phone_numbers) - 1:
            delay = random.randint(15, 30)
            countdown_timer(delay)

# Function for automatic sending
def automatic_sending(config):
    phone_numbers = input(f"{Fore.GREEN}Enter the phone numbers (separated by commas): {Style.RESET_ALL}").split(',')
    phone_numbers = [number.strip() for number in phone_numbers]
    send_emails(config["senders"].copy(), config["receiver"], config["body"], config["subject"], phone_numbers)
    input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

# Function for manual sending
def manual_sending(config):
    while True:
        clear_screen()
        display_banner()  # Show the banner
        print(f"{Fore.BLUE}CHOOSE AN EMAIL:{Style.RESET_ALL}")
        for index, sender in enumerate(config["senders"]):
            print(f"{Fore.GREEN}{index + 1}.{Style.RESET_ALL} {sender['email']}")
        print(f"{Fore.GREEN}0.{Style.RESET_ALL} BACK TO MAIN MENU")

        email_choice = input(f"{Fore.GREEN}Enter the number of the email you want to use: {Style.RESET_ALL}")

        if email_choice.isdigit() and 1 <= int(email_choice) <= len(config["senders"]):
            selected_sender = config["senders"][int(email_choice) - 1]
            phone_number = input(f"{Fore.GREEN}Enter the phone number to send: {Style.RESET_ALL}")
            subject = config["subject"].format(phone_number)

            msg = EmailMessage()
            msg['From'] = selected_sender["email"]
            msg['To'] = config["receiver"]
            msg['Subject'] = subject
            msg.set_content(config["body"])

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(selected_sender["email"], selected_sender["password"])
                    server.send_message(msg)
                    print(f"EMAIL SENT FROM {Fore.GREEN}{selected_sender['email']}{Style.RESET_ALL} TO {Fore.BLUE}{config['receiver']}{Style.RESET_ALL} WITH PHONE NUMBER {Fore.YELLOW}{phone_number}{Style.RESET_ALL} IN SUBJECT")
                
                timestamp = datetime.now(timezone.utc).isoformat()
                try:
                    subprocess.run(
                        ["python3", "report.py", selected_sender["email"], phone_number, timestamp],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except subprocess.CalledProcessError:
                    print(f"{Fore.RED}Error executing report.py. Ensure it exists and is executable.{Style.RESET_ALL}")

            except Exception as e:
                print(f"Error sending email from {selected_sender['email']}: {e}")

            input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        elif email_choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid email choice. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

# Load config
config = load_config()

if config:
    while True:
        show_menu()
        choice = input(f"{Fore.GREEN}Choose an option: {Style.RESET_ALL}")

        if choice == '1':
            automatic_sending(config)
        elif choice == '2':
            manual_sending(config)
        elif choice == '3':
            print(f"{Fore.YELLOW}Exiting the program...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
