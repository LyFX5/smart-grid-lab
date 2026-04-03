from dash import Dash
from layouts.window1 import layout
from callbacks.main_callbacks import register_callbacks

import webbrowser

app = Dash(__name__)
app.layout = layout

register_callbacks(app)

if __name__ == "__main__":
    # webbrowser.open("http://127.0.0.1:8050/")
    app.run(debug=True)
