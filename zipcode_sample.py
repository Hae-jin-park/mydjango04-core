# zipcode_sample_download.py

import os
import csv
from typing import Dict, Iterator, Tuple
from urllib.request import urlretrieve
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()


def get_code_and_name_from_csv(zipcode_csv_path: str) -> Iterator[Tuple[str, str]]:
    """CSV 파일에서 우편번호, 시도, 시군구, 도로명을 읽어서, 우편번호와 주소를 생성합니다.
    :param zipcode_csv_path: 우편번호 CSV 파일 경로
    :return: 우편번호, 주소 튜플을 생성(yield)합니다.
    """

    with open(zipcode_csv_path, "rt", encoding="utf-8-sig") as csvfile:
        # DictReader를 사용하면 첫 줄을 컬럼명으로 자동 처리합니다. 우편번호 CSV 파일은 구분자가 | 입니다.
        csv_reader = csv.DictReader(csvfile, delimiter="|")
        row: Dict
        for row in csv_reader:
            if row["시군구"] == "연수구" :
                code = row["우편번호"]
                name = "인천시 {시군구} {도로명} {건물번호본번} {시군구용건물명} ({법정동명})".format(**row)
                yield code, name


def main():
    # 파이썬으로 샘플을 다운받아 csv_path 경로에 저장합니다. (원본: 531,487줄)
    sample_csv_url = "https://media.githubusercontent.com/media/Hae-jin-park/mydjango04-core/main/data/%EC%9D%B8%EC%B2%9C%EA%B4%91%EC%97%AD%EC%8B%9C.txt"
    csv_path = "shop/assets/zipcode_db/인천.txt"  # 원본: 531,487줄

    os.makedirs(
        os.path.dirname(csv_path), exist_ok=True
    )  # 파일을 저장할 폴더를 생성해줍니다.
    urlretrieve(
        sample_csv_url, csv_path
    )  # sample_csv_url 경로에서 파일을 다운받아, 지정 경로에 저장합니다.

    generator = get_code_and_name_from_csv(csv_path)

    for row in generator:
        print(row)


if __name__ == "__main__":
    main()
