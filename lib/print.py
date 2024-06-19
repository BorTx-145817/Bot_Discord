import time
from colorama import Fore, Back, init

# Initialize colorama
init(autoreset=True)

def custom_print(message, message_type="Message", user=None, runtime=None, button=None):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    user_str = f"│ User: {user}" if user else ""
    runtime_str = f"│ Runtime: {runtime}" if runtime else ""
    button_str = f"│ Button: {button}" if button else ""
    
    print(f"╭┈❲ {timestamp} ❱")
    print(f"╞❴ {message_type} ❵ {message}")
    if user:
        print(user_str)
    if runtime:
        print(runtime_str)
    if button:
        print(button_str)
    print("╰╼┈⟐ ❰ Powered by : Ar BorTx Offical ❱")
