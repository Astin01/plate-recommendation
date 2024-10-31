import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Spring 서버의 사용자 선호도 API URL
API_URL = "http://your-spring-server-url/api/user/preferences"


def fetch_user_preferences(api_url, user_id):
    response = requests.get(f"{api_url}/{user_id}")
    response.raise_for_status()  # 오류 발생 시 예외 처리
    return response.json()       # JSON 형식의 사용자 선호도 반환
# 사용자 선호도와 음식점 정보로 추천 점수를 계산하는 함수


def recommend_restaurants(user_id, api_url, restaurant_scores):
    # API를 통해 사용자 선호도 데이터 가져오기
    user_preferences_data = fetch_user_preferences(api_url, user_id)

    # 사용자 선호도를 벡터로 변환
    user_vector = np.array([
        user_preferences_data['taste'],
        user_preferences_data['price'],
        user_preferences_data['service'],
        user_preferences_data['fresh'],
        user_preferences_data['interior']
    ])

    # 음식점 정보를 순서에 맞게 벡터로 변환
    restaurant_vectors = {
        restaurant: np.array([features['taste'], features['price'],
                             features['service'], features['fresh'], features['interior']])
        for restaurant, features in restaurant_scores.items()
    }

    # 코사인 유사도 계산 함수
    scores = {}
    for restaurant, vector in restaurant_vectors.items():
        similarity = cosine_similarity([user_vector], [vector])[0][0]
        scores[restaurant] = similarity

    # 유사도에 따른 추천 음식점 정렬
    recommended_restaurants = sorted(
        scores.items(), key=lambda x: x[1], reverse=True)

    # 추천 결과 출력
    print("추천 음식점:")
    for restaurant, score in recommended_restaurants:
        print(f"{restaurant}: {score:.4f}")


restaurant_scores = {
    '맛닭꼬': {'taste': 375, 'price': 147, 'service': 100, 'fresh': 70, 'interior': 64},
    '한식당': {'taste': 450, 'price': 200, 'service': 80, 'fresh': 90, 'interior': 75},
}

# 사용자 ID와 함께 추천 함수 실행
user_id = 123
recommend_restaurants(user_id, API_URL, restaurant_scores)
