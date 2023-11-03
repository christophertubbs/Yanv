import pathlib
import unittest

import xarray

from yanv.cache import InMemoryFrameCache

TEST_DATA_PATH = pathlib.Path(__file__).parent.parent / "resources" / "test.nc"

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = InMemoryFrameCache()

    def test_load(self):
        dataset = xarray.load_dataset(TEST_DATA_PATH)
        key: str = self.cache.add(dataset)
        fetched_data = self.cache.get(key=key)

        self.assertEqual(dataset, fetched_data)

        information = self.cache.get_information(key=key)

        pass

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
