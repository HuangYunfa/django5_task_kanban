from django.urls import reverse

print('Testing URL configurations:')
try:
    print(f'reports:index -> {reverse("reports:index")}')
    print('✅ reports:index URL OK')
except Exception as e:
    print(f'❌ reports:index URL error: {e}')

try:
    print(f'users:switch_account -> {reverse("users:switch_account")}')
    print('✅ users:switch_account URL OK')
except Exception as e:
    print(f'❌ users:switch_account URL error: {e}')

try:
    print(f'api:schema-swagger-ui-redirect -> {reverse("api:schema-swagger-ui-redirect")}')
    print('✅ api:schema-swagger-ui-redirect URL OK')
except Exception as e:
    print(f'❌ api:schema-swagger-ui-redirect URL error: {e}')

print('\nURL verification complete!')
