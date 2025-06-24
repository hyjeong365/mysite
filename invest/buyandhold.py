import pandas as pd
from datetime import datetime
import numpy as np


# - 매개변수의 개수는 4개?
#     - 데이터프레임(_df) -> 필수
#     - 투자 시작 시간 (매수)(_start) -> '2010-01-01' 기본값 설정
#     - 투자 종료 시간 (매도)(_end) -> 현재 시간 기본값
#     - 특정 컬럼 선택 -> (_col) -> 'Adj Close' 기본값
def bnh(
        _df,
        _start='2010-01-01', 
        _end= datetime.now(),
        _col='Adj Close'
):
    
    # 데이터프레임 복사본 생성  
    df = _df.copy()


    # Date가 컬럼에 존재하면 Date를 인덱스로 변경
    if 'Date' in df.columns:
        df.set_index('Date', inplace=True)

    #인덱스를 시계열 데이터로 변경
    df.index = pd.to_datetime(df.index)

    # 결측치와 무한대 값 제거
    flag = df.isin ([np.nan, np.inf, -np.inf]).any(axis=1)
    df = df.loc[~flag, ]

    #_start와 _end를 기준으로 인덱스 필터링을 하고 _col을 기준으로 컬럼의 필터링을 해준다. 
    # (시도하고 문제가 발생한다면 인자값이 잘못되었다 출력하고 함수 종료(return data주는 것) ex.문자열 컬럼의 이름이 잘못되었을 수도 있음)
    try:
        df = df.loc[_start : _end, [_col]]
    except Exception as e:
        print(e)
        print('입력된 인자값이 잘못되었습니다. ')
        return ""
    
    #일별수익률
    df['rtn'] = (df[_col].pct_change() + 1).fillna(1)
    #누적 수익률 계산하여 acc_rtn 컬럼에 대입
    df['acc_rtn'] = df['rtn'].cumprod()
    acc_rtn = df.iloc[-1, -1]
    #결과 데이터프레임과 최종 누적수익률을 되돌려준다
    return df, acc_rtn

