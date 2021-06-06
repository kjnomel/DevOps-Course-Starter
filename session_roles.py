from flask import session

USERS_ROLES = [
    { 'id': 'kjnomel', 'role': 'writer' },
    { 'id': 'dummy', 'role': 'reader' }
]


def get_roles():
    return session.get('roles', USERS_ROLES)


def get_role(id):
    users_roles = get_roles()
    user_role_map = next((user_role for user_role in users_roles if user_role['id'] == id), None)
    if user_role_map:
        user_role = user_role_map['role']
        return user_role
    else:
        return 'reader'


def add_role(id, role='reader'):
    users_roles = get_roles()
    user_role = { 'id': id, 'role': role }
    users_roles.append(user_role)
    session['roles'] = users_roles
    return user_role


def save_role(role):
    existing_roles = get_roles()
    updated_roles = [role if role['id'] == existing_roles['id'] else existing_role for existing_role in existing_roles]
    session['items'] = updated_roles
    return role
