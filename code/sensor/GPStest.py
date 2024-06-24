import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import contextily as ctx

# Read the text file
with open('picRep/PIC1/code/sensor/gps_coordinates.txt', 'r') as file:
    lines = file.readlines()

# Extract latitude and longitude from each line
coordinates = []
for line in lines:
    if "got the gps" in line:
        parts = line.split(',')
        lat = float(parts[0].split(':')[-1].strip())
        lng = float(parts[1].split(':')[-1].strip())
        coordinates.append((lat, lng))

# Convert to DataFrame
df = pd.DataFrame(coordinates, columns=['Latitude', 'Longitude'])

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

# Reproject to Web Mercator
gdf = gdf.set_crs(epsg=4326)
gdf = gdf.to_crs(epsg=3857)

# Plot the map
fig, ax = plt.subplots(figsize=(15, 10))
gdf.plot(ax=ax, color='red', markersize=50, alpha=0.7)

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# Adjust plot limits to focus on the points
xlim = [gdf.geometry.x.min() - 1000, gdf.geometry.x.max() + 1000]
ylim = [gdf.geometry.y.min() - 1000, gdf.geometry.y.max() + 1000]
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# Set the title and labels
plt.title('GPS Coordinates on OpenStreetMap')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Show the plot
plt.show()
