from unittest import TestCase

from fixtureupper import UpperRegister
from models import Article, Author


class TestModelFixtureUpper(TestCase):
    def setUp(self):
        self.ModelFixtureUpper = UpperRegister()

        class AuthorFixtureUpper(self.ModelFixtureUpper):
            model = Author
            defaults = {}

        class ArticleFixtureUpper(self.ModelFixtureUpper):
            model = Article
            defaults = {}

        self.m_fu = self.ModelFixtureUpper(start_id=150)
        self.AuthorFixtureUpperClass = AuthorFixtureUpper
        self.ArticleFixtureUpperClass = ArticleFixtureUpper

        self.au_fu = self.m_fu.get_upper('Author')
        self.ar_fu = self.m_fu.get_upper('Article')

    def test_register_fixture_uppers(self):
        self.assertEqual(type(self.m_fu.get_upper('Author')), self.AuthorFixtureUpperClass)
        self.assertEqual(type(self.m_fu.get_upper('Article')), self.ArticleFixtureUpperClass)

    def test_generates_fixture(self):
        fixture = self.au_fu.generate(data={})
        self.assertEqual(len(self.au_fu.fixtures), 1)
        self.assertEqual(fixture, self.au_fu.fixtures[0])
        self.assertEqual(fixture.id, 150)
        self.assertIsNone(fixture.name)

    def test_sets_data(self):
        fixture = self.au_fu.generate(data={
            'name': 'Test Name',
        })
        self.assertEqual(fixture.name, 'Test Name')

    def test_sets_data_with_default(self):
        self.AuthorFixtureUpperClass.defaults['name'] = 'Default Name'
        fixture = self.au_fu.generate(data={})
        self.assertEqual(fixture.name, 'Default Name')

    def test_sets_data_with_default_function(self):
        self.AuthorFixtureUpperClass.defaults['name'] = lambda self, fixture: 'Author with id %s' % fixture.id

        fixture = self.au_fu.generate(data={})
        self.assertEqual(fixture.name, 'Author with id 150')

        fixture = self.au_fu.generate(data={})
        self.assertEqual(fixture.name, 'Author with id 151')

    def test_generates_multiple_fixtures(self):
        fixtures = self.au_fu.generate(data=[
            {},
            {'name': 'Test Name 2'},
            {},
        ])
        self.assertEqual(len(self.au_fu.fixtures), 3)
        self.assertEqual(fixtures, self.au_fu.fixtures)

        self.assertIsNone(fixtures[0].name)
        self.assertEqual(fixtures[0].id, 150)

        self.assertEqual(fixtures[1].name, 'Test Name 2')
        self.assertEqual(fixtures[1].id, 151)

        self.assertIsNone(fixtures[2].name)
        self.assertEqual(fixtures[2].id, 152)

    def test_sets_relation_one_way(self):
        au_fixture = self.au_fu.generate(data={})
        ar_fixture = self.ar_fu.generate(data={
            'author': au_fixture,
        })

        self.assertEqual(au_fixture.articles[0], ar_fixture)
        self.assertEqual(ar_fixture.author, au_fixture)
        self.assertEqual(ar_fixture.main_author_id, au_fixture.id)

    def test_sets_relation_other_way(self):
        ar_fixture = self.ar_fu.generate(data={})
        au_fixture = self.au_fu.generate(data={
            'articles': [ar_fixture],
        })

        self.assertEqual(au_fixture.articles[0], ar_fixture)
        self.assertEqual(ar_fixture.author, au_fixture)
        self.assertEqual(ar_fixture.main_author_id, au_fixture.id)