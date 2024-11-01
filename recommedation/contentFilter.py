import pandas as pd
import numpy as np

# 음식점 데이터 로드
# restaurants = pd.read_excel('restaurants.xlsx')

# 사용자 선호도 (예시)
user_preferences = {
    'taste': 0.4,
    'price': 0.25,
    'service': 0.2,
    'fresh': 0.1,
    'interior': 0.05
}

EXCEL_FILE_PATH = 'restaurant_scores.csv'


def load_restaurant_data(file_path, category=None):
    # Excel 파일을 데이터프레임으로 읽기
    df = pd.read_csv(file_path)

    print(df.columns)
    # 특정 카테고리만 필터링
    if category:
        df = df[df['category'] == category]

    # 데이터프레임을 딕셔너리로 변환
    restaurant_scores = {
        row['name']: {
            'taste': row['taste'],
            'price': row['price'],
            'service': row['service'],
            'fresh': row['fresh'],
            'interior': row['interior'],
            'quantity': row['quantity'],
            'group': row['group'],
            'special': row['special'],
            'clean': row['clean']
        }
        for _, row in df.iterrows()
    }
    return restaurant_scores


restaurant_scores = load_restaurant_data(EXCEL_FILE_PATH, "ko")

# 음식점 특성 (예시)
restaurant_scores = {
    '맛닭꼬': {'taste': 375, 'price': 147, 'service': 100, 'fresh': 70, 'interior': 64},
    '한식당': {'taste': 450, 'price': 200, 'service': 80, 'fresh': 90, 'interior': 75}
}

# 추천 점수 계산
def calculate_scores(user_preferences, restaurant_scores):
    scores = {}
    for restaurant, features in restaurant_scores.items():
        score = sum(user_preferences[key] * features[key]
                    for key in user_preferences)
        scores[restaurant] = score
    return scores


# 추천 음식점 목록 생성
scores = calculate_scores(user_preferences, restaurant_scores)

# 상위 추천 음식점 출력
recommended_restaurants = sorted(
    scores.items(), key=lambda x: x[1], reverse=True)
print("추천 음식점:")
for restaurant, score in recommended_restaurants:
    print(f"{restaurant}: {score:.2f}")
