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
    print(f"{Fore.GREEN}3.{Style.RESET_ALL} SEND EMAILS IN RANGE")
    print(f"{Fore.GREEN}4.{Style.RESET_ALL} EXIT")
    if error_message:
        print(f"{Fore.RED}{error_message}{Style.RESET_ALL}")

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
        if subject_template.count("{}") == 2:
            subject = subject_template.format(phone_number, phone_number)
        else:
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
            subprocess.run(["python3", "report.py", sender_email, phone_number, timestamp])

        except Exception as e:
            print(f"Error sending email from {sender_email}: {e}")

        # Delay only if this is not the last email
        if i < len(phone_numbers) - 1:
            delay = random.randint(7, 15)
            for remaining in range(delay, 0, -1):
                print(f"{Fore.YELLOW}Waiting {remaining} seconds before sending the next email...{Style.RESET_ALL}", end='\r')
                time.sleep(1)
            print(" " * 50, end='\r')  # Clear the line after countdown

# Function for automatic sending
def automatic_sending(config):
    phone_numbers = input(f"{Fore.GREEN}Enter the phone numbers (separated by commas): {Style.RESET_ALL}").split(',')
    phone_numbers = [number.strip() for number in phone_numbers]
    
    # Display the number of emails to be used
    print(f"{Fore.GREEN}You have {Style.RESET_ALL}{Fore.YELLOW}{len(config['senders'])}{Style.RESET_ALL} emails available. Enter {Fore.YELLOW}{len(config['senders'])}{Style.RESET_ALL} phone numbers.")
    
    send_emails(config["senders"].copy(), config["receiver"], config["body"], config["subject"], phone_numbers)
    
    # Add random delay before showing "Press Enter to continue..."
    if phone_numbers:
        delay = random.randint(2, 5)  # Random delay of 2 to 5 seconds
        time.sleep(delay)
    
    input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

# Function for manual sending
def manual_sending(config):
    while True:
        clear_screen()
        display_banner()  # Show the banner
        print(f"{Fore.BLUE}CHOOSE AN EMAIL:{Style.RESET_ALL}")
        for index, sender in enumerate(config["senders"]):
            print(f"{Fore.GREEN}{index + 1}.{Style.RESET_ALL} {sender['email']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}0.{Style.RESET_ALL} BACK TO MAIN MENU{Style.RESET_ALL}")

        email_choice = input(f"{Fore.GREEN}Enter the number of the email you want to use: {Style.RESET_ALL}")

        if email_choice.isdigit() and 1 <= int(email_choice) <= len(config["senders"]):
            selected_sender = config["senders"][int(email_choice) - 1]
            phone_number = input(f"{Fore.GREEN}Enter the phone number to send: {Style.RESET_ALL}")

            # Set the subject with the phone number
            subject = config["subject"].format(phone_number, phone_number)

            # Create the email message
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
                
                # Record the email in the report.txt
                timestamp = datetime.now(timezone.utc).isoformat()
                subprocess.run(["python3", "report.py", selected_sender["email"], phone_number, timestamp])

            except Exception as e:
                print(f"Error sending email from {selected_sender['email']}: {e}")

            input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        elif email_choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid email choice. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

# Function for sending emails in a range
def send_emails_in_range(config):
    clear_screen()
    display_banner()

    print(f"{Fore.BLUE}CHOOSE EMAIL RANGE:{Style.RESET_ALL}")
    for index, sender in enumerate(config["senders"]):
        print(f"{Fore.GREEN}{index + 1}.{Style.RESET_ALL} {sender['email']}{Style.RESET_ALL}")
    
    start_index = int(input(f"{Fore.GREEN}Enter the number of the first email (starting from 1): {Style.RESET_ALL}")) - 1
    end_index = int(input(f"{Fore.GREEN}Enter the number of the last email (starting from 1): {Style.RESET_ALL}")) - 1

    # Check for valid range
    if start_index < 0 or end_index >= len(config["senders"]) or start_index > end_index:
        print(f"{Fore.RED}Invalid range. Please try again.{Style.RESET_ALL}")
        input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        return

    # Calculate the number of emails in the range
    num_emails = end_index - start_index + 1

    # Display the selected range and number of emails
    print(f"{Fore.GREEN}You have chosen {Fore.YELLOW}{num_emails}{Style.RESET_ALL} {Fore.GREEN}emails starting from email number {Fore.YELLOW}{start_index + 1}{Style.RESET_ALL} {Fore.GREEN}to email number {Fore.YELLOW}{end_index + 1}{Style.RESET_ALL}.")
    
    # Extract the email range
    selected_senders = config["senders"][start_index:end_index + 1]

    # Ask for phone numbers
    phone_numbers = input(f"{Fore.GREEN}Enter the phone numbers (separated by commas): {Style.RESET_ALL}").split(',')
    phone_numbers = [number.strip() for number in phone_numbers]

    # Send the emails
    send_emails(selected_senders, config["receiver"], config["body"], config["subject"], phone_numbers)
    
    input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

# Load config
config = load_config()

if config:
    # Main execution loop
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
            print(f"{Fore.YELLOW}Exiting the program...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
