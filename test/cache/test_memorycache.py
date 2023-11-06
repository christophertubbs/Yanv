import pathlib
import unittest

import xarray

from yanv.cache import InMemoryFrameCache

TEST_DATA_PATH = pathlib.Path(__file__).parent.parent / "resources" / "test.nc"


class MemoryCacheTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = InMemoryFrameCache()

    def test_load(self):
        dataset = xarray.load_dataset(TEST_DATA_PATH)
        key: str = self.cache.add(dataset)
        fetched_data = self.cache.get(key=key)

        self.assertEqual(dataset, fetched_data)

        information = self.cache.get_information(key=key)

        self.assertEqual(len(information.dimensions), 3)

        self.assertIn("feature_id", information.dimension_names)
        self.assertIn("reference_time", information.dimension_names)
        self.assertIn("time", information.dimension_names)

        feature_id = information.get_dimension("feature_id")
        reference_time = information.get_dimension("reference_time")
        time = information.get_dimension("time")

        self.assertEqual(2776738, len(feature_id))
        self.assertEqual(1, len(reference_time))
        self.assertEqual(18, len(time))

        crs = information.get_variable("crs")
        streamflow = information.get_variable("streamflow")
        stream_anomaly = information.get_variable("streamflow_anomaly")

        self.assertEqual(1, crs.count)
        self.assertEqual(feature_id.count * time.count, streamflow.count)
        self.assertEqual(feature_id.count * time.count, stream_anomaly.count)


if __name__ == '__main__':
    unittest.main()
