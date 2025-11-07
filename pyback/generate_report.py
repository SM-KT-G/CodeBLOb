import pandas as pd
import matplotlib.pyplot as plt
import os

print("Starting report generation...")

# 1. 샘플 데이터 생성 (데이터베이스나 API에서 가져왔다고 가정)
data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Sales': [150, 220, 180, 300, 280, 400]
}

# 2. Pandas DataFrame으로 변환
df = pd.DataFrame(data)

# 3. 데이터 시각화 (막대 차트)
plt.figure(figsize=(10, 6))  # 그래프 크기 설정
plt.bar(df['Month'], df['Sales'], color='skyblue')

# 4. 차트 제목 및 레이블 추가
plt.title('Monthly Sales Report', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Sales (USD)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 5. 생성된 차트를 이미지 파일로 저장
output_filename = 'sales_report.png'
plt.savefig(output_filename)

print(f"Successfully generated and saved report to '{output_filename}'")
print(f"Report saved in: {os.path.abspath(output_filename)}")
