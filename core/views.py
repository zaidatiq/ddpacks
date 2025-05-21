from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from .tokens import email_verification_token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .models import User, Cart, CartItem
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

def serialize_sku_with_attributes(sku):
    attributes = SKUAttribute.objects.filter(sku=sku)
    attr_dict = {}
    for attr in attributes:
        attr_dict.setdefault(attr.key, []).append(attr.value)

    return {
        'sku': {
            'id': sku.id,
            'code': sku.code,
            'name': sku.name,
            'description': sku.description,
            'unit_of_measurement': sku.unit_of_measurement,
            'units_per_packet': sku.units_per_packet,
            'price': sku.price,
            'capacity': sku.capacity,
            'main_image': sku.main_image
        },
        'attributes': attr_dict
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

# @csrf_exempt
# def sku_list(request):
#     if request.method == 'GET':
#         skus = SKU.objects.all()
#         data = [serialize_basic_sku(sku) for sku in skus]
#         return JsonResponse(data, safe=False)

#     elif request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             if isinstance(data, dict):
#                 data = [data]

#             created = []
#             for item in data:
#                 sku = SKU.objects.create(
#                     code=item['sku_code'],
#                     name=item['name'],
#                     description=item['description'],
#                     unit_of_measurement=item['unit_of_measurement'],
#                     units_per_packet=item['units_per_packet'],
#                     price=item['price'],
#                     capacity=item['capacity'],
#                     main_image=item.get('main_image')
#                 )
#                 created.append({'sku_id': sku.id, 'sku_code': sku.code})

#             return JsonResponse({'message': 'SKUs created', 'created': created}, status=201)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)

# #product detail
# @csrf_exempt
# def sku_detail(request, sku_id):
#     try:
#         sku = SKU.objects.get(id=sku_id)
#     except SKU.DoesNotExist:
#         return JsonResponse({'error': 'SKU not found'}, status=404)

#     if request.method == 'GET':
#         # Basic SKU details
#         sku_data = {
#             'sku_id': sku.id,
#             'sku_code': sku.code,
#             'name': sku.name,
#             'description': sku.description,
#             'unit_of_measurement': sku.unit_of_measurement,
#             'units_per_packet': sku.units_per_packet,
#             'price': sku.price,
#             'capacity': sku.capacity,
#             'main_image': sku.main_image,
#         }

#         # Grouped Attributes
#         attrs = SKUAttribute.objects.filter(sku=sku)
#         attr_dict = {}

#         for attr in attrs:
#             key = attr.key
#             value = attr.value

#             if key == "image":
#                 if key not in attr_dict:
#                     attr_dict[key] = []
#                 attr_dict[key].append(value)
#             else:
#                 if key not in attr_dict:
#                     attr_dict[key] = value

#         # Merge attributes into response
#         sku_data['attributes'] = attr_dict

#         return JsonResponse(sku_data)

#     elif request.method == 'PUT':
#         data = json.loads(request.body)
#         for field in ['name', 'description', 'unit_of_measurement', 'units_per_packet', 'price', 'capacity', 'main_image']:
#             setattr(sku, field, data.get(field, getattr(sku, field)))
#         sku.save()
#         return JsonResponse({'message': 'SKU updated'})

#     elif request.method == 'DELETE':
#         sku.delete()
#         return JsonResponse({'message': 'SKU deleted'})



# # ------------------ ATTRIBUTES ------------------

# @csrf_exempt
# def attribute_list(request):
#     if request.method == 'GET':
#         data = serialize_attributes_grouped()
#         return JsonResponse(data, safe=False)

#     elif request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             if isinstance(data, dict):
#                 data = [data]

#             created = []
#             skipped = []

#             for item in data:
#                 sku_id = item['sku_id']
#                 sku = SKU.objects.get(id=sku_id)

#                 # Case 1: nested format
#                 if 'attributes' in item:
#                     for key, value in item['attributes'].items():
#                         if isinstance(value, list):
#                             for val in value:
#                                 if not SKUAttribute.objects.filter(sku=sku, key=key, value=val).exists():
#                                     attr = SKUAttribute.objects.create(sku=sku, key=key, value=val)
#                                     created.append({'id': attr.id, 'sku_id': sku.id, 'key': key, 'value': val})
#                                 else:
#                                     skipped.append({'sku_id': sku.id, 'key': key, 'value': val})
#                         else:
#                             if not SKUAttribute.objects.filter(sku=sku, key=key, value=value).exists():
#                                 attr = SKUAttribute.objects.create(sku=sku, key=key, value=value)
#                                 created.append({'id': attr.id, 'sku_id': sku.id, 'key': key, 'value': value})
#                             else:
#                                 skipped.append({'sku_id': sku.id, 'key': key, 'value': value})
#                 else:
#                     # Case 2: flat format
#                     if not SKUAttribute.objects.filter(sku=sku, key=item['key'], value=item['value']).exists():
#                         attr = SKUAttribute.objects.create(
#                             sku=sku,
#                             key=item['key'],
#                             value=item['value']
#                         )
#                         created.append({'id': attr.id, 'sku_id': sku.id})
#                     else:
#                         skipped.append({'sku_id': sku.id, 'key': item['key'], 'value': item['value']})

#             return JsonResponse({'message': 'Attributes processed', 'created': created, 'skipped_duplicates': skipped}, status=201)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
        
# @csrf_exempt        
# def sku_attributes(request, sku_id):
#     try:
#         sku = SKU.objects.get(id=sku_id)
#     except SKU.DoesNotExist:
#         return JsonResponse({'error': 'SKU not found'}, status=404)

#     if request.method == 'GET':
#         attributes = SKUAttribute.objects.filter(sku=sku)
#         grouped = {}
#         for attr in attributes:
#             grouped.setdefault(attr.key, []).append(attr.value)
#         return JsonResponse({'sku_id': sku.id, 'attributes': grouped})
#     elif request.method == 'PUT':
#         data = json.loads(request.body)
#         attr.key = data.get('key', attr.key)
#         attr.value = data.get('value', attr.value)
#         attr.save()
#         return JsonResponse({'message': 'Attribute updated'})

#     elif request.method == 'DELETE':
#         attr.delete()
#         return JsonResponse({'message': 'Attribute deleted'})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import json

from .models import SKU, SKUAttribute
from core.decorators import jwt_required, admin_required

@csrf_exempt
def sku_list(request):
    if request.method == 'GET':
        skus = SKU.objects.all()
        data = []
        for sku in skus:
            data.append({
                'sku_id': sku.id,
                'sku_code': sku.code,
                'name': sku.name,
                'description': sku.description,
                'price': sku.price,
                'main_image': sku.main_image,
            })
        return JsonResponse({'skus': data}, safe=False)

# ✅ Public Product Detail API (SKU + Attributes in single JSON)
@csrf_exempt
def sku_list(request):
    if request.method == 'GET':
        skus = SKU.objects.all()
        data = []
        for sku in skus:
            data.append({
                'id': sku.id,
                'sku_code': sku.code,
                'name': sku.name,
                'description': sku.description,
                'unit_of_measurement': sku.unit_of_measurement,
                'units_per_packet': sku.units_per_packet,
                'price': sku.price,
                'capacity': sku.capacity,
                'main_image': sku.main_image,
            })
        return JsonResponse({'skus': data}, status=200)
    else:
        return JsonResponse({'error': 'GET method required'}, status=405)
@csrf_exempt
def sku_detail_combined(request, sku_id):
    try:
        sku = SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
        return JsonResponse({'error': 'SKU not found'}, status=404)

    if request.method == 'GET':
        sku_data = {
            'sku_id': sku.id,
            'sku_code': sku.code,
            'name': sku.name,
            'description': sku.description,
            'unit_of_measurement': sku.unit_of_measurement,
            'units_per_packet': sku.units_per_packet,
            'price': sku.price,
            'capacity': sku.capacity,
            'main_image': sku.main_image,
        }

        attributes = SKUAttribute.objects.filter(sku=sku)
        attr_dict = {}
        for attr in attributes:
            if attr.key == "image":
                attr_dict.setdefault(attr.key, []).append(attr.value)
            else:
                attr_dict[attr.key] = attr.value

        sku_data['attributes'] = attr_dict

        return JsonResponse(sku_data)


# ✅ SKU Create / Update / Delete (Admin only)
@csrf_exempt
@admin_required
def sku_manage(request, sku_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sku = SKU.objects.create(
                code=data['sku_code'],
                name=data['name'],
                description=data['description'],
                unit_of_measurement=data['unit_of_measurement'],
                units_per_packet=data['units_per_packet'],
                price=data['price'],
                capacity=data['capacity'],
                main_image=data.get('main_image')
            )
            return JsonResponse({'message': 'SKU created', 'sku_id': sku.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'PUT' and sku_id:
        try:
            sku = SKU.objects.get(id=sku_id)
            data = json.loads(request.body)
            for field in ['name', 'description', 'unit_of_measurement', 'units_per_packet', 'price', 'capacity', 'main_image']:
                setattr(sku, field, data.get(field, getattr(sku, field)))
            sku.save()
            return JsonResponse({'message': 'SKU updated'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'SKU not found'}, status=404)

    elif request.method == 'DELETE' and sku_id:
        try:
            sku = SKU.objects.get(id=sku_id)
            sku.delete()
            return JsonResponse({'message': 'SKU deleted'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'SKU not found'}, status=404)


# ✅ SKU Attributes Create / Update / Delete (Admin only)
@csrf_exempt
@admin_required
def sku_attributes_manage(request, sku_id=None, attr_id=None):
    if request.method == 'POST' and sku_id:
        try:
            sku = SKU.objects.get(id=sku_id)
            data = json.loads(request.body)
            created = []

            for key, value in data.items():
                if isinstance(value, list):
                    for val in value:
                        attr, created_flag = SKUAttribute.objects.get_or_create(sku=sku, key=key, value=val)
                        if created_flag:
                            created.append({'id': attr.id, 'key': key, 'value': val})
                else:
                    attr, created_flag = SKUAttribute.objects.get_or_create(sku=sku, key=key, value=value)
                    if created_flag:
                        created.append({'id': attr.id, 'key': key, 'value': value})

            return JsonResponse({'message': 'Attributes processed', 'created': created}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'PUT' and attr_id:
        try:
            attr = SKUAttribute.objects.get(id=attr_id)
            data = json.loads(request.body)
            attr.key = data.get('key', attr.key)
            attr.value = data.get('value', attr.value)
            attr.save()
            return JsonResponse({'message': 'Attribute updated'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Attribute not found'}, status=404)

    elif request.method == 'DELETE' and attr_id:
        try:
            attr = SKUAttribute.objects.get(id=attr_id)
            attr.delete()
            return JsonResponse({'message': 'Attribute deleted'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Attribute not found'}, status=404)



# ------------------ INVENTORY ------------------

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# ✅ Inventory list + Create (Admin only for POST, JWT only for GET)
@csrf_exempt
@jwt_required
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
        # ✅ Only admin allowed
        if not request.user.is_admin:
            return JsonResponse({'error': 'Admin only access'}, status=403)
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


# ✅ Inventory update / delete (Admin only)
@csrf_exempt
@jwt_required
@admin_required
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

# @csrf_exempt
# def register_view(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             required_fields = ['email', 'password', 'full_name', 'company_name', 'phone', 'address']
#             for field in required_fields:
#                 if not data.get(field):
#                     return JsonResponse({'error': f'{field} is required'}, status=400)

#             if User.objects.filter(email=data['email']).exists():
#                 return JsonResponse({'error': 'Email already registered'}, status=400)

#             hashed_password = make_password(data['password'])

#             user = User.objects.create(
#                 email=data['email'],
#                 password=hashed_password,
#                 full_name=data['full_name'],
#                 company_name=data['company_name'],
#                 phone=data['phone'],
#                 address=data['address']
                
#             )
#             user.is_active = False  # Deactivate account until it is confirmed
#             user.save()
#             send_verification_email(request, user)
#             return JsonResponse({'message': 'User registered successfully'}, status=201)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

# def send_verification_email(request, user):
#     current_site = get_current_site(request)
#     subject = 'Activate Your Account'
#     message = render_to_string('email_verification.html', {
#         'user': user,
#         'domain': current_site.domain,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': email_verification_token.make_token(user),
#     })
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

# def activate_account(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user and email_verification_token.check_token(user, token):
#         user.is_active = True
#         user.is_verified = True
#         user.save()
#         return JsonResponse({'message': 'Email verified successfully.'})
#     else:
#         return JsonResponse({'error': 'Invalid verification link.'}, status=400)

# @csrf_exempt
# def login_view(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             password = data.get('password')

#             if not email or not password:
#                 return JsonResponse({'error': 'Email and password are required'}, status=400)

#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return JsonResponse({'error': 'Invalid email or password'}, status=400)

#             if not check_password(password, user.password):
#                 return JsonResponse({'error': 'Invalid email or password'}, status=400)

#             token = generate_jwt(user)

#             return JsonResponse({'token': token}, status=200)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)



# @jwt_required
# def protected_view(request):
#     return JsonResponse({'message': f'Hello, {request.user.full_name}! This is a protected endpoint.'})


# from django.contrib.auth.tokens import default_token_generator

# @csrf_exempt
# def request_password_reset(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         email = data.get('email')
#         try:
#             user = User.objects.get(email=email)
#             send_password_reset_email(request, user)
#             return JsonResponse({'message': 'Password reset email sent.'})
#         except User.DoesNotExist:
#             return JsonResponse({'error': 'User with this email does not exist.'}, status=400)

# def send_password_reset_email(request, user):
#     current_site = get_current_site(request)
#     subject = 'Reset Your Password'
#     message = render_to_string('password_reset_email.html', {
#         'user': user,
#         'domain': current_site.domain,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user),
#     })
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

# @csrf_exempt
# def reset_password(request, uidb64, token):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         new_password = data.get('password')
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#             if default_token_generator.check_token(user, token):
#                 user.set_password(new_password)
#                 user.save()
#                 return JsonResponse({'message': 'Password has been reset successfully.'})
#             else:
#                 return JsonResponse({'error': 'Invalid token.'}, status=400)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             return JsonResponse({'error': 'Invalid request.'}, status=400)





# #CART
# @jwt_required
# def add_to_cart(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         sku_id = data.get('sku_id')
#         quantity = data.get('quantity', 1)
#         try:
#             sku = SKU.objects.get(id=sku_id)
#             cart, created = Cart.objects.get_or_create(user=request.user)
#             cart_item, created = CartItem.objects.get_or_create(cart=cart, sku=sku)
#             if not created:
#                 cart_item.quantity += quantity
#             else:
#                 cart_item.quantity = quantity
#             cart_item.save()
#             return JsonResponse({'message': 'Item added to cart.'})
#         except SKU.DoesNotExist:
#             return JsonResponse({'error': 'SKU not found.'}, status=404)

# @jwt_required
# def view_cart(request):
#     try:
#         cart = Cart.objects.get(user=request.user)
#         items = CartItem.objects.filter(cart=cart)
#         data = [{'sku_id': item.sku.id, 'quantity': item.quantity} for item in items]
#         return JsonResponse({'cart_items': data})
#     except Cart.DoesNotExist:
#         return JsonResponse({'cart_items': []})

# @jwt_required
# def remove_from_cart(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         sku_id = data.get('sku_id')
#         try:
#             cart = Cart.objects.get(user=request.user)
#             cart_item = CartItem.objects.get(cart=cart, sku_id=sku_id)
#             cart_item.delete()
#             return JsonResponse({'message': 'Item removed from cart.'})
#         except (Cart.DoesNotExist, CartItem.DoesNotExist):
#             return JsonResponse({'error': 'Item not found in cart.'}, status=404)



@csrf_exempt
@admin_required
def admin_register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            required_fields = ['email', 'password', 'full_name', 'company_name', 'phone', 'address']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'error': 'Email already registered'}, status=400)

            user = User.objects.create(
                email=data['email'],
                password=make_password(data['password']),
                full_name=data['full_name'],
                company_name=data['company_name'],
                phone=data['phone'],
                address=data['address'],
                is_active=True,
                is_verified=True,
                role='admin'  # Forcefully set as admin
            )

            return JsonResponse({'message': 'Admin user registered successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ✅ Register
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
                address=data['address'],
                is_active=False  # Until verified
            )
            user.save()
            send_verification_email(request, user)
            return JsonResponse({'message': 'User registered successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def send_verification_email(request, user):
    current_site = get_current_site(request)
    subject = 'Activate Your Account'
    message = render_to_string('email_verification.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': email_verification_token.make_token(user),
    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

@csrf_exempt
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse({'error': 'Invalid verification link.'}, status=400)

    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        return JsonResponse({'message': 'Email verified successfully.'})
    else:
        return JsonResponse({'error': 'Invalid verification link.'}, status=400)

# ✅ Login with JWT return
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

            if not user.is_active:
                return JsonResponse({'error': 'Account not activated. Please verify your email.'}, status=403)

            token = generate_jwt(user)
            return JsonResponse({'token': token}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# ✅ Protected View
@jwt_required
def protected_view(request):
    return JsonResponse({'message': f'Hello, {request.user.full_name}! This is a protected endpoint.'})

# ✅ Password Reset Flow
@csrf_exempt
def request_password_reset(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(request, user)
            return JsonResponse({'message': 'Password reset email sent.'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User with this email does not exist.'}, status=400)

def send_password_reset_email(request, user):
    current_site = get_current_site(request)
    subject = 'Reset Your Password'
    message = render_to_string('password_reset_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

@csrf_exempt
def reset_password(request, uidb64, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('password')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return JsonResponse({'message': 'Password has been reset successfully.'})
            else:
                return JsonResponse({'error': 'Invalid token.'}, status=400)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({'error': 'Invalid request.'}, status=400)

# ✅ Cart APIs secured with JWT
@csrf_exempt
@jwt_required
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sku_id = data.get('sku_id')
        quantity = data.get('quantity', 1)
        try:
            sku = SKU.objects.get(id=sku_id)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, sku=sku)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'message': 'Item added to cart.'})
        except SKU.DoesNotExist:
            return JsonResponse({'error': 'SKU not found.'}, status=404)

@jwt_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        data = [{'sku_id': item.sku.id, 'quantity': item.quantity} for item in items]
        return JsonResponse({'cart_items': data})
    except Cart.DoesNotExist:
        return JsonResponse({'cart_items': []})
@csrf_exempt
@jwt_required
def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sku_id = data.get('sku_id')
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, sku_id=sku_id)
            cart_item.delete()
            return JsonResponse({'message': 'Item removed from cart.'})
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Item not found in cart.'}, status=404)