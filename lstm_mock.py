import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from unittest import mock

# 1. LSTM 모델 클래스 정의
def build_lstm_model(input_shape, output_dim=1):
    model = keras.Sequential([
        layers.LSTM(16, input_shape=input_shape),
        layers.Dense(output_dim)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# 2. 임의 데이터 생성 (시계열 데이터)
def generate_dummy_data(num_samples=100, timesteps=10, features=1):
    X = np.random.rand(num_samples, timesteps, features)
    y = np.random.rand(num_samples, 1)
    return X, y

# 3. 실제 LSTM 모델 학습/예측 예시
def real_lstm_example():
    X, y = generate_dummy_data()
    model = build_lstm_model(input_shape=(X.shape[1], X.shape[2]))
    model.fit(X, y, epochs=2, batch_size=8, verbose=0)
    preds = model.predict(X[:5])
    print('실제 LSTM 예측 결과:', preds)

# 4. mock을 활용한 LSTM 모델 테스트 구조 예시
def mock_lstm_example():
    # LSTM 모델을 mock 객체로 대체
    mock_model = mock.MagicMock()
    mock_model.predict.return_value = np.array([[0.5], [0.5], [0.5], [0.5], [0.5]])
    X, _ = generate_dummy_data(num_samples=5)
    preds = mock_model.predict(X)
    print('Mock LSTM 예측 결과:', preds)

if __name__ == "__main__":
    print('--- 실제 LSTM 동작 예시 ---')
    real_lstm_example()
    print('\n--- Mock LSTM 테스트 예시 ---')
    mock_lstm_example()