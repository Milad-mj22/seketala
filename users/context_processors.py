
from users.models import MenuItem, UserRole, jobs



def menu_items_processor(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return {'menu_items': []}

        # گرفتن نقش‌های کاربر
        roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)

        # job = jobs.objects.filter(name=user.profile.).first()
    # 
        job = user.profile.job_position.name

        items = user.profile.job_position.items.all()

        # To efficiently fetch related submenus of these items (assuming submenus is a related_name)
        items = items.prefetch_related('submenus')



        # گرفتن آیتم‌های منو مرتبط با نقش‌ها
        # items = MenuItem.objects.filter(roles__id__in=roles).distinct().order_by('order')

        return {'menu_items': items}    
    
    except:
        #print('Error in menu_items_processor')
        return {'menu_items': None}    
