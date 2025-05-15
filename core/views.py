from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .models import User
import bcrypt
from .auth_utils import generate_jwt, jwt_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import SKU, SKUAttribute, Inventory
import json


# ------------------ SERIALIZER ------------------

def serialize_basic_sku(sku):
    return {
        'id': sku.id,
        'sku_code': sku.code,
        'name': sku.name,
        'description': sku.description,
        'unit_of_measurement': sku.unit_of_measurement,
        'units_per_packet': sku.units_per_packet,
        'case_config': sku.case_config,
        'price': float(sku.price),
        'capacity': sku.capacity,
        'main_image': sku.main_image
    }


def serialize_attributes_grouped():
    result = []
    sku_ids = SKUAttribute.objects.values_list('sku_id', flat=True).distinct()

    for sku_id in sku_ids:
        attributes = SKUAttribute.objects.filter(sku_id=sku_id)
        attr_dict = {}

        for attr in attributes:
            if attr.key == 'image':
                attr_dict.setdefault('image', []).append(attr.value)
            else:
                attr_dict[attr.key] = attr.value

        result.append({
            'sku_id': sku_id,
            'attributes': attr_dict
        })

    return result


# ------------------ SKU ------------------

@csrf_exempt
def sku_list(request):
    if request.method == 'GET':
        skus = SKU.objects.all()
        data = [serialize_basic_sku(sku) for sku in skus]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            if isinstance(data, dict):
                data = [data]

            created = []
            for item in data:
                sku = SKU.objects.create(
                    code=item['sku_code'],
                    name=item['name'],
                    description=item['description'],
                    unit_of_measurement=item['unit_of_measurement'],
                    units_per_packet=item['units_per_packet'],
                    price=item['price'],
                    capacity=item['capacity'],
                    main_image=item.get('main_image')
                )
                created.append({'sku_id': sku.id, 'sku_code': sku.code})

            return JsonResponse({'message': 'SKUs created', 'created': created}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def sku_detail(request, sku_id):
    try:
        sku = SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
        return JsonResponse({'error': 'SKU not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(serialize_basic_sku(sku))

    elif request.method == 'PUT':
        data = json.loads(request.body)
        for field in ['name', 'description', 'unit_of_measurement', 'units_per_packet', 'price', 'capacity', 'main_image']:
            setattr(sku, field, data.get(field, getattr(sku, field)))
        sku.save()
        return JsonResponse({'message': 'SKU updated'})

    elif request.method == 'DELETE':
        sku.delete()
        return JsonResponse({'message': 'SKU deleted'})


# ------------------ ATTRIBUTES ------------------

@csrf_exempt
def attribute_list(request):
    if request.method == 'GET':
        data = serialize_attributes_grouped()
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            if isinstance(data, dict):
                data = [data]

            created = []
            skipped = []

            for item in data:
                sku_id = item['sku_id']
                sku = SKU.objects.get(id=sku_id)

                # Case 1: nested format
                if 'attributes' in item:
                    for key, value in item['attributes'].items():
                        if isinstance(value, list):
                            for val in value:
                                if not SKUAttribute.objects.filter(sku=sku, key=key, value=val).exists():
                                    attr = SKUAttribute.objects.create(sku=sku, key=key, value=val)
                                    created.append({'id': attr.id, 'sku_id': sku.id, 'key': key, 'value': val})
                                else:
                                    skipped.append({'sku_id': sku.id, 'key': key, 'value': val})
                        else:
                            if not SKUAttribute.objects.filter(sku=sku, key=key, value=value).exists():
                                attr = SKUAttribute.objects.create(sku=sku, key=key, value=value)
                                created.append({'id': attr.id, 'sku_id': sku.id, 'key': key, 'value': value})
                            else:
                                skipped.append({'sku_id': sku.id, 'key': key, 'value': value})
                else:
                    # Case 2: flat format
                    if not SKUAttribute.objects.filter(sku=sku, key=item['key'], value=item['value']).exists():
                        attr = SKUAttribute.objects.create(
                            sku=sku,
                            key=item['key'],
                            value=item['value']
                        )
                        created.append({'id': attr.id, 'sku_id': sku.id})
                    else:
                        skipped.append({'sku_id': sku.id, 'key': item['key'], 'value': item['value']})

            return JsonResponse({'message': 'Attributes processed', 'created': created, 'skipped_duplicates': skipped}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def attribute_detail(request, attr_id):
    try:
        attr = SKUAttribute.objects.get(id=attr_id)
    except SKUAttribute.DoesNotExist:
        return JsonResponse({'error': 'Attribute not found'}, status=404)

    if request.method == 'PUT':
        data = json.loads(request.body)
        attr.key = data.get('key', attr.key)
        attr.value = data.get('value', attr.value)
        attr.save()
        return JsonResponse({'message': 'Attribute updated'})

    elif request.method == 'DELETE':
        attr.delete()
        return JsonResponse({'message': 'Attribute deleted'})


# ------------------ INVENTORY ------------------

@csrf_exempt
def inventory_list(request):
    if request.method == 'GET':
        inventories = Inventory.objects.all()
        data = [{
            'id': inv.id,
            'sku_id': inv.sku.id,
            'sku_code': inv.sku.code,
            'total': inv.total,
            'available': inv.available,
            'reserved': inv.reserved
        } for inv in inventories]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            if isinstance(data, dict):
                data = [data]

            created = []
            for item in data:
                sku = SKU.objects.get(id=item['sku_id'])
                inv = Inventory.objects.create(
                    sku=sku,
                    total=item['total'],
                    available=item['available'],
                    reserved=item['reserved']
                )
                created.append({'id': inv.id, 'sku_id': sku.id})

            return JsonResponse({'message': 'Inventory items added', 'created': created}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def inventory_detail(request, inv_id):
    try:
        inv = Inventory.objects.get(id=inv_id)
    except Inventory.DoesNotExist:
        return JsonResponse({'error': 'Inventory not found'}, status=404)

    if request.method == 'PUT':
        data = json.loads(request.body)
        inv.total = data.get('total', inv.total)
        inv.available = data.get('available', inv.available)
        inv.reserved = data.get('reserved', inv.reserved)
        inv.save()
        return JsonResponse({'message': 'Inventory updated'})

    elif request.method == 'DELETE':
        inv.delete()
        return JsonResponse({'message': 'Inventory deleted'})


#USER

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            required_fields = ['email', 'password', 'full_name', 'company_name', 'phone', 'address']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'error': 'Email already registered'}, status=400)

            hashed_password = make_password(data['password'])

            user = User.objects.create(
                email=data['email'],
                password=hashed_password,
                full_name=data['full_name'],
                company_name=data['company_name'],
                phone=data['phone'],
                address=data['address']
            )

            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid email or password'}, status=400)

            if not check_password(password, user.password):
                return JsonResponse({'error': 'Invalid email or password'}, status=400)

            token = generate_jwt(user)

            return JsonResponse({'token': token}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@jwt_required
def protected_view(request):
    return JsonResponse({'message': f'Hello, {request.user.full_name}! This is a protected endpoint.'})
