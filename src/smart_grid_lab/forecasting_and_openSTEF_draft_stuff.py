train_end = pd.Timestamp(year=2018, month=10, day=1, tz="utc")
val_end = pd.Timestamp(year=2018, month=11, day=1, tz="utc")


train_df = load_df.loc[:train_end]

val_df = load_df.loc[train_end:val_end]

test_df = load_df.loc[val_end:]


print(train_df.shape)
print(val_df.shape)
print(test_df.shape)


FEATURES = [c for c in load_df.columns if c != TARGET]

FEATURES


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_val = val_df[FEATURES]
y_val = val_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)

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


---


from openstef.data_classes.prediction_job import PredictionJobDataClass

pj = PredictionJobDataClass(
    id=287,
    model="xgb",
    resolution_minutes=15,
    forecast_type="demand",
    quantiles=[10, 30, 50, 70, 90],
)


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


train_df.head()


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







