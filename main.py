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
    command = "cls" if platform.system() == "Windows" else "clear"
    subprocess.run(command, shell=True)

# Function to display the banner
def display_banner():
    banner = pyfiglet.Figlet(font="small")
    banner_text = banner.renderText("DARK DEVIL")
    
    terminal_width = os.get_terminal_size().columns
    centered_banner = '\n'.join(line.center(terminal_width) for line in banner_text.splitlines())
    
    print(Fore.CYAN + centered_banner)
    # Center the author line based on terminal width
    author_line = f"Author/Github: @AbdurRehman1129"
    print(Fore.YELLOW + author_line.center(terminal_width))


# Function to show the main menu
def show_menu(error_message=""):
    clear_screen()
    display_banner()
    print(f"{Fore.CYAN}MENU:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1.{Style.RESET_ALL} AUTOMATIC SENDING (1ST NUMBER BY 1ST EMAIL)")
    print(f"{Fore.GREEN}2.{Style.RESET_ALL} MANUAL SENDING (CHOOSE EMAIL)")
    print(f"{Fore.GREEN}3.{Style.RESET_ALL} SEND EMAILS IN RANGE")
    print(f"{Fore.GREEN}4.{Style.RESET_ALL} INVERSE SENDING (FIRST NUMBER WITH LAST EMAIL)")
    print(f"{Fore.GREEN}5.{Style.RESET_ALL} EXIT")
    if error_message:
        print(f"{Fore.RED}{error_message}{Style.RESET_ALL}")

# Function to send emails with delay and random user-agent
def send_emails(sender_emails, receiver_email, email_body, subject_template, phone_numbers):
    i = 0
    while i < len(phone_numbers):
        if not sender_emails:
            print(f"{Fore.RED}No sender emails available.{Style.RESET_ALL}")
            return

        sender = sender_emails.pop(0)
        sender_email = sender["email"]
        sender_password = sender["password"]

        if subject_template.count("{}") == 2:
            subject = subject_template.format(phone_numbers[i], phone_numbers[i])
        else:
            subject = subject_template.format(phone_numbers[i])

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
                print(f"EMAIL SENT FROM {Fore.GREEN}{sender_email}{Style.RESET_ALL} TO {Fore.BLUE}{receiver_email}{Style.RESET_ALL} WITH PHONE NUMBER {Fore.YELLOW}{phone_numbers[i]}{Style.RESET_ALL} IN SUBJECT")
            
            timestamp = datetime.now(timezone.utc).isoformat()
            subprocess.run(["python3", "report.py", sender_email, phone_numbers[i], timestamp])
            i += 1  # move to the next phone number after successful sending

        except Exception as e:
            print(f"{Fore.RED}Error sending email from {sender_email}: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Retrying with the same email and phone number: {phone_numbers[i]}{Style.RESET_ALL}")
            # Wait a moment before retrying
            time.sleep(5)

        if i < len(phone_numbers):
            delay = random.randint(7, 15)
            for remaining in range(delay, 0, -1):
                print(f"{Fore.YELLOW}Waiting {remaining} seconds before sending the next email...{Style.RESET_ALL}", end='\r')
                time.sleep(1)
            print(" " * 50, end='\r')

# Function for automatic sending
def automatic_sending(config):
    while True:
        clear_screen()
        display_banner()
        total_emails = len(config['senders'])
        print(f"{Fore.LIGHTCYAN_EX}AUTOMATIC SENDING{Style.RESET_ALL}")
        print(f"{Fore.GREEN}You have a total of {Style.RESET_ALL}{Fore.YELLOW}{total_emails}{Style.RESET_ALL} {Fore.GREEN}emails available.")
        print(f"{Fore.GREEN}You can enter up to {Style.RESET_ALL}{Fore.YELLOW}{total_emails}{Style.RESET_ALL} {Fore.GREEN}phone numbers.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Type '{Style.RESET_ALL}{Fore.YELLOW}0{Style.RESET_ALL}{Fore.GREEN}' to return to the main menu.{Style.RESET_ALL}")

        phone_numbers = input(f"{Fore.GREEN}Enter phone numbers (separated by commas): {Style.RESET_ALL}").split(',')
        phone_numbers = [number.strip() for number in phone_numbers]

        if len(phone_numbers) == 1 and phone_numbers[0] == '0':
            break

        if len(phone_numbers) > total_emails:
            print(f"{Fore.RED}You can only enter up to {total_emails} phone numbers. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to retry...{Style.RESET_ALL}")
            continue

        send_emails(config["senders"].copy(), config["receiver"], config["body"], config["subject"], phone_numbers)
        input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        break

# Function for manual sending
def manual_sending(config):
    while True:
        clear_screen()
        display_banner()
        print(f"{Fore.CYAN}MANUAL SENDING{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Available emails:{Style.RESET_ALL}")
        for idx, sender in enumerate(config["senders"], start=1):
            print(f"{Fore.LIGHTMAGENTA_EX}{idx}. {sender['email']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Type '{Style.RESET_ALL}{Fore.YELLOW}0{Style.RESET_ALL}{Fore.GREEN}' to return to the main menu.{Style.RESET_ALL}")

        choice = input(f"{Fore.GREEN}Choose an email by number: {Style.RESET_ALL}")
        if choice == '0':
            break
        try:
            index = int(choice) - 1
            if index < 0 or index >= len(config["senders"]):
                raise ValueError
            sender = config["senders"][index]
            phone_number = input(f"{Fore.GREEN}Enter the phone number to include in the subject: {Style.RESET_ALL}")
            send_emails([sender], config["receiver"], config["body"], config["subject"], [phone_number])
        except ValueError:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to retry...{Style.RESET_ALL}")

# Function for sending emails in a range
def send_emails_in_range(config):
    while True:
        clear_screen()
        display_banner()
        print(f"{Fore.CYAN}RANGE SELECTION{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Type '{Style.RESET_ALL}{Fore.YELLOW}0{Style.RESET_ALL}{Fore.GREEN}' at any time to return to the main menu.{Style.RESET_ALL}")
        
        try:
            start_input = input(f"{Fore.GREEN}Enter the start email index (1-{len(config['senders'])}): {Style.RESET_ALL}")
            if start_input.strip() == '0':
                break
            start = int(start_input) - 1
            
            end_input = input(f"{Fore.GREEN}Enter the end email index (1-{len(config['senders'])}): {Style.RESET_ALL}")
            if end_input.strip() == '0':
                break
            end = int(end_input)
            
            if start < 0 or end > len(config["senders"]) or start >= end:
                raise ValueError
            
            phone_numbers_input = input(f"{Fore.GREEN}Enter phone numbers (separated by commas): {Style.RESET_ALL}")
            if phone_numbers_input.strip() == '0':
                break
            phone_numbers = [number.strip() for number in phone_numbers_input.split(',')]
            
            send_emails(config["senders"][start:end], config["receiver"], config["body"], config["subject"], phone_numbers)
            break
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to retry...{Style.RESET_ALL}")

# Function for inverse sending
def inverse_sending(config):
    while True:
        clear_screen()
        display_banner()
        total_emails = len(config['senders'])
        print(f"{Fore.LIGHTCYAN_EX}INVERSE SENDING{Style.RESET_ALL}")
        print(f"{Fore.GREEN}You have a total of {Style.RESET_ALL}{Fore.YELLOW}{total_emails}{Style.RESET_ALL} {Fore.GREEN}emails available.")
        print(f"{Fore.GREEN}You can enter up to {Style.RESET_ALL}{Fore.YELLOW}{total_emails}{Style.RESET_ALL} {Fore.GREEN}phone numbers.{Style.RESET_ALL}")

        phone_numbers = input(f"{Fore.GREEN}Enter phone numbers (separated by commas): {Style.RESET_ALL}").split(',')
        phone_numbers = [number.strip() for number in phone_numbers]

        if len(phone_numbers) > total_emails:
            print(f"{Fore.RED}You can only enter up to {total_emails} phone numbers. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to retry...{Style.RESET_ALL}")
            continue

        reversed_senders = list(reversed(config["senders"]))
        send_emails(reversed_senders, config["receiver"], config["body"], config["subject"], phone_numbers)
        input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        break

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
            send_emails_in_range(config)
        elif choice == '4':
            inverse_sending(config)
        elif choice == '5':
            print(f"{Fore.YELLOW}Exiting the program...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
