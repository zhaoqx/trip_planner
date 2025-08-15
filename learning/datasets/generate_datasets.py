"""
示例数据集生成器
生成用于机器学习练习的旅游相关数据集
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def generate_attractions_dataset(n_samples=500):
    """生成景点数据集"""
    np.random.seed(42)
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '西安', '苏州', '南京', '武汉']
    categories = ['历史文化', '自然风光', '现代都市', '美食体验', '休闲娱乐', '艺术展览']
    
    data = {
        'attraction_id': range(1, n_samples + 1),
        'name': [f"景点_{i}" for i in range(1, n_samples + 1)],
        'city': np.random.choice(cities, n_samples),
        'category': np.random.choice(categories, n_samples),
        'rating': np.random.normal(4.0, 0.8, n_samples).clip(1, 5),
        'price_level': np.random.choice([1, 2, 3, 4], n_samples, p=[0.3, 0.4, 0.2, 0.1]),
        'visitor_count_monthly': np.random.poisson(5000, n_samples) + 1000,
        'opening_hours': np.random.uniform(6, 12, n_samples),
        'distance_from_center': np.random.exponential(8, n_samples) + 1,
        'accessibility_score': np.random.uniform(0.3, 1.0, n_samples),
        'season_popularity': np.random.uniform(0.5, 1.0, n_samples),
        'has_parking': np.random.choice([True, False], n_samples, p=[0.7, 0.3]),
        'wifi_available': np.random.choice([True, False], n_samples, p=[0.8, 0.2]),
    }
    
    df = pd.DataFrame(data)
    
    # 添加一些逻辑关系
    df['rating'] = df['rating'] + (df['price_level'] - 2.5) * 0.1 + np.random.normal(0, 0.2, n_samples)
    df['rating'] = df['rating'].clip(1, 5).round(1)
    
    return df

def generate_user_reviews_dataset(n_reviews=2000):
    """生成用户评论数据集"""
    np.random.seed(42)
    
    positive_keywords = ['很好', '不错', '推荐', '漂亮', '值得', '满意', '喜欢']
    negative_keywords = ['一般', '失望', '不推荐', '太贵', '人多', '排队', '差']
    neutral_keywords = ['还行', '可以', '普通', '凑合', '一般般']
    
    data = {
        'review_id': range(1, n_reviews + 1),
        'attraction_id': np.random.randint(1, 501, n_reviews),  # 关联景点
        'user_id': np.random.randint(1, 1000, n_reviews),
        'rating': np.random.choice([1, 2, 3, 4, 5], n_reviews, p=[0.05, 0.1, 0.25, 0.35, 0.25]),
        'visit_date': [
            (datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
            for _ in range(n_reviews)
        ],
    }
    
    # 根据评分生成评论文本
    reviews = []
    for rating in data['rating']:
        if rating >= 4:
            keywords = positive_keywords
        elif rating <= 2:
            keywords = negative_keywords
        else:
            keywords = neutral_keywords
        
        # 简单的评论生成
        selected_words = np.random.choice(keywords, size=np.random.randint(2, 4), replace=True)
        review_text = f"这个地方{'，'.join(selected_words)}。"
        reviews.append(review_text)
    
    data['review_text'] = reviews
    
    return pd.DataFrame(data)

def generate_user_behavior_dataset(n_users=1000):
    """生成用户行为数据集"""
    np.random.seed(42)
    
    age_groups = ['18-25', '26-35', '36-45', '46-55', '55+']
    travel_purposes = ['旅游', '商务', '探亲', '学习']
    
    data = {
        'user_id': range(1, n_users + 1),
        'age_group': np.random.choice(age_groups, n_users),
        'gender': np.random.choice(['男', '女'], n_users),
        'travel_frequency': np.random.poisson(3, n_users) + 1,  # 每年旅行次数
        'avg_budget_per_trip': np.random.lognormal(7, 0.8, n_users).astype(int),  # 平均预算
        'preferred_travel_purpose': np.random.choice(travel_purposes, n_users),
        'mobile_user': np.random.choice([True, False], n_users, p=[0.85, 0.15]),
        'social_media_active': np.random.choice([True, False], n_users, p=[0.7, 0.3]),
        'loyalty_score': np.random.uniform(0, 1, n_users).round(2),
    }
    
    return pd.DataFrame(data)

def save_datasets():
    """保存所有数据集"""
    import os
    
    # 创建数据集目录
    dataset_dir = 'learning/datasets'
    os.makedirs(dataset_dir, exist_ok=True)
    
    # 生成并保存数据集
    attractions_df = generate_attractions_dataset()
    reviews_df = generate_user_reviews_dataset()
    users_df = generate_user_behavior_dataset()
    
    attractions_df.to_csv(f'{dataset_dir}/attractions.csv', index=False, encoding='utf-8')
    reviews_df.to_csv(f'{dataset_dir}/user_reviews.csv', index=False, encoding='utf-8')
    users_df.to_csv(f'{dataset_dir}/user_behavior.csv', index=False, encoding='utf-8')
    
    # 创建数据集描述文件
    dataset_info = {
        "datasets": {
            "attractions.csv": {
                "description": "景点信息数据集",
                "columns": {
                    "attraction_id": "景点ID",
                    "name": "景点名称",
                    "city": "所在城市", 
                    "category": "景点类别",
                    "rating": "平均评分",
                    "price_level": "价格等级(1-4)",
                    "visitor_count_monthly": "月访客量",
                    "opening_hours": "开放小时数",
                    "distance_from_center": "距市中心距离(公里)",
                    "accessibility_score": "交通便利度得分",
                    "season_popularity": "季节受欢迎度",
                    "has_parking": "是否有停车场",
                    "wifi_available": "是否提供WiFi"
                },
                "rows": len(attractions_df),
                "use_cases": ["推荐系统", "回归分析", "聚类分析"]
            },
            "user_reviews.csv": {
                "description": "用户评论数据集",
                "columns": {
                    "review_id": "评论ID",
                    "attraction_id": "景点ID",
                    "user_id": "用户ID",
                    "rating": "用户评分",
                    "visit_date": "访问日期",
                    "review_text": "评论文本"
                },
                "rows": len(reviews_df),
                "use_cases": ["情感分析", "文本挖掘", "NLP应用"]
            },
            "user_behavior.csv": {
                "description": "用户行为数据集",
                "columns": {
                    "user_id": "用户ID",
                    "age_group": "年龄组",
                    "gender": "性别",
                    "travel_frequency": "年旅行频次",
                    "avg_budget_per_trip": "平均旅行预算",
                    "preferred_travel_purpose": "主要旅行目的",
                    "mobile_user": "是否为移动端用户",
                    "social_media_active": "是否活跃于社交媒体",
                    "loyalty_score": "忠诚度得分"
                },
                "rows": len(users_df),
                "use_cases": ["用户画像", "分类预测", "客户细分"]
            }
        },
        "generated_date": datetime.now().strftime('%Y-%m-%d'),
        "notes": "这些是为机器学习学习生成的示例数据集，包含旅游相关的多种数据类型。"
    }
    
    with open(f'{dataset_dir}/dataset_info.json', 'w', encoding='utf-8') as f:
        json.dump(dataset_info, f, ensure_ascii=False, indent=2)
    
    print("数据集生成完成！")
    print(f"景点数据: {len(attractions_df)} 行")
    print(f"评论数据: {len(reviews_df)} 行") 
    print(f"用户数据: {len(users_df)} 行")
    print(f"文件保存在: {dataset_dir}/")

if __name__ == "__main__":
    save_datasets()