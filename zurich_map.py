"""A map of Zürich built using tkinter python library
Followed tutorial from: https://www.youtube.com/watch?v=qDO5ndZuibk
Tkinter documentation: https://github.com/TomSchimansky/TkinterMapView?tab=readme-ov-file#create-position-markers

"""
import tkinter
from tkintermapview import TkinterMapView


def plot_locations(locations: list[tuple[float, float]]) -> None:
    """Plot each location in locations in the interactive map of Zürich

    Representation Invariants:
    - For each tuple t in the list, t[0] is the latitude of the location as a float
    - For each tuple t in the list, t[1] is the longtitude of the location as a float
    """
    for location in locations:
        map_widget.set_marker(location[0], location[1])


if __name__ == '__main__':
    # Create Tkinter window
    window = tkinter.Tk()
    window.geometry("600x600")
    window.title("Map_of_Zürich")
    window.resizable(False, False)

    # Create google map window
    map_widget = TkinterMapView(window, width=600, height=600, corner_radius=0)
    map_widget.pack(fill='both')

    # Setting the locaiton to Zürich
    map_widget.set_position(47.3769, 8.5417)
    map_widget.set_zoom(12)

    # Plot the locations on the map
    # marker_2 = map_widget.set_marker(47.384444284588675, 8.574511882827997, 'location1')
    # market_3 = map_widget.set_marker(47.376525305868704, 8.571999516647077, "location2")

    # Running the program
    window.mainloop()
