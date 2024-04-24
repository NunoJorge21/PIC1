import tkinter as tk
from tkinter import simpledialog, messagebox

class SoundIntensityGrid(tk.Tk):
    def __init__(self, rows, cols):
        super().__init__()

        self.rows = rows
        self.cols = cols

        self.cell_width = 30
        self.cell_height = 30

        self.canvas_width = self.cols * self.cell_width
        self.canvas_height = self.rows * self.cell_height

        self.create_grid()

    def create_grid(self):
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.intensity_values = [[0] * self.cols for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                x1, y1 = j * self.cell_width, i * self.cell_height
                x2, y2 = x1 + self.cell_width, y1 + self.cell_height
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#CCCCCC", outline="")

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        col = event.x // self.cell_width
        row = event.y // self.cell_height
        self.update_cell_intensity(row, col)

    def update_cell_intensity(self, row, col):
        value = simpledialog.askinteger("Intensidade de som", f"Insira um valor para a célula ({row+1}, {col+1}):", initialvalue=0)
        if value is not None:
            if 0 <= value <= 120:
                self.intensity_values[row][col] = value
                self.update_cell_color(row, col)
            else:
                messagebox.showerror("Erro", "Valor fora do intervalo permitido (0-120)")

    def update_cell_color(self, row, col):
        intensity = self.intensity_values[row][col]
        red = min(int(255 * intensity / 120), 255)
        blue = min(int(255 * (120 - intensity) / 120), 255)
        color = f"#{red:02X}00{blue:02X}"

        x1, y1 = col * self.cell_width, row * self.cell_height
        x2, y2 = x1 + self.cell_width, y1 + self.cell_height

        self.canvas.itemconfig(self.canvas.find_closest((x1 + x2) / 2, (y1 + y2) / 2), fill=color)

if __name__ == "__main__":
    grid_app = SoundIntensityGrid(rows=10, cols=10)
    grid_app.geometry("400x400")

    grid_app.mainloop()

