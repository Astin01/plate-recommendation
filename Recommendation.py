import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Excel 파일 경로
EXCEL_FILE_PATH = 'restaurant_scores.xlsx'


def load_restaurant_data(file_path, category=None):
    # Excel 파일을 데이터프레임으로 읽기
    df = pd.read_excel(file_path)

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

# 추천 엔드포인트


@app.route('/recommend/<string:category>', methods=['POST'])
def recommend(category):
    # 사용자 선호도 데이터를 JSON 형식으로 받기
    user_preferences_data = request.json

    # 사용자 선호도를 벡터로 변환
    user_vector = np.array([
        user_preferences_data['taste'],
        user_preferences_data['price'],
        user_preferences_data['service'],
        user_preferences_data['fresh'],
        user_preferences_data['interior'],
        user_preferences_data['quantity'],
        user_preferences_data['group'],
        user_preferences_data['special'],
        user_preferences_data['clean']
    ])

    # 음식점 데이터를 Excel에서 불러오기 (카테고리에 맞춰서 필터링)
    restaurant_scores = load_restaurant_data(EXCEL_FILE_PATH, category)

    # 음식점 정보를 벡터로 변환
    restaurant_vectors = {
        restaurant: np.array([features['taste'], features['price'],
                             features['service'], features['fresh'],
                             features['interior'], features['quantity'],
                             features['group'], features['special'],
                             features['clean']])
        for restaurant, features in restaurant_scores.items()
    }

    # 코사인 유사도 계산
    scores = {}
    for restaurant, vector in restaurant_vectors.items():
        similarity = cosine_similarity([user_vector], [vector])[0][0]
        scores[restaurant] = similarity

    # 유사도에 따라 추천 음식점 정렬
    recommended_restaurants = sorted(
        scores.items(), key=lambda x: x[1], reverse=True)

   # 원하는 JSON 형식으로 변환
    result = [
        {"name": restaurant, "score": score}
        for restaurant, score in recommended_restaurants
    ]

    # 결과 JSON 형식으로 반환
    return jsonify(restaurantRecommendList=result)


# 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
