import numpy as np
import pandas as pd
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping

LOOK_BACK = 20
TRAIN_RATIO = 0.8
EPOCHS = 100
BATCH_SIZE = 32

stock_name = {
    "apple": "F:/apple_stock.csv"
}

model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

def get_model_path(stock):
    return os.path.join(model_dir, f"{stock}_lstm_model.h5")

def get_scaler_path(stock):
    return os.path.join(model_dir, f"{stock}_scaler.pkl")

def get_training_data_lstm(stock, look_back):
    if stock not in stock_name:
        return "no data for this stock"

    file = stock_name[stock]
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.dropna(inplace=True)

    # 日期处理
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format="%d-%b-%y", errors='coerce')
        df = df.dropna(subset=['Date'])  # 移除日期无法解析的行
        df.sort_values('Date', inplace=True)

    # 价格列取 Close（去重名列）
    if 'Close' not in df.columns:
        raise ValueError("CSV file must contain a 'Close' column.")

    prices = df['Close'].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    prices_scaled = scaler.fit_transform(prices.reshape(-1, 1))

    joblib.dump(scaler, get_scaler_path(stock))  # 保存 scaler

    def create_sequences(data, look_back):
        X, y = [], []
        for i in range(len(data) - look_back):
            X.append(data[i:i + look_back, 0])
            y.append(data[i + look_back, 0])
        return np.array(X), np.array(y)

    X_all, y_all = create_sequences(prices_scaled, look_back)
    X_all = X_all.reshape((X_all.shape[0], X_all.shape[1], 1))

    train_size = int(len(X_all) * TRAIN_RATIO)
    X_train, X_test = X_all[:train_size], X_all[train_size:]
    y_train, y_test = y_all[:train_size], y_all[train_size:]

    return X_train, X_test, y_train, y_test

def train(X_train, y_train, X_test, y_test, stock):
    model = Sequential()
    model.add(LSTM(200, return_sequences=True, input_shape=(LOOK_BACK, 1)))
    model.add(Dropout(0.1))
    model.add(LSTM(100, return_sequences=False))
    model.add(Dropout(0.1))
    model.add(Dense(1, activation="linear"))

    model.compile(optimizer=Adam(learning_rate=0.0005), loss='mean_squared_error')

    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, verbose=1)
    early_stop = EarlyStopping(monitor='val_loss', patience=12, verbose=1, restore_best_weights=True)

    model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_test, y_test),
        callbacks=[reduce_lr, early_stop],
        verbose=1
    )

    model.save(get_model_path(stock))  # 保存模型

    # 加载 scaler
    scaler = joblib.load(get_scaler_path(stock))

    y_pred = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred)
    y_true = scaler.inverse_transform(y_test.reshape(-1, 1))

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    return rmse, mae, r2

def predict_next_price(stock):
    model_path = get_model_path(stock)
    scaler_path = get_scaler_path(stock)

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        return "Model or scaler not found. Please train the model first."

    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    df = pd.read_csv(stock_name[stock])
    df.columns = df.columns.str.strip()  # 清理空格
    if 'Close' not in df.columns:
        raise ValueError("CSV 文件中找不到 'Close' 列，请检查原始数据。")

    df.dropna(inplace=True)
    prices = df['Close'].values
    prices_scaled = scaler.transform(prices.reshape(-1, 1))

    latest_seq = prices_scaled[-LOOK_BACK:].reshape(1, LOOK_BACK, 1)
    pred = model.predict(latest_seq)
    next_price = scaler.inverse_transform(pred)[0][0]

    return round(next_price, 2)
