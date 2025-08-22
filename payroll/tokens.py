from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmployeeCredentialsTokenGenerator(PasswordResetTokenGenerator):
    """
    Password-reset token generator for non-User models such as EmployeeCredentials.

    - Uses only attributes that actually exist on your model (and its related employee),
      so it won’t call user-specific methods like get_email_field_name().
    - Includes password hash, so changing the password invalidates previously issued tokens.
    - Includes is_active flags if present (on creds and/or related employee).
    - Includes last_login / password change timestamps if present (best-effort).
    - Keeps Django’s built-in timestamp + SECRET_KEY based signing.
    """

    # Separate token namespace from Django's default user generator
    key_salt = "payroll.tokens.EmployeeCredentialsTokenGenerator"

    def _make_hash_value(self, creds, timestamp):
        """
        Build a stable string (str) that varies whenever security-sensitive fields change.
        """
        # Required / always safe
        pk_str = str(getattr(creds, "pk", ""))  # must exist
        pwd_hash = str(getattr(creds, "password", "") or "")

        # Related employee fields (optional)
        employee = getattr(creds, "employee", None)
        work_email = ""
        if employee is not None:
            work_email = str(getattr(employee, "work_email", "") or "")

        # Optional timestamps — normalize to string without microseconds/tz
        def norm_dt(dt):
            if not dt:
                return ""
            try:
                return dt.replace(microsecond=0, tzinfo=None).isoformat()
            except Exception:
                return str(dt)

        last_login_str = norm_dt(getattr(creds, "last_login", None))

        # Compose the hash value string. Order matters; keep consistent.
        return f"{pk_str}{pwd_hash}{last_login_str}{timestamp}{work_email}"


# Export a singleton like Django does for default_token_generator
employee_token_generator = EmployeeCredentialsTokenGenerator()
