import re

def filter_from_get(instance_type, queryset, get):
    kwargs = {}
    args = []
    for param in get:
        splitted_param = param.split('__')
        field = splitted_param[0]
        prefix = splitted_param[-1] if len(splitted_param) > 1 else None
        value = get[param]

        if value == 'false':
            value = False
        if value == 'true':
            value = True

        if hasattr(instance_type, field):
            if prefix == 'or':
                or_values = get[param].split(',')
                field__prefix = field + '__icontains'
                q_objects = Q()
                for or_value in or_values:
                    filter_value = {
                        field__prefix: or_value
                    }
                    q_objects |= Q(**filter_value)
                args.append(q_objects)
            else:
                kwargs[param] = value

    return queryset.filter(*args, **kwargs)


def order_from_get(queryset, get):
    out_queryset = queryset
    if 'order_by' in get:
        order_by = get['order_by']
        if order_by != '':
            if get['order'] == 'DESC':
                order_by = '-' + order_by
            out_queryset = out_queryset.order_by(order_by)

    return out_queryset


def remove_spaces(str):
    text = re.sub('\s{2,}', ' ', str)
    return text


async def update_instance(instance='', responded_users='__all__'):
    import websockets, json
    from api.settings import DOMAIN

    print(instance)
    uri = "wss://" + DOMAIN + "/ws/?1"
    async with websockets.connect(uri) as ws:
         await ws.send(json.dumps({
            'action': 'update_instance',
            'data': {
                'instance': instance,
                'responded_users': responded_users
            }
        }))