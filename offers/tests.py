from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

class OfferAPITestCase(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.force_authenticate(user=self.user)  # ← DAS ist wichtig!

    def test_create_offer(self):
        data = {
        "title": "Test Offer",
        "description": "Testbeschreibung",
        "details": [
            {
                "title": "Basic",
                "description": "Beschreibung Basic",
                "delivery_time_in_days": 3,
                "price": 50,
                "revisions": 1,
                "features": "Feature A, Feature B",
                "offer_type": "basic"
            },
            {
                "title": "Standard",
                "description": "Beschreibung Standard",
                "delivery_time_in_days": 5,
                "price": 100,
                "revisions": 2,
                "features": "Feature C, Feature D",
                "offer_type": "standard"
            },
            {
                "title": "Premium",
                "description": "Beschreibung Premium",
                "delivery_time_in_days": 7,
                "price": 150,
                "revisions": 3,
                "features": "Feature E, Feature F",
                "offer_type": "premium"
            }
        ]
    }

        response = self.client.post('/api/offers/', data, format='json')
        print("RESPONSE:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
