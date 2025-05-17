# electronic_card_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from delegate_card_app.views import home_page_view, query_delegate_view, scan_checkin_view,  navigation_page_view
from delegate_card_app.views import submit_delegate_info_view
from delegate_card_app.views import dashboard_view, dashboard_data_api, delegate_list_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # 注意：你有一个 'api/' 前缀的 include，这可能会导致应用内的URL也带有 'api/' 前缀
    # 如果 delegate_card_app.urls 里面也有叫 'delegate_list' 的 URL，并且也使用了 'delegate_card_app' 命名空间
    # 那么 'delegate_card_app:delegate_list' 会解析到那个应用内的URL
    path('api/', include('delegate_card_app.urls')), # 假设这是给DRF ViewSet用的
    path('submit-info/', submit_delegate_info_view, name='submit_delegate_info_page'),
    path('query/', query_delegate_view, name='query_delegate_page'),
    path('scan-checkin/', scan_checkin_view, name='scan_checkin_page'),
    path('card-display/', home_page_view, name='home'),
    path('', navigation_page_view, name='navigation_page'),
    path('dashboard/', dashboard_view, name='dashboard_page'),
    path('api/dashboard-data/', dashboard_data_api, name='dashboard_data_api'), # 这个API路径可能与上面的 'api/' include 冲突或混淆
    path('delegates-list/', delegate_list_view, name='delegate_list'), # <--- 修改这里
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # 确保静态文件服务也配置了