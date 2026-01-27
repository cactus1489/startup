import pandas as pd
import sys

def check_encoding(file_path):
    encodings = ['utf-8', 'cp949', 'utf-8-sig', 'euc-kr']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, nrows=5)
            print(f"SUCCESS:{enc}")
            print(",".join(df.columns.tolist()))
            return enc
        except Exception as e:
            pass
    print("FAIL: No viable encoding found")
    return None

if __name__ == "__main__":
    check_encoding('youth_startup/서울시_상권분석서비스(추정매출-상권)_2020-2025.csv')
