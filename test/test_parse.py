# Copyright 2023 Newmarket Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
import pandas as pd
from scrape_fresh_standard_code.spiders.fresh_standard_code_spider import FreshStandardCodeSpider
from gtin import GTIN


def test_cleansing_dataframe1():
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx")
    spider = FreshStandardCodeSpider()
    df = spider.cleansing_dataframe(df)
    print(df)


def assert_item(items, fresh_standard_code, name, header, vegefru_code, growing_method, volume, size, check_digit):
    item = items[fresh_standard_code]
    assert item["standard_name"] == name
    assert item["vegefru_code"] == vegefru_code
    assert item["growing_method"] == growing_method
    assert item["volume"] == volume
    assert item["size"] == size
    assert item["check_digit"] == check_digit
    assert item["fresh_standard_code"] == fresh_standard_code

    # GTINのチェックディジットを計算させてcheck_digitを検証する
    assert int(tuple(GTIN(raw=item["fresh_standard_code"][:-1]))[-1]) == check_digit


def test_parse_vegefru_item1():
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx")
    spider = FreshStandardCodeSpider()
    FreshStandardCodeSpider.dist_path = "./test_parse/dist"
    df = spider.cleansing_dataframe(df)
    items = spider.parse_vegefru_items(df)
    spider.write_json("fresh_standard_codes.json", items)

    assert_item(items, "4922301000007", "だいこん", 4922, 30100, 0, 0, 0, 7)
    assert_item(items, "4922396400997", "ルジナ", 4922, 39640, 0, 9, 9, 7)
    print("count: {}".format(len(items)))

def test_parse_vegefru_item2():
    # モラードバナナのコード値のミスを補正する
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx", sheet_name="商品コードリスト(果物)")
    spider = FreshStandardCodeSpider()
    FreshStandardCodeSpider.dist_path = "./test_parse/dist"
    df = spider.cleansing_dataframe(df)
    items = spider.parse_vegefru_items(df)
    spider.write_json("fresh_standard_codes.json", items)

    assert_item(items, "4922491626001", "モラードバナナ", 4922, 49162, 6, 0, 0, 1)
    assert_item(items, "4922491626995", "モラードバナナ", 4922, 49162, 6, 9, 9, 5)
#    assert_item(items, "4922492626995", "モラードバナナ", 4922, 49262, 6, 9, 9, 5) # 49262の場合、check digitは4が正しい
    print("count: {}".format(len(items)))


def test_generatee_vegefru_pvs_map1():
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx")
    spider = FreshStandardCodeSpider()
    FreshStandardCodeSpider.dist_path = "./test_parse/dist"
    df = spider.cleansing_dataframe(df)
    items = spider.parse_vegefru_items(df)

    vegefru_pvs_map = spider.generate_vegefru_pvs_map(items)
    spider.write_json("vegefru_pvs_map.json", vegefru_pvs_map)


def test_generate_volume_enums1():
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx")
    spider = FreshStandardCodeSpider()
    FreshStandardCodeSpider.dist_path = "./test_parse/dist"
    df = spider.cleansing_dataframe(df)
    items = spider.parse_vegefru_items(df)

    enums = spider.generatee_volume_enums(items)
    spider.write_json("volume_enums.json", enums)

    assert enums[30100][1] == '原体(レギュラー)'
    assert enums[30100][2] == '1/2本'
    assert enums[30100][3] == '1/3本'
    assert enums[30100][9] == '原体(その他)'
    assert enums[39640][1] == '原体(レギュラー)'
    assert enums[39640][9] == '原体(その他)'

    all_enums = set()
    for enum_map in enums.values():
        for k, v in enum_map.items():
            all_enums.add("{}:{}".format(k, v))
    print(all_enums)


def test_generate_size_enums1():
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx")
    spider = FreshStandardCodeSpider()
    FreshStandardCodeSpider.dist_path = "./test_parse/dist"
    df = spider.cleansing_dataframe(df)
    items = spider.parse_vegefru_items(df)

    enums = spider.generate_size_enums(items)
    spider.write_json("size_enums.json", enums)

    assert not 1 in enums[30100].keys()
    assert enums[30100][2] == 'S'
    assert enums[30100][3] == 'M'
    assert enums[30100][4] == 'L'
    assert enums[30100][5] == '2L'
    assert enums[30100][6] == '3L'
    assert enums[30100][7] == '4L以上'
    assert enums[30100][9] == 'その他'
    assert not 0 in enums[30100].keys()
    assert not 1 in enums[39640].keys()
    assert enums[39640][9] == 'その他'
    assert not 0 in enums[39640].keys()

    all_enums = set()
    for enum_map in enums.values():
        for k, v in enum_map.items():
            all_enums.add("{}:{}".format(k, v))
    print(all_enums)


def test_generate_growing_method_enums1():
    df = pd.read_excel("./test_parse/seikalist20230401.xlsx")
    spider = FreshStandardCodeSpider()
    FreshStandardCodeSpider.dist_path = "./test_parse/dist"
    df = spider.cleansing_dataframe(df)
    items = spider.parse_vegefru_items(df)

    enums = spider.generate_growing_method_enums(items)
    spider.write_json("growing_method_enums.json", enums)

    assert not 6 in enums[30100].keys()
    assert enums[30200][6] == '輸入'
    assert enums[34400][4] == 'ハウス'
    assert enums[34400][6] == '輸入'

    all_enums = set()
    for enum_map in enums.values():
        for k, v in enum_map.items():
            all_enums.add("{}:{}".format(k, v))
    print(all_enums)
