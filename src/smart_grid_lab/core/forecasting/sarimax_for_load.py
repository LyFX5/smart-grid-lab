from statsmodels.tsa.statespace.sarimax import SARIMAX


class SarimaxForecaster:

    def __init__(self, order=(2, 0, 2), seasonal_order=(2, 0, 2, 24)):
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None

    def fit(self, y, exog):
        self.model = SARIMAX(
            y,
            exog=exog,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)
        return self

    def forecast(self, steps, exog_future):
        return self.model.get_forecast(
            steps=steps, exog=exog_future
        ).predicted_mean

    @property
    def fitted(self):
        return self.model.fittedvalues
