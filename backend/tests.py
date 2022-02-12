from django.test import TestCase
from django.test.client import Client

from backend.models import School, Ingredient, MealItem, MealSelection

import datetime


class UserTestCase(TestCase):
    fixtures = ['test_school.yaml']

    def setUp(self):
        self.school = School.objects.get(pk=1)

        self.i_apple = Ingredient.objects.get(pk=1)
        self.i_orange = Ingredient.objects.get(pk=2)
        self.i_fish = Ingredient.objects.get(pk=3)
        self.i_dough = Ingredient.objects.get(pk=4)
        self.i_dough = Ingredient.objects.get(pk=5)

        self.m_apple_pie = MealItem.objects.get(pk=1)
        self.m_anchovy = MealItem.objects.get(pk=2)
        self.m_pizza = MealItem.objects.get(pk=3)
        self.m_orange = MealItem.objects.get(pk=4)

        self.mm_lunch = MealSelection.objects.get(pk=1)

        # Creating profiles
        self.pdict_alex_hu = {
            'email': '2021090@appleby.on.ca',  # only the best school
            'password': 'goodpassword123',
            'school': self.school.pk,
            'name': 'Alex Hu',
            'height': 50,
            'weight': 7000.,  # that's TLC worthy!
            'birthdate': datetime.date(2003, 11, 24).isoformat(),
            'meals': ['breakfast', 'lunch'],  # alex needs to stay fit
            'meal_length': 23,
            'sex': 'male',
            'health_goal': 'athletic_performance',  # in chess, of course
            'activity_level': 'mild',
            'grad_year': 2025,
            'ban': [self.m_anchovy.pk],
            'favour': [self.m_apple_pie.pk, self.m_pizza.pk],
            'allergies': [self.i_fish.pk]
        }


class AuthTestCase(UserTestCase):
    def test_register_valid(self):
        c = Client()

        res_json = c.post('/register/', self.pdict_alex_hu).json()
        self.assertFalse(res_json['error'], msg=f'Got error "{res_json["message"]}"')

    def test_register_invalid(self):
        c = Client()

        def with_replacement_test(name, repl):
            reg_dict = self.pdict_alex_hu.copy()
            for k, v in repl.items():
                reg_dict[k] = v
            reg_dict['email'] = 'moses@mosesxu.net'
            reg_dict['password'] = '123456'

            res_json = c.post('/register/', reg_dict).json()
            self.assertTrue(res_json['error'], msg=f'Failed to catch invalid registration "{name}"')
            print(f'Invalid register test "{name}" gave error message "{res_json["message"]}"')

        with_replacement_test('invalid primary key', {'school': 6942069})
        with_replacement_test('invalid value', {'weight': 'one million'})
        with_replacement_test('invalid choice (obj)', {'sex': 'amogus'})  # I'm gonna get cancelled for this
        with_replacement_test('invalid choice (list)', {'meals': ['i eat one meal a day']})

    def test_auth_valid(self):
        c = Client()

        print(c.post('/register/', self.pdict_alex_hu).json())

        login_res = c.post('/login/', {
            'email': self.pdict_alex_hu['email'],
            'password': self.pdict_alex_hu['password'],
            'type': 'student'
        }).json()
        self.assertFalse(login_res['error'], msg=f'Got error "{login_res["message"]}"')

        logout_res = c.get('/logout/').json()
        self.assertFalse(logout_res['error'], msg=f'Got error "{logout_res["message"]}"')

    def test_auth_invalid(self):
        c = Client()

        def test_invalid(email=None, password=None):
            if not email:
                email = self.pdict_alex_hu['email']
            if not password:
                password = self.pdict_alex_hu['password']

            login_res = c.post('/login/', {
                'email': email,
                'password': password,
                'type': 'student'
            }).json()
            self.assertTrue(login_res['error'], msg=f'Expected email={email} password={password} to fail login')

        test_invalid('b')
        test_invalid(None, 'not the right pass')
        test_invalid('a', 'b')

    def test_auth_school(self):
        self.assertFalse(True, msg='TODO')


class DataFetchTestCase(UserTestCase):
    fixtures = ['test_school.yaml', 'test_user.yaml']

    def make_logged_in_client(self):
        c = Client()
        self.assertFalse(c.post('/login/', {
            'email': self.pdict_alex_hu['email'],
            'password': self.pdict_alex_hu['password'],
            'type': 'student'
        }).json()['error'])

        return c

    def check_response_list(self, res: dict):
        self.assertFalse(res['error'])
        for x in res['data']:
            self.assertIn('pk', x)

    def test_schools(self):
        c = Client()
        res = c.get('/api/schools/').json()
        self.check_response_list(res)
        self.assertEqual(len(res['data']), 1)

    def test_meals(self):
        c = self.make_logged_in_client()
        res = c.get('/api/meals/').json()
        # print(res)
        self.check_response_list(res)

    def test_items(self):
        c = self.make_logged_in_client()
        meal_id = c.get('/api/meals/').json()['data'][0]['pk']
        res = c.get(f'/api/items/{meal_id}/').json()
        # print(res)
        self.check_response_list(res)

    def test_school_items(self):
        c = self.make_logged_in_client()
        res = c.get(f'/api/school_items/').json()
        # print(res)
        self.check_response_list(res)

    def test_ingredients(self):
        c = self.make_logged_in_client()
        res = c.get(f'/api/ingredients/').json()
        # print(res)
        self.check_response_list(res)
