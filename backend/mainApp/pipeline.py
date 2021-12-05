from .models import *

def update_user_data(strategy, details, backend, user=None, *args, **kwargs):
    """
    Update user details using data from provider. Compared to the default
    strategy, this pipeline function does not override user account details if
    they were already previously inserted
    (i.e. len(field_current_value)>0 implies no update)
    """

    if not user:
        return

    registeredUser = RegisteredUser.objects.get(user=user)
    if registeredUser.registration_provider is None or \
        len(registeredUser.registration_provider)==0 \
    :
        registeredUser.registration_provider = backend.name
        registeredUser.save()


    changed = False
    field_mapping = strategy.setting('USER_FIELD_MAPPING', {}, backend)
    for name, value in details.items():
        name = field_mapping.get(name, name)
        if value is not None and hasattr(user, name):
            current_value = getattr(user, name, None)
            if len(current_value)==0:
                changed = True
                setattr(user, name, value)
    # Notifying the change, in case some user attributes were updated:
    if changed:
        strategy.storage.user.changed(user)
