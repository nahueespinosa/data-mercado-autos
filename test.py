import unittest
from loader import DataLoader


class TestDataLoader(unittest.TestCase):
    def test_get_access_token(self):
        c = DataLoader()
        token = c.get_access_token()

        self.assertEqual(len(token), 'APP_USR-5387223166827464-090515-8cc4448aac10d5105474e135355a8321-8035443')

    def test_get_category_id_ropa(self):
        c = DataLoader()
        id = c.get_category_id("Ropa y Accesorios")

        self.assertEqual(id, "MLA1430")

    def test_get_category_id_autos(self):
        c = DataLoader()
        id = c.get_category_id("Autos, Motos y Otros")

        self.assertEqual(id, "MLA1743")

    def test_get_category_id_non_existent(self):
        c = DataLoader()
        id = c.get_category_id("Inventada")

        self.assertIsNone(id)


if __name__ == '__main__':
    unittest.main()
