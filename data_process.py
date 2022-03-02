# -*- coding:utf-8 -*-
"""
@Time: 2022/03/01 23:16
@Author: KI
@File: data_process.py
@Motto: Hungry And Humble
"""
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CNN_PATH = 'model/CNN.pkl'


def load_data(file_name):
    df = pd.read_csv('data/' + file_name, encoding='gbk')
    columns = df.columns
    df.fillna(df.mean(), inplace=True)
    MAX = np.max(df[columns[1]])
    MIN = np.min(df[columns[1]])
    df[columns[1]] = (df[columns[1]] - MIN) / (MAX - MIN)

    return df, MAX, MIN


def nn_seq(file_name, B):
    print('data processing...')
    data, MAX, MIN = load_data(file_name)
    load = data[data.columns[1]]
    load = load.tolist()
    load = torch.FloatTensor(load).view(-1)
    data = data.values.tolist()
    seq = []
    for i in range(len(data) - 30):
        train_seq = []
        train_label = []
        for j in range(i, i + 24):
            train_seq.append(load[j])
        for c in range(2, 8):
            train_seq.append(data[i + 24][c])
        train_label.append(load[i + 24])
        train_seq = torch.FloatTensor(train_seq).view(-1)
        train_label = torch.FloatTensor(train_label).view(-1)
        seq.append((train_seq, train_label))
    # print(seq[:5])

    Dtr = seq[0:int(len(seq) * 0.7)]
    Dte = seq[int(len(seq) * 0.7):len(seq)]

    train_len = int(len(Dtr) / B) * B
    test_len = int(len(Dte) / B) * B
    Dtr, Dte = Dtr[:train_len], Dte[:test_len]

    train = MyDataset(Dtr)
    test = MyDataset(Dte)

    Dtr = DataLoader(dataset=train, batch_size=B, shuffle=True, num_workers=0)
    Dte = DataLoader(dataset=test, batch_size=B, shuffle=True, num_workers=0)

    return Dtr, Dte, MAX, MIN


class MyDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)


def get_mape(x, y):
    """
    :param x:true
    :param y:pred
    :return:MAPE
    """
    return np.mean(np.abs((x - y) / x))
