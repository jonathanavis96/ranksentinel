"""Tests for email canonicalization and deduplication."""

import pytest

from ranksentinel.email_utils import canonicalize_email

# Check if fastapi is available for API tests
try:
    from fastapi.testclient import TestClient
    from ranksentinel.api import app
    from ranksentinel.db import connect, init_db
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.fixture
def client(tmp_path):
    """Create a test client with a temporary database."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi not available")
    
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


@pytest.fixture
def conn(tmp_path):
    """Create a test database connection."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi not available")
    
    from ranksentinel.config import Settings
    
    db_path = tmp_path / "test.db"
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    connection = connect(test_settings)
    init_db(connection)
    
    yield connection
    
    connection.close()


class TestEmailCanonicalization:
    """Test email canonicalization utility function."""
    
    def test_lowercase_and_trim(self):
        """Test basic lowercase and trimming."""
        assert canonicalize_email("  User@Example.COM  ") == "user@example.com"
        assert canonicalize_email("ADMIN@SITE.ORG") == "admin@site.org"
    
    def test_gmail_dot_removal(self):
        """Test Gmail dot removal in local part."""
        assert canonicalize_email("user.name@gmail.com") == "username@gmail.com"
        assert canonicalize_email("u.s.e.r@gmail.com") == "user@gmail.com"
        assert canonicalize_email("first.last@gmail.com") == "firstlast@gmail.com"
    
    def test_gmail_plus_tag_removal(self):
        """Test Gmail plus tag removal."""
        assert canonicalize_email("user+tag@gmail.com") == "user@gmail.com"
        assert canonicalize_email("user+spam@gmail.com") == "user@gmail.com"
        assert canonicalize_email("user+test123@gmail.com") == "user@gmail.com"
    
    def test_gmail_dot_and_plus_combined(self):
        """Test combined Gmail dot and plus tag handling."""
        assert canonicalize_email("user.name+tag@gmail.com") == "username@gmail.com"
        assert canonicalize_email("first.last+spam@gmail.com") == "firstlast@gmail.com"
        assert canonicalize_email("U.S.E.R+Test@Gmail.COM") == "user@gmail.com"
    
    def test_googlemail_domain_normalization(self):
        """Test googlemail.com normalization to gmail.com."""
        assert canonicalize_email("user@googlemail.com") == "user@gmail.com"
        assert canonicalize_email("user.name@googlemail.com") == "username@gmail.com"
        assert canonicalize_email("user+tag@googlemail.com") == "user@gmail.com"
        assert canonicalize_email("user.name+tag@GoogleMail.COM") == "username@gmail.com"
    
    def test_non_gmail_domains_unchanged(self):
        """Test that non-Gmail domains preserve dots and plus signs."""
        assert canonicalize_email("user.name@example.com") == "user.name@example.com"
        assert canonicalize_email("user+tag@example.com") == "user+tag@example.com"
        assert canonicalize_email("first.last+test@yahoo.com") == "first.last+test@yahoo.com"
    
    def test_invalid_email_passthrough(self):
        """Test that invalid emails are returned as-is after lowercase/trim."""
        assert canonicalize_email("notanemail") == "notanemail"
        assert canonicalize_email("  INVALID  ") == "invalid"
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert canonicalize_email("") == ""
        assert canonicalize_email("@") == "@"
        assert canonicalize_email("user@") == "user@"
        assert canonicalize_email("@domain.com") == "@domain.com"


class TestEmailDeduplicationAPI:
    """Test email deduplication in API endpoints."""
    
    def test_start_monitoring_duplicate_detection(self, client, conn):
        """Test that duplicate canonical emails are detected in start_monitoring."""
        # Create first customer with user@gmail.com
        response1 = client.post(
            "/public/start-monitoring",
            json={
                "email": "user@gmail.com",
                "domain": "example.com",
                "use_sitemap": True,
            },
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["success"] is True
        customer_id_1 = data1["customer_id"]
        
        # Try to create with dot variant - should detect as duplicate
        response2 = client.post(
            "/public/start-monitoring",
            json={
                "email": "u.s.e.r@gmail.com",
                "domain": "example2.com",
                "use_sitemap": True,
            },
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["success"] is True
        assert data2["customer_id"] == customer_id_1  # Same customer
        assert ("already" in data2["message"].lower() or "trial" in data2["message"].lower())
        
        # Try to create with plus variant - should detect as duplicate
        response3 = client.post(
            "/public/start-monitoring",
            json={
                "email": "user+spam@gmail.com",
                "domain": "example3.com",
                "use_sitemap": True,
            },
        )
        assert response3.status_code == 200
        data3 = response3.json()
        assert data3["success"] is True
        assert data3["customer_id"] == customer_id_1  # Same customer
        
        # Try googlemail.com variant - should detect as duplicate
        response4 = client.post(
            "/public/start-monitoring",
            json={
                "email": "user@googlemail.com",
                "domain": "example4.com",
                "use_sitemap": True,
            },
        )
        assert response4.status_code == 200
        data4 = response4.json()
        assert data4["success"] is True
        assert data4["customer_id"] == customer_id_1  # Same customer
    
    def test_start_monitoring_non_gmail_preserves_dots(self, client, conn):
        """Test that non-Gmail domains preserve dots as separate users."""
        # Create first customer
        response1 = client.post(
            "/public/start-monitoring",
            json={
                "email": "user@example.com",
                "domain": "site1.com",
                "use_sitemap": True,
            },
        )
        assert response1.status_code == 200
        customer_id_1 = response1.json()["customer_id"]
        
        # Create with dot - should be different customer for non-Gmail
        response2 = client.post(
            "/public/start-monitoring",
            json={
                "email": "u.s.e.r@example.com",
                "domain": "site2.com",
                "use_sitemap": True,
            },
        )
        assert response2.status_code == 200
        customer_id_2 = response2.json()["customer_id"]
        
        # Should be different customers
        assert customer_id_1 != customer_id_2
    
    def test_database_stores_raw_and_canonical(self, client, conn):
        """Test that database stores both email_raw and email_canonical."""
        # Create customer with Gmail variant
        response = client.post(
            "/public/start-monitoring",
            json={
                "email": "User.Name+Tag@Gmail.COM",
                "domain": "example.com",
                "use_sitemap": True,
            },
        )
        assert response.status_code == 200
        customer_id = response.json()["customer_id"]
        
        # Check database
        from ranksentinel.db import fetch_one
        customer = fetch_one(
            conn,
            "SELECT email_raw, email_canonical FROM customers WHERE id=?",
            (customer_id,),
        )
        
        assert customer["email_raw"] == "user.name+tag@gmail.com"  # Lowercased but preserved
        assert customer["email_canonical"] == "username@gmail.com"  # Canonicalized
    
    def test_uniqueness_constraint_on_canonical_email(self, client, conn):
        """Test that database enforces uniqueness on email_canonical."""
        # Create first customer
        response1 = client.post(
            "/public/start-monitoring",
            json={
                "email": "user@gmail.com",
                "domain": "example.com",
                "use_sitemap": True,
            },
        )
        assert response1.status_code == 200
        
        # The API should handle duplicates gracefully, not raise database errors
        response2 = client.post(
            "/public/start-monitoring",
            json={
                "email": "u.s.e.r@gmail.com",
                "domain": "example.com",
                "use_sitemap": True,
            },
        )
        assert response2.status_code == 200
        assert response2.json()["success"] is True
