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


import logging
import numpy as np
import pandas as pd
import scrapy
import json
import os
from scrape_fresh_standard_code.items import FreshStndardCodesItem


class FreshStandardCodeSpider(scrapy.Spider):
    name = "fresh_standard_code_spider"
    allowed_domains = ["ofsi.or.jp"]
    start_urls = ["https://www.ofsi.or.jp/kyougikai/freshstandardcode/"]
    dist_path = "../dist"

    def cleansing_dataframe(self, df):
        """
        XLSXの形式のデータを綺麗にする

        :param df:
        :return: クレンジング済みのdf
        """
        # 先頭のヘッダ行を削除する
        df = df.iloc[2:]
        df.columns = ["_", "standard_name", "growing_method", "volume", "size",
                      "header_code", "vegefru_code", "p", "v", "s", "c/d", "memo"]

        # 数値フィールドは数値に変換しておく。
        df["header_code"] = df["header_code"].astype(int)
        df["vegefru_code"] = df["vegefru_code"].astype(int)
        df["p"] = df["p"].astype(int)
        df["v"] = df["v"].astype(int)
        df["s"] = df["s"].astype(int)
        df["c/d"] = df["c/d"].astype(int)

        # 全角英数字を半角英数字への変換と前後の空白の削除を行う
        ztoh = str.maketrans('０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ／',
                             '0123456789abcdefghijklmnopqrstuvwxyz/')

        # @formatter:off
        df["standard_name"]  = df["standard_name"] .apply(lambda x: x.strip().translate(ztoh) if not pd.isnull(x) else x)
        df["growing_method"] = df["growing_method"].apply(lambda x: x.strip().translate(ztoh) if not pd.isnull(x) else x)
        df["volume"]         = df["volume"]        .apply(lambda x: x.strip().translate(ztoh) if not pd.isnull(x) else x)
        df["size"]           = df["size"]          .apply(lambda x: x.strip().translate(ztoh) if not pd.isnull(x) else x)
        # @formatter:on

        return df

    def write_json(self, file_name, obj):
        dist_path = FreshStandardCodeSpider.dist_path
        if not os.path.exists(dist_path):
            os.mkdir(dist_path)
        with open("{}/{}".format(dist_path, file_name), "w") as f:
            json.dump(obj, f, indent=True, ensure_ascii=False)

    def parse(self, response):
        """
        スクレイピングのデータ処理を行う。

        :param response:
        :return:
        """
        # 青果標準商品コードのURLリンクを探索する
        next_page_url = None
        for sel in response.xpath('//tr/td/a[text() = "青果標準商品コード"]'):
            next_page_url = sel.xpath("@href").get()
            break
        self.log("青果標準商品コードのxlsxファイルへのリンク： " + next_page_url, logging.INFO)

        if next_page_url is None:
            raise Exception("青果標準商品コードのxlsxファイルへのリンクが見つかりませんでした。")

        dfs = []
        for sheet in ["商品コードリスト(野菜)", "商品コードリスト(果物)"]:
            # xlsxファイルをPandasで読み込む
            df = pd.read_excel(next_page_url, sheet_name=sheet)
            # オリジナルに近い状態で保存しておく
            # df.write_excel(FreshStandardCodeSpider.dist_path + "/fresh_standard_code_original.xlsx")
            # 加工しやすいようにデータをクレンジングする
            df = self.cleansing_dataframe(df)
            dfs.append(df)
        df = pd.concat(dfs)

        # データフレームからデータの形式に変換する
        fresh_standard_codes = self.parse_vegefru_items(df)

        item = FreshStndardCodesItem()
        item["fresh_standard_codes"] = fresh_standard_codes

        yield item

    def parse_vegefru_items(self, df):
        """
        PandasのDataFrameの形式からJSON向けのデータ形式へ変換する

        :param df:
        :return: { fresh_standard_code: {...} } のdict形式
        """
        fresh_standard_codes = {}
        for i, r in df.iterrows():
            try:
                item = {}
                item["standard_name"] = r["standard_name"]
                item["header_code"] = r["header_code"]
                item["vegefru_code"] = r["vegefru_code"]
                item["growing_method"] = r["p"]
                item["volume"] = r["v"]
                item["size"] = r["s"]
                item["check_digit"] = r["c/d"]

                # コード値ガアル場合
                if r["p"] > 0:
                    item["growing_method_label"] = r["growing_method"]
                if r["v"] > 0:
                    item["volume_label"] = r["volume"]
                if r["s"] > 0:
                    item["size_label"] = r["size"]

                item["fresh_standard_code"] = "{:4d}{:5d}{:1d}{:1d}{:1d}{:1d}".format(
                    r["header_code"],
                    r["vegefru_code"],
                    r["p"],
                    r["v"],
                    r["s"],
                    r["c/d"]
                )
                fresh_standard_codes[item["fresh_standard_code"]] = item
            except Exception as ex:
                print("[{}] {}".format(i, r))
                print(ex)
                raise ex

        return fresh_standard_codes

    def generatee_vegefru_pvs_map(self, fresh_standard_codes):
        """
        fresh_standard_codeのマップをvegefru_code,PVSの2段階のキー構造に変更する

        :param fresh_standard_codes:
        :return: vegefru_codeとPVSの二つのキーで選択できるfresh_standard_codeマップ
        """

        vegefru_map = {}
        for k, v in fresh_standard_codes.items():
            key1 = v["vegefru_code"]
            if not key1 in vegefru_map.keys():
                vegefru_map[key1] = {
                    "standard_name": v["standard_name"],
                    "vegefru_code": v["vegefru_code"],
                }

            key2 = "{:1d}{:1d}{:1d}".format(v["growing_method"], v["volume"], v["size"])
            vegefru_map[key1][key2] = {
                "growing_method": v["growing_method"],
                "volume": v["volume"],
                "size": v["size"],
                "check_digit": v["check_digit"],
                "fresh_standard_code": v["fresh_standard_code"]
            }
        return vegefru_map

    def generatee_growing_method_enums(self, fresh_standard_codes):
        """
        青果標準商品コード内で実際に使われているPのENUM値を生成する。
        ※Pの値は品目によって変化しないので、ENUM値の生成は必要ない。

        定義はこちら
        ```json
        {
            0: "指定なし",
            1: "有機農産物",
            2: "特別栽培農産物",
            3: "無袋(サン)",
            4: "ハウスまたは温室",
            5: "マルチ",
            6: "輸入",
            9: "その他"
        }
        ```

        :param fresh_standard_codes: 青果標準コードのマップ
        :return: {vegefru_code:{P値:Pのラベル名}} のdict形式を返す
        """
        return self._generatee_enums("growing_method", fresh_standard_codes)

    def generatee_size_enums(self, fresh_standard_codes):
        """
        青果標準商品コード内で実際に使われているSのENUM値を生成する。
        ※Sの値は品目によって変化しないので、ENUM値の生成は必要ない。

        定義はこちら
        ```json
        {
            0: "指定なし",
            1: "2S",
            2: "S",
            3: "M",
            4: "L",
            5: "2L",
            6: "3L",
            7: "4L",
            9: "その他"
        }
        ```

        :param fresh_standard_codes: 青果標準コードのマップ
        :return: {vegefru_code:{S値:Sのラベル名}} のdict形式を返す
        """
        return self._generatee_enums("size", fresh_standard_codes)

    def generatee_volume_enums(self, fresh_standard_codes):
        """
        青果標準商品コード内で実際に使われているVのENUM値を生成する。
        Vは品種毎に定義が異なる

        :param fresh_standard_codes: 青果標準コードのマップ
        :return: {vegefru_code:{V値:Vのラベル名}} のdict形式を返す
        """
        return self._generatee_enums("volume", fresh_standard_codes)

    def _generatee_enums(self, key, fresh_standard_codes):
        """
        keyを渡す事で各データ行の重複を削除したENUM値を生成する

        :param key:
        :param fresh_standard_codes:
        :return: {vegefru_code:{key値:keyのラベル名}} のdict形式を返す
        """
        all_enum_maps = {}
        for k, v in fresh_standard_codes.items():
            if not v["vegefru_code"] in all_enum_maps.keys():
                all_enum_maps[v["vegefru_code"]] = {}

            if v[key] == 0:
                continue

            enum_map = all_enum_maps[v["vegefru_code"]]
            if not v[key] in enum_map.keys():
                enum_map[v[key]] = v[key + "_label"]
        return all_enum_maps
