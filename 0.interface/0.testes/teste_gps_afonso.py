import tkinter as tk
from tkinter import messagebox
import folium
import webbrowser

def generate_map(lat, lon):
    # Create a folium map centered at the given latitude and longitude
    map_ = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], tooltip="Location").add_to(map_)
    
    # Save the map to an HTML file
    map_.save("map.html")
    
    # Open the map in the default web browser
    webbrowser.open("map.html")

def submit():
    try:
        # Get the input values
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        
        # Generate the map with the provided coordinates
        generate_map(lat, lon)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numeric values for latitude and longitude")

# Create the main window
root = tk.Tk()
root.title("GPS Coordinates to Map")

# Create and place the latitude and longitude entry fields
tk.Label(root, text="Latitude:").grid(row=0, column=0, padx=10, pady=10)
lat_entry = tk.Entry(root)
lat_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Longitude:").grid(row=1, column=0, padx=10, pady=10)
lon_entry = tk.Entry(root)
lon_entry.grid(row=1, column=1, padx=10, pady=10)

# Create and place the submit button
submit_button = tk.Button(root, text="Generate Map", command=submit)
submit_button.grid(row=2, columnspan=2, padx=10, pady=10)

# Start the GUI event loop
root.mainloop()
