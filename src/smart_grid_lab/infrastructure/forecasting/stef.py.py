import numpy as np
import pandas as pd
import plotly.express as px

import plotly.io as pio

pio.renderers.default = "browser"

import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)

train_end = "2018-10-01"
val_end = "2018-11-01"

train_df = df.loc[:train_end]

val_df = df.loc[train_end:val_end]

test_df = df.loc[val_end:]

print(train_df.shape)
print(val_df.shape)
print(test_df.shape)


FEATURES = [c for c in df.columns if c != TARGET]

FEATURES


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_val = val_df[FEATURES]
y_val = val_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


openstef_df = df.reset_index()

openstef_df.rename(
    columns={
        df.index.name: "datetime",
        TARGET: "load",
    },
    inplace=True,
)

openstef_df.head()


openstef_df.rename(
    columns={
        "utc_timestamp": "datetime",
        TARGET: "load",
    },
    inplace=True,
)


sample = df.iloc[-96 * 7 :]

sample["load"].plot(figsize=(15, 5))

plt.title("One Week Load Profile")

plt.show()


naive_pred = y_test.shift(96)

mask = naive_pred.notna()

mae = mean_absolute_error(
    y_test[mask],
    naive_pred[mask],
)

rmse = np.sqrt(
    mean_squared_error(
        y_test[mask],
        naive_pred[mask],
    )
)

print("MAE :", mae)
print("RMSE:", rmse)


FORECAST_HORIZON = 12


from openstef.pipeline.train_model import PredictionJobDataClass

print(PredictionJobDataClass.model_fields.keys())


from openstef.pipeline.train_model import (
    PredictionJobDataClass,
)

pj = PredictionJobDataClass(
    id="microgrid_load",
    name="Microgrid Load Forecast",
    model="xgb",
    forecast_type="demand",
)


train_df.head()


train_df.columns


cols = train_df.columns.tolist()

cols.remove("load")

train_df = train_df[["load"] + cols]


import inspect

from openstef.pipeline.train_model import (
    train_model_pipeline_core,
)

print(inspect.getsource(train_model_pipeline_core)[:8000])


from openstef.model.regressors import xgb

dir(xgb)


from openstef.model.regressors import lgbm

dir(lgbm)


from openstef.pipeline.train_model import (
    PredictionJobDataClass,
)

pj = PredictionJobDataClass(
    id="microgrid_load",
    name="Microgrid Load Forecast",
    model="xgb",
    forecast_type="demand",
)
