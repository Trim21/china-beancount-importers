"""Importer for 微信
"""
import re
import csv
import datetime
from os import path
from typing import Dict

from beancount.core import data
from dateutil.parser import parse
from beancount.ingest import importer
from beancount.core.amount import Amount
from beancount.core.number import D

_COMMENTS_STR = "收款方备注:二维码收款付款方留言:"


class WechatImporter(importer.ImporterProtocol):
    """An importer for Wechat CSV files."""

    def __init__(self, account_dict: Dict):
        # print(file_type)
        self.accountDict = account_dict
        self.currency = "CNY"
        self.default_set = frozenset({"wechat"})

    def identify(self, file):
        # Match if the filename is as downloaded and the header has the unique
        # fields combination we're looking for.
        return re.match(r"微信支付账单\(\d{8}-\d{8}\).csv", path.basename(file.name))

    def file_name(self, file):
        return "wechat.{}".format(path.basename(file.name))

    def file_account(self, _=None):
        return "Assets:WeChat"
        # return None

    def file_date(self, file):
        # Extract the statement date from the filename.
        return datetime.datetime.strptime(
            path.basename(file.name).split("-")[-1], "%Y%m%d).csv"
        ).date()

    def extract(self, file, existing_entries=None):
        # Open the CSV file and create directives.
        entries = []
        index = 0
        with open(file.name, encoding="utf-8") as f:
            for _ in range(16):
                next(f)
            for index, row in enumerate(csv.DictReader(f)):
                meta = data.new_metadata(file.name, index)
                dt = parse(row["交易时间"])
                meta["time"] = str(dt.time())
                raw_amount = D(row["金额(元)"].lstrip("¥"))
                isExpense = True if (row["收/支"] == "支出" or row["收/支"] == "/") else False
                if isExpense:
                    raw_amount = -raw_amount
                amount = Amount(raw_amount, self.currency)
                payee = row["交易对方"]
                narration: str = row["商品"]
                if narration.startswith(_COMMENTS_STR):
                    narration = narration.replace(_COMMENTS_STR, "")
                if narration == "/":
                    narration = ""
                account_1_text = row["支付方式"]
                account_1 = "Assets:FIXME"
                # print(raw_amount,narration,account_1_text,account_2_text)
                for asset_k, asset_v in self.accountDict.items():
                    if account_1_text.find(asset_k) != -1:
                        # print(asset_k, asset_v)
                        account_1 = asset_v

                postings = [data.Posting(account_1, amount, None, None, None, None)]

                if row["当前状态"] == "充值完成":
                    postings.insert(
                        0,
                        data.Posting(self.file_account(), None, None, None, None, None),
                    )
                    narration = "微信零钱充值"
                    payee = None
                txn = data.Transaction(
                    meta,
                    dt.date(),
                    self.FLAG,
                    payee,
                    narration,
                    self.default_set,
                    data.EMPTY_SET,
                    postings,
                )
                entries.append(txn)

        # Insert a final balance check.
        return entries
