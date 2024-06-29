import tkinter as tk
from view.gui import LambdaCalcView
from controller.controller import LambdaCalcController

def main():
    """
    Function to initialize the main window and create the necessary instances for the Lambda Calculator GUI.
    """
    # Create the main tkinter window
    root = tk.Tk()
    
    # Create an instance of the LambdaCalcView class with the root window as the parent
    view = LambdaCalcView(root)
    
    # Create an instance of the LambdaCalcController class with the view as the parameter
    controller = LambdaCalcController(view)
    
    # Start the main loop of the tkinter window
    root.mainloop()

if __name__ == "__main__":
    main()
