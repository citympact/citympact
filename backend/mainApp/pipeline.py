def update_user_data(strategy, details, backend, user=None, *args, **kwargs):
    """
    Update user details using data from provider. Compared to the default
    strategy, this pipeline function does not override user account details if
    they were already previously inserted
    (i.e. len(field_current_value)>0 implies no update)
    """

    if not user:
        return
    changed = False
    for name, value in details.items():
        name = field_mapping.get(name, name)
        if value is None or not hasattr(user, name) or name in protected:
            continue

        current_value = getattr(user, name, None)

        if len(current_value)>0:
            continue

        changed = True
        setattr(user, name, value)

    if changed:
        strategy.storage.user.changed(user)
