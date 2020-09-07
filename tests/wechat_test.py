import csv
from os import path
from decimal import Decimal
from os.path import abspath, normpath

from beancount.ingest import cache
from beancount.core.data import Amount
from beancount.ingest.extract import extract_from_file

from tests.utils import get_importer
from china_beancount_importers.wechat import WechatImporter


def test_example_config():
    importer = get_importer("examples/wechat.import")
    assert isinstance(importer, WechatImporter)


def test_extract_as_expected():
    importer = get_importer("examples/wechat.import")
    fs = normpath(abspath("tests/fixtures/wechat/微信支付账单(20200830-20200906).csv"))
    extracted = extract_from_file(fs, importer)
    assert len(extracted) == 7, "should extract 17 entries from file"


def test_extract_(tmpdir):
    csv_path = path.join(tmpdir, "微信支付账单(20200830-20200906).csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.write("\n" * 16)
        writer = csv.writer(f)
        writer.writerow("交易时间,交易类型,交易对方,商品,收/支,金额(元),支付方式,当前状态,交易单号,商户单号,备注".split(","))
        writer.writerow(
            [
                "2020-09-06 23:19:24",
                "零钱充值",
                "招商银行(1111)",
                "/",
                "/",
                "¥1.00",
                "招商银行(1111)",
                "充值完成",
                233,
                "/",
                "/",
            ]
        )
    file = cache._FileMemo(csv_path)
    importer: WechatImporter = get_importer("examples/wechat.import")
    entries = importer.extract(file)
    assert len(entries) == 1
    txn = entries[0]
    assert [x.account == importer.account for x in txn.postings] == [True, False]
    assert [x.units for x in txn.postings] == [
        Amount(Decimal(1), "CNY"),
        Amount(Decimal(-1), "CNY"),
    ]
    assert txn.postings[1].account == "Assets:Bank:CMB:C1111"
