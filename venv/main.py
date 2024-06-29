import tkinter as tk
from view.gui import LambdaCalcView
from controller.controller import LambdaCalcController

def main():
    root = tk.Tk()
    view = LambdaCalcView(root)
    controller = LambdaCalcController(view)
    root.mainloop()

if __name__ == "__main__":
    main()
