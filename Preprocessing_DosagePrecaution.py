import pandas as pd
import re

# CSV 불러오기
file_path = "file_path"
df = pd.read_csv(file_path, encoding="cp949")

# 필요 없는 컬럼 제거
cols_to_drop = ['급여구분', '공고번호', '공고일자']
for col in cols_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])

# 필요한 컬럼만 유지
cols_keep = ['제품코드', '제품명', '성분명', '1일최대투여량', '1일최대 투여기준량', '점검기준 성분함량 (총함량)']
df = df[cols_keep]

# 전처리 함수 정의
def split_ingredients(row):
    raw = str(row['성분명'])
    clean = raw.replace('with', '/')
    parts = [x.strip() for x in clean.split('/')]
    result = []
    for p in parts:
        if '(as' in p:
            inside = re.search(r'\(as ([^)]+)\)', p)
            if inside:
                result.append(inside.group(1).strip())
        else:
            if '외' in p:
                p = re.split(r'외', p)[0].strip()
            result.append(p.strip())
    return result

# 분리된 성분별로 행 생성 *propofol 제거
rows = []
for _, row in df.iterrows():
    ingredients = split_ingredients(row)
    for ingredient in ingredients:
        if 'propofol' in ingredient.lower() or '프로포폴' in ingredient:
            continue
        rows.append({
            'product_code': row['제품코드'],
            'product_name': row['제품명'],
            'ingredient_name': ingredient,
            'max_daily_dose': row['1일최대투여량'],
            'max_daily_dose_value': row['1일최대 투여기준량'],
            'unit_dose': row['점검기준 성분함량 (총함량)']
        })

df_clean = pd.DataFrame(rows)

output_path = "전처리_용량주의약물.csv"
df_clean.to_csv(output_path, index=False, encoding="utf-8-sig")

print("저장되었습니다.")
print(df_clean.head())