# これはなに？

このプロジェクトは生鮮取引電子化推進協議会が公開している**青果物標準商品コード**の表データの最新を取得してJSONデータに落とし込むスクレイピングツールのプロジェクトです。

データはこちらから取得できます。  
https://www.ofsi.or.jp/kyougikai/freshstandardcode/

青果物標準商品コードの仕様については[こちら](https://www.ofsi.or.jp/file/task_edi/H13output2/seika_m/seika_m1.pdf)を参照してください。

# JSONデータ

生成済みのデータを利用する場合はdistフォルダを参照してください。

生成済ファイル一覧

| ファイル名                     | 説明                                           |
|---------------------------|----------------------------------------------|
| fresh_standard_codes.json | 青果物標準コードの各項目をマップ形式にしたJSONデータ                 |
| vegefru_pvs.json          | 青果物標準コードの各項目をベジフルコードとPVSで2段階のマップ形式にしたJSONデータ |
| growing_method_enums.json | 栽培方法等(P)で実際に利用されている項目をマップ形式にしたJSONデータ        |
| volume_enums.json         | 商品形態(V)で実際に利用されている項目をマップ形式にしたJSONデータ         |
| size_enums.json           | 階級(S)で実際に利用されている項目をマップ形式にしたJSONデータ           |


# 開発者向け

## 依存モジュール

Pythonの下記モジュールを利用しています。

* Scrapy
* Pandas
* openpyxl
* gtin
* tomli

## JSON生成方法

Dockerを使います。Pythonを直接使う場合は後述の実行方法を参照してください。

1. ダウンロードしたプロジェクトフォルダに移動します。

```shell
$ cd ダウンロードしたfresh_standard_code_jsonのフォルダ
```

2. Dockerイメージをビルドします。

```shell
$ docker build -t fresh_standard_code_json:latest .
```

3. Dockerイメージを実行します。

```shell
$ docker run --rm --mount type=bind,source=./dist,target=/fresh_standard_code_json/dist -t fresh_standard_code_json:latest
```

4. distフォルダにjsonファイルが生成していたら成功です。

```shell
$ ls ./dist
```

## 実行方法

Scrapyを使って実行します。

1. poetryをインストールします。

```shell
$ pythom -m pip install poetry
```

2. poetryで依存モジュールをインストールします。

```shell
$ poetry install
```

3. scrapyのプロジェクトフォルダに移動します。

```shell
$ cd scrape
```

4. poetryの実行環境を使ってscrapyを実行します。

```shell
$ poetry run scrapy crawl fresh_standard_code_spider
```

# LICENSE

本プロジェクトはApache License, Version2.0ライセンスで公開しています。  
fresh_standard_code_json by Newmarket Inc. is licensed under the Apache License, Version2.0