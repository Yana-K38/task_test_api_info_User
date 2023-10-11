def sorted_query(sort_by: str):
    base_query = """
        SELECT id, username, email, avatar, phone_number, is_active, is_superuser, is_verified
        FROM users
    """
    if sort_by:
        if sort_by == "username":
            order_by = "ORDER BY username"
        elif sort_by == "email":
            order_by = "ORDER BY email"
        elif sort_by == "is_active":
            order_by = "ORDER BY is_active"
        elif sort_by == "is_superuser":
            order_by = "ORDER BY is_superuser"
        elif sort_by == "is_verified":
            order_by = "ORDER BY is_verified"
        else:
            raise ValueError("Invalid sort_by value")
        sql_query = f"{base_query} {order_by}"
    else:
        sql_query = base_query
    return sql_query
