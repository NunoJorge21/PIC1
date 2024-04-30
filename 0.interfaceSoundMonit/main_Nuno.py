import plotly.express as px
import pandas as pd

def getDataFromArduino():
    data = {'Latitude': [38.736667, 38.736944, 38.736944, 38.736667], 
            'Longitude': [-9.137222, -9.137222, -9.138333, -9.138333],
            'Intensity_dB': [120, 120, 30, 30]}

    return pd.DataFrame(data)

df = getDataFromArduino()
#print(type(df))
#print(df)

# color of the dot determined by 'peak_hour'
# size of the dot determined by 'car_hours'
fig = px.scatter_mapbox(df,
                        lon = df['Longitude'],
                        lat = df['Latitude'],
                        zoom = 18,
                        color = df['Intensity_dB'],
                        size = df['Intensity_dB'],
                        width = 1200,
                        height = 900,
                        title = 'Sound Monitoring Scatter Map')

fig.update_layout(mapbox_style='open-street-map')
fig.update_layout(margin={'r':0, 't':50, 'l':0, 'b':10})
fig.show()

print('Plot complete.')