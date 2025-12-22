import sys
import os

# Ensure the current directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gui_main import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
