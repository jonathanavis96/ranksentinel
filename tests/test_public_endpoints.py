"""Tests for public API endpoints (/public/leads, /public/start-monitoring)."""

import pytest
from fastapi.testclient import TestClient

from ranksentinel.api import app
from ranksentinel.db import connect, init_db


@pytest.fixture
def client(tmp_path):
    """Create a test client with a temporary database."""
    from ranksentinel.config import Settings, get_settings
    
    db_path = tmp_path / "test.db"
    
    # Create settings with the test database
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    # Initialize the database
    conn = connect(test_settings)
    init_db(conn)
    conn.close()
    
    # Override the settings dependency
    def override_get_settings():
        return test_settings
    
    app.dependency_overrides[get_settings] = override_get_settings
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestPublicLeads:
    """Tests for /public/leads endpoint."""
    
    def test_create_lead_success(self, client):
        """Test successful lead creation."""
        payload = {
            "email": "test@example.com",
            "domain": "example.com",
            "key_pages": "https://example.com/page1\nhttps://example.com/page2",
            "use_sitemap": True,
        }
        
        response = client.post("/public/leads", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "lead_id" in data
        assert data["lead_id"] is not None
    
    def test_create_lead_minimal(self, client):
        """Test lead creation with minimal required fields."""
        payload = {
            "email": "minimal@example.com",
            "domain": "minimal.com",
        }
        
        response = client.post("/public/leads", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_lead_duplicate(self, client):
        """Test creating duplicate lead returns existing lead."""
        payload = {
            "email": "duplicate@example.com",
            "domain": "duplicate.com",
        }
        
        # First submission
        response1 = client.post("/public/leads", json=payload)
        assert response1.status_code == 200
        data1 = response1.json()
        lead_id1 = data1["lead_id"]
        
        # Second submission with same email
        response2 = client.post("/public/leads", json=payload)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["lead_id"] == lead_id1
    
    def test_create_lead_invalid_email(self, client):
        """Test lead creation with invalid email."""
        payload = {
            "email": "invalid-email",
            "domain": "example.com",
        }
        
        response = client.post("/public/leads", json=payload)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_create_lead_missing_domain(self, client):
        """Test lead creation with missing domain."""
        payload = {
            "email": "test@example.com",
            "domain": "",
        }
        
        response = client.post("/public/leads", json=payload)
        
        # Pydantic validation returns 422 for validation errors
        assert response.status_code == 422
    
    def test_create_lead_sends_sample_report(self, client, monkeypatch):
        """Test that sample report email is sent on lead creation."""
        from unittest.mock import Mock, MagicMock
        
        # Mock MailgunClient
        mock_send_email = Mock()
        mock_mailgun_instance = MagicMock()
        mock_mailgun_instance.send_email = mock_send_email
        
        mock_mailgun_class = Mock(return_value=mock_mailgun_instance)
        
        # Patch MailgunClient where it's imported (in the mailgun module)
        monkeypatch.setattr("ranksentinel.mailgun.MailgunClient", mock_mailgun_class)
        
        # Configure test settings with Mailgun credentials
        from ranksentinel.config import Settings, get_settings
        test_settings = Settings(
            RANKSENTINEL_DB_PATH=":memory:",
            MAILGUN_API_KEY="test-key",
            MAILGUN_DOMAIN="test.mailgun.org",
        )
        
        def override_get_settings():
            return test_settings
        
        app.dependency_overrides[get_settings] = override_get_settings
        
        # Make request
        payload = {
            "email": "email-test@example.com",
            "domain": "example.com",
        }
        
        response = client.post("/public/leads", json=payload)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sample report" in data["message"].lower() or "check your email" in data["message"].lower()
        
        # Verify email was sent
        assert mock_send_email.called, "MailgunClient.send_email should have been called"
        call_args = mock_send_email.call_args
        assert call_args is not None
        
        # Check email parameters
        assert call_args.kwargs["to"] == "email-test@example.com"
        assert "Sample RankSentinel Report" in call_args.kwargs["subject"]
        assert "example.com" in call_args.kwargs["subject"]
        assert "CRITICAL ISSUES" in call_args.kwargs["text"]
        assert "ranksentinel.com/schedule" in call_args.kwargs["text"]
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_create_lead_email_failure_doesnt_block(self, client, monkeypatch):
        """Test that email sending failure doesn't block lead creation."""
        from unittest.mock import Mock
        
        # Mock MailgunClient to raise an exception
        mock_mailgun_class = Mock(side_effect=Exception("Mailgun error"))
        
        monkeypatch.setattr("ranksentinel.mailgun.MailgunClient", mock_mailgun_class)
        
        # Configure test settings with Mailgun credentials
        from ranksentinel.config import Settings, get_settings
        test_settings = Settings(
            RANKSENTINEL_DB_PATH=":memory:",
            MAILGUN_API_KEY="test-key",
            MAILGUN_DOMAIN="test.mailgun.org",
        )
        
        def override_get_settings():
            return test_settings
        
        app.dependency_overrides[get_settings] = override_get_settings
        
        # Make request
        payload = {
            "email": "failure-test@example.com",
            "domain": "example.com",
        }
        
        response = client.post("/public/leads", json=payload)
        
        # Verify response - should succeed despite email failure
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "lead_id" in data
        
        # Clean up
        app.dependency_overrides.clear()


class TestPublicStartMonitoring:
    """Tests for /public/start-monitoring endpoint."""
    
    def test_start_monitoring_success(self, client):
        """Test successful monitoring start for new customer."""
        payload = {
            "email": "monitor@example.com",
            "domain": "monitor.com",
            "key_pages": "https://monitor.com/page1",
            "use_sitemap": True,
        }
        
        response = client.post("/public/start-monitoring", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "customer_id" in data
        assert data["customer_id"] is not None
    
    def test_start_monitoring_minimal(self, client):
        """Test monitoring start with minimal required fields."""
        payload = {
            "email": "minimal-monitor@example.com",
            "domain": "https://minimal-monitor.com",
        }
        
        response = client.post("/public/start-monitoring", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_start_monitoring_domain_normalization(self, client):
        """Test that domains without protocol are normalized."""
        payload = {
            "email": "normalize@example.com",
            "domain": "normalize.com",  # No protocol
        }
        
        response = client.post("/public/start-monitoring", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_start_monitoring_upgrade_lead(self, client):
        """Test upgrading a lead to active customer."""
        email = "upgrade@example.com"
        
        # First create a lead
        lead_payload = {
            "email": email,
            "domain": "upgrade.com",
        }
        response1 = client.post("/public/leads", json=lead_payload)
        assert response1.status_code == 200
        
        # Then start monitoring (should upgrade)
        monitor_payload = {
            "email": email,
            "domain": "upgrade.com",
        }
        response2 = client.post("/public/start-monitoring", json=monitor_payload)
        assert response2.status_code == 200
        data = response2.json()
        assert data["success"] is True
    
    def test_start_monitoring_already_active(self, client):
        """Test starting monitoring for already active customer."""
        payload = {
            "email": "already-active@example.com",
            "domain": "already-active.com",
        }
        
        # First submission
        response1 = client.post("/public/start-monitoring", json=payload)
        assert response1.status_code == 200
        
        # Second submission
        response2 = client.post("/public/start-monitoring", json=payload)
        assert response2.status_code == 200
        data = response2.json()
        assert data["success"] is True
        assert "already" in data["message"].lower()
    
    def test_start_monitoring_invalid_email(self, client):
        """Test monitoring start with invalid email."""
        payload = {
            "email": "not-an-email",
            "domain": "example.com",
        }
        
        response = client.post("/public/start-monitoring", json=payload)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_start_monitoring_with_key_pages(self, client):
        """Test monitoring start with multiple key pages."""
        payload = {
            "email": "keypages@example.com",
            "domain": "keypages.com",
            "key_pages": "https://keypages.com/page1\nhttps://keypages.com/page2\nhttps://keypages.com/page3",
            "use_sitemap": False,
        }
        
        response = client.post("/public/start-monitoring", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
