from .simulation_callbacks import register_simulation_callbacks


def register_callbacks(app):
    register_simulation_callbacks(app)
