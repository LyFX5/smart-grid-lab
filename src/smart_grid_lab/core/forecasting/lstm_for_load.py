import numpy as np
from torch.utils.data import Dataset
import torch.nn as nn


class ResidualDataset(Dataset):

    def __init__(self, residuals, exog, window):

        self.X = []
        self.y = []

        for i in range(len(residuals) - window):
            x = np.hstack(
                [residuals[i : i + window, None], exog[i : i + window]]
            )
            self.X.append(x.astype(np.float32))
            self.y.append(np.float32(residuals[i + window]))

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class ResidualLSTM(nn.Module):

    def __init__(self, input_size, hidden=64):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return self.head(h[-1])


"""
peace of code with onehote encoding (may be usefull)

from sklearn.preprocessing import OneHotEncoder

df = df.copy()
df = df.sort_values("timestamp")
df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour

encoder = OneHotEncoder(sparse_output=False)
hour = encoder.fit_transform(df[["hour"]])

hour_cols=[f"hour_{i}" for i in range(hour.shape[1])]
hour_df=pd.DataFrame(hour,columns=hour_cols,index=df.index)

df=pd.concat([df,hour_df],axis=1)
df=df.set_index("timestamp")
"""
