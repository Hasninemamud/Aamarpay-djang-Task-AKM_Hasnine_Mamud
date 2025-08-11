from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import FileUpload, PaymentTransaction, ActivityLog

# Unregister the default User admin
admin.site.unregister(User)

# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'filename', 'upload_time', 'status', 'word_count', 'get_file_size')
    list_filter = ('status', 'upload_time', 'user')
    search_fields = ('filename', 'user__username')
    readonly_fields = ('id', 'user', 'filename', 'upload_time', 'status', 'word_count', 'file')
    date_hierarchy = 'upload_time'
    ordering = ('-upload_time',)
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'file', 'filename', 'upload_time')
        }),
        ('Processing Status', {
            'fields': ('status', 'word_count', 'error_message')
        }),
    )
    
    def get_file_size(self, obj):
        """Display file size in human readable format"""
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "N/A"
    get_file_size.short_description = 'File Size'
    
    def has_read_permission(self, request):
        return False
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_id', 'amount', 'status', 'timestamp', 'view_gateway_response')
    list_filter = ('status', 'timestamp', 'user')
    search_fields = ('transaction_id', 'user__username')
    readonly_fields = ('id', 'user', 'transaction_id', 'amount', 'status', 'gateway_response', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'transaction_id', 'amount', 'status', 'timestamp')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse', 'collapse-closed')
        }),
    )
    
    def view_gateway_response(self, obj):
        """Display gateway response in a readable format"""
        if obj.gateway_response:
            return '<button type="button" class="btn btn-sm btn-info" onclick="showGatewayResponse(this)">View Response</button>'
        return "No response"
    view_gateway_response.short_description = 'Gateway Response'
    view_gateway_response.allow_tags = True
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    class Media:
        js = ('admin/js/gateway_response.js',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'timestamp', 'view_metadata')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('action', 'user__username')
    readonly_fields = ('id', 'user', 'action', 'metadata', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('user', 'action', 'timestamp')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse', 'collapse-closed')
        }),
    )
    
    def view_metadata(self, obj):
        """Display metadata in a readable format"""
        if obj.metadata:
            return '<button type="button" class="btn btn-sm btn-info" onclick="showMetadata(this)">View Metadata</button>'
        return "No metadata"
    view_metadata.short_description = 'Metadata'
    view_metadata.allow_tags = True
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    class Media:
        js = ('admin/js/metadata_viewer.js',)


# # Custom admin site configuration
# admin.site.site_header = 'Payment & File Upload System'
# admin.site.site_title = 'Payment & File Upload Admin'
# admin.site.index_title = 'Welcome to Payment & File Upload Admin'