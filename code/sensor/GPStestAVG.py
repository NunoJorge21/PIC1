import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import contextily as ctx

# Read the text file
with open('picRep/PIC1/code/sensor/gps_coordinates3.txt', 'r') as file:
    lines = file.readlines()

# Extract latitude and longitude from each line
coordinates = []
average_coordinates = []
for line in lines:
    if "got the gps" in line and "avg" not in line:
        parts = line.split(',')
        lat = float(parts[0].split(':')[-1].strip())
        lng = float(parts[1].split(':')[-1].strip())
        coordinates.append((lat, lng))
    elif "avg got the gps" in line:
        parts = line.split(',')
        lat = float(parts[0].split(':')[-1].strip())
        lng = float(parts[1].split(':')[-1].strip())
        average_coordinates.append((lat, lng))

# Convert to DataFrame
df = pd.DataFrame(coordinates, columns=['Latitude', 'Longitude'])
avg_df = pd.DataFrame(average_coordinates, columns=['Latitude', 'Longitude'])

# Create GeoDataFrames
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
avg_gdf = gpd.GeoDataFrame(avg_df, geometry=gpd.points_from_xy(avg_df.Longitude, avg_df.Latitude))

# Reproject to Web Mercator
gdf = gdf.set_crs(epsg=4326)
gdf = gdf.to_crs(epsg=3857)
avg_gdf = avg_gdf.set_crs(epsg=4326)
avg_gdf = avg_gdf.to_crs(epsg=3857)

# Plot the map
fig, ax = plt.subplots(figsize=(15, 10))
gdf.plot(ax=ax, color='red', markersize=50, alpha=0.7, label='GPS Points')
avg_gdf.plot(ax=ax, color='blue', markersize=100, alpha=0.7, marker='x', label='Average Points')

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# Adjust plot limits to focus on the points
xlim = [min(gdf.geometry.x.min(), avg_gdf.geometry.x.min()) - 1000, max(gdf.geometry.x.max(), avg_gdf.geometry.x.max()) + 1000]
ylim = [min(gdf.geometry.y.min(), avg_gdf.geometry.y.min()) - 1000, max(gdf.geometry.y.max(), avg_gdf.geometry.y.max()) + 1000]
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# Set the title and labels
plt.title('GPS Coordinates and Averages on OpenStreetMap')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Add legend
plt.legend()

# Show the plot
plt.show()
