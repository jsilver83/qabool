from django.test import TestCase, Client

from .models import Agreement
from .forms import AgreementForm

class IntitialAgreementTestCase(TestCase):
    def setUp(self):
        Agreement.objects.create(agreement_type='INITIAL')
        # Every test needs a client.
        self.client = Client()

    def test_redirect_register_to_initialagreement(self):
        """
        Navigating to /en/register should load /en/initialagreement
        as long as the user has not agreed yet.
        """
        response = self.client.get('/en/register', follow=True)
        self.assertRedirects(response, '/en/initialagreement/', status_code=301,
                                 target_status_code=200)
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertEqual(response.redirect_chain[0], ('/en/register/', 301))
        self.assertEqual(response.redirect_chain[1], ('/en/initialagreement/', 302))

        response = self.client.get('/en/register/', follow=True)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertRedirects(response, '/en/initialagreement/', status_code=302,
                                 target_status_code=200)

    def test_initialagreement_form_invalid_agree1(self):
        form_data = {'agree1': False, 'agree2': True}
        form = AgreementForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_initialagreement_form_invalid_agree2(self):
        form_data = {'agree1': True, 'agree2': False}
        form = AgreementForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_initialagreement_form_invalid_agree1_agree2(self):
        form_data = {'agree1': False, 'agree2': False}
        form = AgreementForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_initialagreement_form_valid(self):
        form_data = {'agree1': True, 'agree2': True}
        form = AgreementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_initialagreement_without_agree1(self):
        response = self.client.post('/en/initialagreement/', {'agree1': False, 'agree2': True})
        self.assertFormError(response, 'form', 'agree1', 'This field is required.')
        self.assertFormError(response, 'form', 'agree2', None)
        self.assertEqual(response.resolver_match.func.__name__, 'initial_agreement')
        self.assertEqual(response.status_code, 200)

    def test_post_initialagreement_without_agree2(self):
        response = self.client.post('/en/initialagreement/', {'agree1': True, 'agree2': False})
        self.assertFormError(response, 'form', 'agree1', None)
        self.assertFormError(response, 'form', 'agree2', 'This field is required.')
        self.assertEqual(response.resolver_match.func.__name__, 'initial_agreement')
        self.assertEqual(response.status_code, 200)


    def test_post_initialagreement_without_agree1_agree2(self):
        response = self.client.post('/en/initialagreement/', {'agree1': False, 'agree2': False})
        self.assertFormError(response, 'form', 'agree1', 'This field is required.')
        self.assertFormError(response, 'form', 'agree2', 'This field is required.')
        self.assertEqual(response.resolver_match.func.__name__, 'initial_agreement')
        self.assertEqual(response.status_code, 200)


    def test_post_initialagreement_after_agreeing(self):
        response = self.client.post('/en/initialagreement/', {'agree1': True, 'agree2': True}, follow=True)
        self.assertFormError(response, 'form', 'agree1', None)
        self.assertFormError(response, 'form', 'agree2', None)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertRedirects(response, '/en/register/', status_code=302, target_status_code=200)

