"""Email utilities for canonicalization and validation."""


def canonicalize_email(email: str) -> str:
    """
    Canonicalize an email address to prevent abuse via Gmail dot/plus tricks.
    
    Rules:
    - Lowercase and trim whitespace
    - For Gmail/Googlemail domains:
      - Remove all dots from local part
      - Strip everything after '+' in local part
      - Normalize domain to 'gmail.com'
    
    Args:
        email: Raw email address
        
    Returns:
        Canonicalized email address
        
    Examples:
        >>> canonicalize_email("User.Name+tag@Gmail.COM")
        'username@gmail.com'
        >>> canonicalize_email("user.name@googlemail.com")
        'username@gmail.com'
        >>> canonicalize_email("user@example.com")
        'user@example.com'
    """
    # Lowercase and trim
    email = email.strip().lower()
    
    # Split into local and domain parts
    if "@" not in email:
        return email  # Invalid email, return as-is
    
    local, domain = email.rsplit("@", 1)
    
    # Gmail-specific canonicalization
    if domain in ("gmail.com", "googlemail.com"):
        # Remove dots
        local = local.replace(".", "")
        # Strip +tag suffix
        if "+" in local:
            local = local.split("+")[0]
        # Normalize domain to gmail.com
        domain = "gmail.com"
    
    return f"{local}@{domain}"
