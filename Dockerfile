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


FROM python:3.10

RUN python -m pip install --upgrade pip && python -m pip install --upgrade pip poetry

RUN mkdir /fresh_standard_code_json
ADD . /fresh_standard_code_json

WORKDIR /fresh_standard_code_json
RUN poetry install

WORKDIR /fresh_standard_code_json/scrape
CMD ["poetry", "run", "scrapy", "crawl", "fresh_standard_code_spider"]