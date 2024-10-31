import pandas as pd
import numpy as np
import requests
from lightfm import LightFM
from lightfm.data import Dataset
from scipy.sparse import csr_matrix

# 1. 음식점 데이터 로드 (엑셀 파일에서)
def load_restaurant_data(filepath):
    df = pd.read_excel(filepath)
    
    # 비중 계산 (각 항목 / 총점)
    for col in ["taste", "price", "service", "fresh", "interior", "quantity", "group", "special", "clean"]:
        df[col + "_ratio"] = df[col] / df["total"]
    
    return df

# 2. 사용자 선호도 로드 (REST API 요청)
def fetch_user_preferences(api_url, user_id):
    response = requests.get(f"{api_url}/user/preferences/{user_id}")
    user_preferences = response.json()
    return user_preferences

# 3. 데이터셋 준비
def prepare_dataset(df, user_preferences):
    # LightFM Dataset 객체 생성
    dataset = Dataset()
    
    # 사용자 및 음식점 추가
    dataset.fit(
        users=[user_preferences['user_id']],
        items=df['name'].tolist(),
        user_features=list(user_preferences.keys()),
        item_features=df.columns[1:-1]  # 비중 항목만 사용 (총점 제외)
    )
    
    # 상호작용 행렬 구성 (사용자가 각 음식점에 대한 점수를 매긴 것으로 가정)
    interactions, _ = dataset.build_interactions(
        [(user_preferences['user_id'], item, user_preferences.get(item)) for item in df['name']]
    )
    
    # 사용자 피처와 음식점 피처 구성
    user_features = dataset.build_user_features(
        [(user_preferences['user_id'], [f"{k}_{v}" for k, v in user_preferences.items()])]
    )
    
    item_features = dataset.build_item_features(
        [(row['name'], [f"{col}_{row[col + '_ratio']}" for col in ["taste", "price", "service", "fresh", "interior", "quantity", "group", "special", "clean"]])
         for _, row in df.iterrows()]
    )
    
    return interactions, user_features, item_features

# 4. LightFM 모델 학습 및 추천
def train_and_recommend(interactions, user_features, item_features, user_id, item_labels):
    model = LightFM(loss='warp')
    model.fit(interactions, user_features=user_features, item_features=item_features, epochs=30, num_threads=4)
    
    # 예측 수행
    scores = model.predict(user_id, np.arange(len(item_labels)), user_features=user_features, item_features=item_features)
    
    # 추천 리스트 정렬
    top_items = sorted(zip(scores, item_labels), reverse=True)
    return top_items[:10]  # 상위 10개 추천

# 실행 함수
def main():
    # 엑셀 파일 경로 및 API URL 설정
    excel_filepath = 'restaurants_data.xlsx'  # 예: restaurants_data.xlsx
    api_url = 'https://example.com/api'  # 실제 API 엔드포인트
    
    # 데이터 로드
    df = load_restaurant_data(excel_filepath)
    
    # 특정 사용자 ID
    user_id = 1
    user_preferences = fetch_user_preferences(api_url, user_id)
    
    # 데이터셋 준비
    interactions, user_features, item_features = prepare_dataset(df, user_preferences)
    
    # 추천 실행
    top_recommendations = train_and_recommend(interactions, user_id, item_labels=df['name'].tolist())
    
    # 추천 결과 출력
    print("추천 음식점 리스트:")
    for score, name in top_recommendations:
        print(f"{name}: {score:.2f}")

# 프로그램 실행
if __name__ == "__main__":
    main()
