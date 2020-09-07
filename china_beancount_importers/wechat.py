"""Importer for 微信
"""
import re
import csv
import datetime
from os import path
from typing import Dict

from beancount.core import data, flags
from dateutil.parser import parse
from beancount.ingest import importer
from beancount.core.amount import Amount
from beancount.core.number import D

_COMMENTS_STR = "收款方备注:二维码收款付款方留言:"


class WechatImporter(importer.ImporterProtocol):
    """An importer for Wechat CSV files."""

    def __init__(self, account="Assets:WeChat", account_dict: Dict = None):
        """

        :param account: 微信本身的账户
        :param account_dict: 支付方式和beancount账户的对应
        """
        self.account = account
        self.accountDict = account_dict or {}
        self.accountDict.update(
            {
                "零钱": self.account,
                "/": self.account,
            }
        )
        self.default_set = frozenset({"wechat"})
        self.currency = "CNY"

    def identify(self, file):
        # Match if the filename is as downloaded and the header has the unique
        # fields combination we're looking for.
        return re.match(r"微信支付账单\(\d{8}-\d{8}\).csv", path.basename(file.name))

    def file_name(self, file):
        return "wechat.{}".format(path.basename(file.name))

    def file_account(self, _=None):
        return self.account
        # return None

    def file_date(self, file):
        # Extract the statement date from the filename.
        return datetime.datetime.strptime(
            path.basename(file.name).split("-")[-1], "%Y%m%d).csv"
        ).date()

    def extract(self, file, existing_entries=None):
        # Open the CSV file and create directives.
        entries = []
        with open(file.name, encoding="utf-8") as f:
            for _ in range(16):
                next(f)
            for index, row in enumerate(csv.DictReader(f)):
                flag = flags.FLAG_WARNING
                dt = parse(row["交易时间"])
                meta = data.new_metadata(
                    file.name, index, kvlist={"time": str(dt.time())}
                )
                amount = Amount(D(row["金额(元)"].lstrip("¥")), self.currency)
                if row["收/支"] in {"支出", "/"}:
                    # 支出
                    amount = -amount
                payee = row["交易对方"]
                narration: str = row["商品"]
                if narration.startswith(_COMMENTS_STR):
                    narration = narration.replace(_COMMENTS_STR, "")
                if narration == "/":
                    narration = ""
                account_1_text = row["支付方式"]
                account_1 = "Assets:FIXME"
                for asset_k, asset_v in self.accountDict.items():
                    if asset_k in account_1_text:
                        account_1 = asset_v
                        flag = flags.FLAG_OKAY

                postings = [data.Posting(account_1, amount, None, None, None, None)]

                if row["当前状态"] == "充值完成":
                    postings.insert(
                        0,
                        data.Posting(self.account, -amount, None, None, None, None),
                    )
                    narration = "微信零钱充值"
                    payee = None
                txn = data.Transaction(
                    meta,
                    dt.date(),
                    flag,
                    payee,
                    narration,
                    self.default_set,
                    data.EMPTY_SET,
                    postings,
                )
                entries.append(txn)
        return entries
