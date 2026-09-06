ALLOWED_TRANSITIONS = {

    'pending': [
        'confirmed',
        'cancelled',
    ],

    'confirmed': [

        'cancelled',
    ],

    'cancelled': [],

}


def can_transition(current_status, new_status):
    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        []
    )

    return new_status in allowed_statuses
