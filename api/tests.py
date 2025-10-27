from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthCheckTestCase(APITestCase):
    """Test case for the health check endpoint"""
    
    def test_health_check_endpoint(self):
        """Test that the health check endpoint returns a 200 status"""
        url = reverse('health-check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('message', response.data)

