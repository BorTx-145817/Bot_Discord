from halo import Halo

# Setup spinner
spinner = Halo(text='Bot is running', spinner='dots')

def start_spinner():
    spinner.start()

def stop_spinner():
    spinner.stop()

def succeed_spinner(text=""):
    spinner.succeed(text)
