from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

class OfferAPITestCase(APITestCase):
    def setUp(self):
        self.offer_data = {
            "title": "Test Offer",
            "description": "Testbeschreibung",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": "50.00",
                    "features": "Feature A, Feature B",
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": "100.00",
                    "features": "Feature C, Feature D",
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 7,
                    "price": "150.00",
                    "features": "Feature E, Feature F",
                    "offer_type": "premium"
                }
            ]
        }

    def register_user(self, user_type):
        """Registriert einen User über den echten Registrierungs-Endpoint."""
        url = reverse("registration")
        data = {
            "username": f"{user_type}_user",
            "email": f"{user_type}@mail.de",
            "password": "testpass123",
            "repeated_password": "testpass123",
            "type": user_type
        }
        response = self.client.post(url, data, format="json")
        return response.data["token"]

    def test_create_offer_as_business_user(self):
        token = self.register_user("business")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/offers/", self.offer_data, format="json")
        print("✅ RESPONSE (Business):", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_offer_as_customer_user(self):
        token = self.register_user("customer")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/offers/", self.offer_data, format="json")
        print("🚫 RESPONSE (Customer):", response.data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
