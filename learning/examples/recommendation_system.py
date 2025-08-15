"""
机器学习示例：旅游景点推荐系统

这个示例展示了如何使用机器学习技术构建一个简单的旅游景点推荐系统。
涵盖了数据处理、特征工程、模型训练和预测等步骤。
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

class TravelRecommendationML:
    """旅游推荐机器学习系统"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        
    def generate_sample_data(self, n_samples=1000):
        """生成示例旅游数据"""
        np.random.seed(42)
        
        # 景点类型
        categories = ['历史文化', '自然风光', '现代都市', '美食体验', '休闲娱乐']
        
        # 城市
        cities = ['北京', '上海', '杭州', '成都', '西安', '深圳', '广州', '苏州']
        
        data = {
            'city': np.random.choice(cities, n_samples),
            'category': np.random.choice(categories, n_samples),
            'price_level': np.random.choice([1, 2, 3, 4], n_samples, p=[0.3, 0.4, 0.2, 0.1]),
            'distance_from_center': np.random.exponential(8, n_samples) + 1,  # 公里
            'visitor_count': np.random.poisson(2000, n_samples) + 500,
            'opening_hours': np.random.uniform(8, 12, n_samples),  # 开放小时数
            'season_factor': np.random.uniform(0.6, 1.0, n_samples),  # 季节因子
            'accessibility_score': np.random.uniform(0.5, 1.0, n_samples),  # 交通便利度
        }
        
        df = pd.DataFrame(data)
        
        # 基于特征生成评分（添加一些合理的关系）
        rating_base = 3.5
        rating_base += (df['price_level'] - 2.5) * 0.2  # 价格影响
        rating_base += (1 / (1 + df['distance_from_center'] / 10)) * 0.5  # 距离影响
        rating_base += df['season_factor'] * 0.8
        rating_base += df['accessibility_score'] * 0.6
        rating_base += np.random.normal(0, 0.3, n_samples)  # 随机噪声
        
        df['rating'] = np.clip(rating_base, 1.0, 5.0)
        
        return df
        
    def preprocess_data(self, df):
        """数据预处理"""
        df_processed = df.copy()
        
        # 对类别特征进行编码
        categorical_features = ['city', 'category']
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                df_processed[feature + '_encoded'] = self.label_encoders[feature].fit_transform(df[feature])
            else:
                df_processed[feature + '_encoded'] = self.label_encoders[feature].transform(df[feature])
        
        # 选择特征
        feature_cols = ['city_encoded', 'category_encoded', 'price_level', 
                       'distance_from_center', 'visitor_count', 'opening_hours',
                       'season_factor', 'accessibility_score']
        
        self.feature_names = feature_cols
        return df_processed[feature_cols]
        
    def train(self, df):
        """训练模型"""
        print("开始训练模型...")
        
        # 预处理数据
        X = self.preprocess_data(df)
        y = df['rating']
        
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 标准化特征
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 训练模型
        self.model.fit(X_train_scaled, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test_scaled)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2_score = self.model.score(X_test_scaled, y_test)
        
        print(f"模型训练完成！")
        print(f"测试集RMSE: {rmse:.4f}")
        print(f"测试集R²得分: {r2_score:.4f}")
        
        # 特征重要性
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\n特征重要性排序:")
        for _, row in feature_importance.head().iterrows():
            print(f"{row['feature']}: {row['importance']:.4f}")
            
        return rmse, r2_score
        
    def predict_rating(self, city, category, price_level, distance_from_center, 
                      visitor_count, opening_hours, season_factor, accessibility_score):
        """预测景点评分"""
        
        # 创建输入数据
        input_data = pd.DataFrame({
            'city': [city],
            'category': [category],
            'price_level': [price_level],
            'distance_from_center': [distance_from_center],
            'visitor_count': [visitor_count],
            'opening_hours': [opening_hours],
            'season_factor': [season_factor],
            'accessibility_score': [accessibility_score]
        })
        
        try:
            # 预处理
            X_input = self.preprocess_data(input_data)
            X_input_scaled = self.scaler.transform(X_input)
            
            # 预测
            predicted_rating = self.model.predict(X_input_scaled)[0]
            
            return max(1.0, min(5.0, predicted_rating))  # 确保在1-5范围内
            
        except Exception as e:
            print(f"预测出错: {e}")
            return None
            
    def recommend_improvements(self, current_features):
        """基于模型推荐改进建议"""
        suggestions = []
        
        # 获取特征重要性
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        # 基于重要特征给出建议
        if importance.get('accessibility_score', 0) > 0.15:
            if current_features.get('accessibility_score', 0.5) < 0.8:
                suggestions.append("改善交通便利性，增加公共交通选项")
                
        if importance.get('distance_from_center', 0) > 0.1:
            if current_features.get('distance_from_center', 10) > 15:
                suggestions.append("考虑在市中心附近增加分店或服务点")
                
        if importance.get('opening_hours', 0) > 0.1:
            if current_features.get('opening_hours', 8) < 10:
                suggestions.append("延长营业时间，提供更灵活的服务")
                
        return suggestions

def main():
    """主函数演示"""
    print("=== 旅游景点推荐系统机器学习示例 ===\n")
    
    # 创建推荐系统
    recommender = TravelRecommendationML()
    
    # 生成示例数据
    print("1. 生成示例数据...")
    df = recommender.generate_sample_data(1000)
    print(f"生成了 {len(df)} 条数据")
    print(f"平均评分: {df['rating'].mean():.2f}")
    print(f"评分范围: {df['rating'].min():.2f} - {df['rating'].max():.2f}")
    
    # 训练模型
    print("\n2. 训练模型...")
    rmse, r2_score = recommender.train(df)
    
    # 预测示例
    print("\n3. 预测示例...")
    
    test_cases = [
        {
            'name': '北京故宫',
            'city': '北京',
            'category': '历史文化',
            'price_level': 3,
            'distance_from_center': 2.0,
            'visitor_count': 50000,
            'opening_hours': 8,
            'season_factor': 0.9,
            'accessibility_score': 0.95
        },
        {
            'name': '郊外小景点',
            'city': '杭州',
            'category': '自然风光',
            'price_level': 1,
            'distance_from_center': 25.0,
            'visitor_count': 200,
            'opening_hours': 6,
            'season_factor': 0.7,
            'accessibility_score': 0.4
        }
    ]
    
    for case in test_cases:
        name = case.pop('name')
        predicted_rating = recommender.predict_rating(**case)
        
        if predicted_rating is not None:
            print(f"\n{name}:")
            print(f"  预测评分: {predicted_rating:.2f}")
            
            # 给出改进建议
            suggestions = recommender.recommend_improvements(case)
            if suggestions:
                print("  改进建议:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
            else:
                print("  - 当前配置良好，无需特别改进")
    
    print("\n=== 系统演示完成 ===")

if __name__ == "__main__":
    main()