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

from itemadapter import ItemAdapter
import scrapy


class FreshStandardCodesWriterPipeline:
    def process_item(self, item, spider):
        fresh_standard_codes = item["fresh_standard_codes"]
        # 青果標準商品コード一覧をJSON形式で出力する
        spider.write_json("fresh_standard_codes.json", fresh_standard_codes)

        return item


class VegefruPVSWriterPipeline:
    def process_item(self, item, spider):
        fresh_standard_codes = item["fresh_standard_codes"]
        # 青果標準商品コード一覧をベジフルコードとPVSで正規化したマップをJSON形式で出力する
        vegefru_pvs_map = spider.generatee_vegefru_pvs_map(fresh_standard_codes)
        spider.write_json("vegefru_pvs.json", vegefru_pvs_map)

        return item


class GrowingMethodEnumsWriterPipeline:
    def process_item(self, item, spider):
        fresh_standard_codes = item["fresh_standard_codes"]

        # growing_method(P)のenum値をJSON形式で出力する
        growing_method_enums = spider.generatee_growing_method_enums(fresh_standard_codes)
        spider.write_json("growing_method_enums.json", growing_method_enums)

        return item


class VolumeEnumsWriterPipeline:
    def process_item(self, item, spider):
        fresh_standard_codes = item["fresh_standard_codes"]

        # volume(V)のenum値をJSON形式で出力する
        volume_enums = spider.generatee_volume_enums(fresh_standard_codes)
        spider.write_json("volume_enums.json", volume_enums)

        return item


class SizeEnumsWriterPipeline:
    def process_item(self, item, spider):
        fresh_standard_codes = item["fresh_standard_codes"]

        # sizeのenum値をJSON形式で出力する
        size_enums = spider.generatee_size_enums(fresh_standard_codes)
        spider.write_json("size_enums.json", size_enums)

        return item
