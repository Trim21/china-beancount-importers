import datetime
from decimal import Decimal
from os.path import abspath, normpath

from beancount.core.data import Amount, Posting, Transaction
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
    assert extracted == [
        Transaction(
            meta={
                "filename": fs,
                "lineno": 6,
                "time": "15:29:00",
            },
            date=datetime.date(2020, 9, 4),
            flag="*",
            payee="同程旅行",
            narration="同程旅行",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:Bank:CCB:C2222",
                    units=Amount(Decimal("742.00"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
        Transaction(
            meta={
                "filename": fs,
                "lineno": 2,
                "time": "21:34:00",
            },
            date=datetime.date(2020, 9, 5),
            flag="*",
            payee="CW",
            narration="收款方备注:二维码收款",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:WeChat",
                    units=Amount(Decimal("670.00"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
        Transaction(
            meta={
                "filename": fs,
                "lineno": 3,
                "time": "18:16:00",
            },
            date=datetime.date(2020, 9, 5),
            flag="*",
            payee="公司a",
            narration="店铺b",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:Bank:CMB:C1111",
                    units=-Amount(Decimal("21.40"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
        Transaction(
            meta={
                "filename": fs,
                "lineno": 4,
                "time": "17:11:00",
            },
            date=datetime.date(2020, 9, 5),
            flag="*",
            payee="用户a。",
            narration="转账备注:微信转账",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:Bank:CMB:C1111",
                    units=-Amount(Decimal("420.00"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
        Transaction(
            meta={
                "filename": fs,
                "lineno": 5,
                "time": "12:34:00",
            },
            date=datetime.date(2020, 9, 5),
            flag="*",
            payee="京东商城平台商户",
            narration="京东-订单编号234",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:Bank:CMB:C1111",
                    units=-Amount(Decimal("9.90"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
        Transaction(
            meta={
                "filename": fs,
                "lineno": 0,
                "time": "16:59:00",
            },
            date=datetime.date(2020, 9, 6),
            flag="*",
            payee="用户b",
            narration="这是一条留言",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:Bank:CMB:C1111",
                    units=-Amount(Decimal("20.00"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
        Transaction(
            meta={
                "filename": fs,
                "lineno": 1,
                "time": "14:24:00",
            },
            date=datetime.date(2020, 9, 6),
            flag="*",
            payee="京东商城平台商户",
            narration="京东-订单编号233",
            tags=frozenset({"wechat"}),
            links=frozenset(),
            postings=[
                Posting(
                    account="Assets:Bank:CMB:C1111",
                    units=-Amount(Decimal("150.58"), "CNY"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                )
            ],
        ),
    ]
