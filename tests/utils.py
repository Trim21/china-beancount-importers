import runpy


def get_importer(filepath):
    importer_list = runpy.run_path(filepath)
    assert len(importer_list["CONFIG"]) == 1, "config should contain only one importer"
    return importer_list["CONFIG"][0]
