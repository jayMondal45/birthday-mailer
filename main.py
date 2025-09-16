import pandas as pd
import random
import datetime as dt
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your Gmail credentials
my_email = "Your_email_here"
password = "Your_app_key_here"

def read_template_file(filename, name):
    """Read template file and replace [NAME] placeholder."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().replace("[NAME]", name)
    except FileNotFoundError:
        print(f"Warning: Template file '{filename}' not found.")
        return f"Happy Birthday, {name}! Hope you have a wonderful day!"
    except Exception as e:
        print(f"Error reading template file '{filename}': {e}")
        return f"Happy Birthday, {name}! Hope you have a wonderful day!"

def send_birthday_emails():
    """Main function to send birthday emails."""
    
    # Check if birthdays.csv exists
    if not os.path.exists("birthdays.csv"):
        print("Error: birthdays.csv file not found!")
        return
    
    try:
        # Read birthdays.csv
        data = pd.read_csv("birthdays.csv")
        
        # Validate required columns
        required_columns = ["name", "email", "month", "day"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            print(f"Error: Missing columns in CSV: {missing_columns}")
            return
            
        records = data.to_dict(orient="records")
        
        # Get today's date
        today = dt.datetime.now()
        current_month = today.month
        current_day = today.day
        
        print(f"Checking birthdays for {today.strftime('%B %d, %Y')}...")
        
        birthday_count = 0
        
        # Open SMTP connection once
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(my_email, password)
                
                # Loop through all people
                for person in records:
                    try:
                        name = str(person["name"]).strip()
                        email = str(person["email"]).strip()
                        month = int(person["month"])
                        day = int(person["day"])
                        
                        # Skip if any required field is missing/invalid
                        if pd.isna(person["name"]) or pd.isna(person["email"]):
                            print(f"Skipping incomplete record: {person}")
                            continue
                            
                        # Check if today is the person's birthday
                        if month == current_month and day == current_day:
                            birthday_count += 1
                            
                            # Choose appropriate template
                            if name == "girlfriend":
                                # Special girlfriend letter
                                message = read_template_file("letter_templates/girlfriend.txt", name)
                            else:
                                # Random letter template (letter_1.txt, letter_2.txt, letter_3.txt)
                                random_num = random.randint(1, 3)
                                message = read_template_file(f"letter_templates/letter_{random_num}.txt", name)
                            
                            # Create proper email message
                            msg = MIMEMultipart()
                            msg['From'] = my_email
                            msg['To'] = email
                            msg['Subject'] = "Happy Birthday! 🎉"
                            
                            # Attach message body
                            msg.attach(MIMEText(message, 'plain', 'utf-8'))
                            
                            # Send email
                            connection.send_message(msg)
                            print(f"✅ Birthday email sent to {name} ({email})")
                            
                    except (ValueError, KeyError) as e:
                        print(f"Error processing record for {person.get('name', 'Unknown')}: {e}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error sending email to {person.get('name', 'Unknown')}: {e}")
                        continue
                        
        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed! Please check:")
            print("1. Your email address is correct")
            print("2. You're using an App Password (not your regular Gmail password)")
            print("3. 2-Factor Authentication is enabled on your Gmail account")
            return
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error occurred: {e}")
            return
        except Exception as e:
            print(f"❌ Unexpected error with email connection: {e}")
            return
            
        if birthday_count == 0:
            print("No birthdays today! 🎂")
        else:
            print(f"🎉 Sent {birthday_count} birthday email{'s' if birthday_count != 1 else ''}!")
            
    except FileNotFoundError:
        print("❌ Error: birthdays.csv file not found!")
    except pd.errors.EmptyDataError:
        print("❌ Error: birthdays.csv file is empty!")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")

if __name__ == "__main__":
    send_birthday_emails()