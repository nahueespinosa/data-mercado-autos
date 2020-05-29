import unittest
from loader import DataLoader


class TestDataLoader(unittest.TestCase):
    def test_get_access_token(self):
        c = DataLoader()
        token = c.get_access_token()

        self.assertEqual(len(token), 'APP_USR-5387223166827464-090515-8cc4448aac10d5105474e135355a8321-8035443')


if __name__ == '__main__':
    unittest.main()
