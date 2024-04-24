import tkinter as tk
from tkinter import simpledialog

class SoundIntensityGrid(tk.Tk):
    def __init__(self, rows, cols):
        super().__init__()

        self.rows = rows
        self.cols = cols

        self.cell_width = 30
        self.cell_height = 30

        self.create_grid()

    def create_grid(self):
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack()

        self.cells = [[tk.Frame(self.grid_frame, width=self.cell_width, height=self.cell_height, bg="#CCCCCC", borderwidth=1, relief="solid")
                       for _ in range(self.cols)] for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].grid(row=i, column=j, padx=1, pady=1)
                self.cells[i][j].bind("<Button-1>", lambda event, i=i, j=j: self.on_cell_click(i, j))

    def on_cell_click(self, row, col):
        value = simpledialog.askinteger("Intensidade de som", f"Insira um valor para a célula ({row+1}, {col+1}):", initialvalue=0)
        if value is not None:
            self.update_cell_intensity(row, col, value)

    def update_cell_intensity(self, row, col, intensity):
        red = min(int(255 * intensity / 255), 255)
        blue = min(int(255 * (255 - intensity) / 255), 255)
        color = f"#{red:02X}00{blue:02X}"

        self.cells[row][col].config(bg=color)

if __name__ == "__main__":
    grid_app = SoundIntensityGrid(rows=10, cols=10)
    grid_app.geometry("400x400")

    grid_app.mainloop()
