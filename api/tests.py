from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Distance_Unit

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse


class ModelTestCase(TestCase):
    # This class defines the test suite for the openrun model.

    def setUp(self):
        # Define the test client and other test variables.
        self.user = User(username='temporary1', password='temporary1')
        self.unit = Distance_Unit(
            name='peoples', suffix='pe', conversion_factor='1')

    def test_model_can_creat_user(self):
        old_count = User.objects.count()
        self.user.save()
        new_count = User.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_can_creat_unit(self):
        old_count = Distance_Unit.objects.count()
        self.unit.save()
        new_count = Distance_Unit.objects.count()
        self.assertNotEqual(old_count, new_count)


class viewTestCase(TestCase):
    # Test suite for the api views.

    def setUp(self):
        # Define the test client and other test variables.

        self.staff_user = User.objects.create(
            username='staff',
            is_staff=True,)
        self.normal_user = User.objects.create(
            username='user',
            is_staff=False,)
        self.client = APIClient()
        self.url = reverse('distance_unit-list')
        self.unit_data = {
            'name': 'temporary1',
            'suffix': 'tm',
            'conversion_factor': '1',
            }

    def test_api_staff_user_can_create_a_distance_unit(self):
        # test staff user can create distance_unit
        self.client.force_authenticate(user=self.staff_user)
        self.response = self.client.post(
            self.url,
            self.unit_data,
            format='json')
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_normal_user_can_not_create_a_distance_unit(self):
        # test non staff user can not create distance_unit
        self.client.force_authenticate(user=self.normal_user)
        self.response = self.client.post(
            self.url,
            self.unit_data,
            format='json')
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_amend_a_distance_unit(self):
        # test non staff user can not create distance_unit
        self.client.force_authenticate(user=self.staff_user)
        self.response = self.client.post(
            self.url,
            self.unit_data,
            format='json')
        unit = Distance_Unit.objects.get()
        change_unit = {
            'name': 'temporary1', 'suffix': 'tt', 'conversion_factor': '1.2'}

        resp = self.client.put(
            reverse('distance_unit-detail', kwargs={'pk': unit.id}),
            change_unit, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_api_can_delete_a_distance_unit(self):
        # test non staff user can not create distance_unit
        self.client.force_authenticate(user=self.staff_user)
        self.response = self.client.post(
            self.url,
            self.unit_data,
            format='json')
        unit = Distance_Unit.objects.get()

        resp = self.client.delete(
            reverse('distance_unit-detail', kwargs={'pk': unit.id}),
            format='json', follow=True)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class uploadTestCase(TestCase):
    # Test suite for the file upload section.

    def setUp(self):
        valid_gpx = '<?xml version="1.0" encoding="UTF-8"?>\
                <gpx version="1.1">\
                <trk>\
                <name><![CDATA[Running 4/15/10 6:04 pm]]></name>\
                <time>2010-04-15T18:04:28Z</time>\
                <trkseg>\
                <trkpt lat="51.443217000" lon="-2.610013000">\
                <ele>69.7</ele>\
                <time>2010-04-15T18:04:28Z</time>\
                </trkpt>\
                <trkpt lat="51.443946000" lon="-2.610618000">\
                <ele>72.9</ele>\
                <time>2010-04-15T18:05:08Z</time>\
                </trkpt>\
                </trkseg>\
                <trkseg>\
                <trkpt lat="51.443638000" lon="-2.614061000">\
                <ele>79.6</ele>\
                <time>2010-04-15T18:07:20Z</time>\
                </trkpt>\
                <trkpt lat="51.443255000" lon="-2.615090000">\
                <ele>81.0</ele>\
                <time>2010-04-15T18:07:33Z</time>\
                </trkpt>\
                </trkseg>\
                </trk>\
                </gpx>'.encode('utf-8')

        self.staff_user = User.objects.create(
            username='staff',
            is_staff=True,)
        self.normal_user = User.objects.create(
            username='user',
            is_staff=False,)
        self.client = APIClient()

        self.file_dict = { 'gpx_file': SimpleUploadedFile(
            'test.gpx', valid_gpx, 'text/xml')}

    def test_api_can_upload_file(self):
        self.client.force_authenticate(user=self.staff_user)
        resp = self.client.put(reverse('upload', {'filename': 'test.gpx'}), self.file_dict, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
