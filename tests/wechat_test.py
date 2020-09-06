import os
import glob

from beancount.ingest.extract import extract_from_file

from tests.utils import get_importer
from china_beancount_importers.wechat import WechatImporter


def test_example_config():
    importer = get_importer("examples/wechat.import")
    assert isinstance(importer, WechatImporter)


def test_extract_as_expected():
    importer = get_importer("examples/wechat.import")
    extracted = []
    for f in glob.glob("./tests/fixtures/wechat/*"):
        extracted.extend(extract_from_file(os.path.abspath(f), importer))
    assert extracted
