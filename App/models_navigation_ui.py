from django.db import models

class NavigationUiGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    order = models.IntegerField(default=0)
    visible_to_roles = models.JSONField(default=list, help_text="List of roles that can see this navigation group")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'navigation_ui_group'
        verbose_name = 'Navigation UI Group'
        verbose_name_plural = 'Navigation UI Groups'
        ordering = ['order', 'name']

class NavigationUiItem(models.Model):
    group = models.ForeignKey(NavigationUiGroup, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    title = models.CharField(max_length=100)
    url_name = models.CharField(max_length=100, help_text="Django URL name")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class")
    badge_text = models.CharField(max_length=20, blank=True, null=True, help_text="Badge text (e.g., 'New', '5')")
    badge_class = models.CharField(max_length=50, blank=True, null=True, default='badge-primary', help_text="Bootstrap badge class")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    visible_to_roles = models.JSONField(default=list, help_text="List of roles that can see this item")
    requires_permission = models.CharField(max_length=100, blank=True, null=True, help_text="Required permission to view this item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def has_children(self):
        return self.children.filter(is_active=True).exists()

    class Meta:
        db_table = 'navigation_ui_items'
        verbose_name = 'Navigation UI Item'
        verbose_name_plural = 'Navigation UI Items'
        ordering = ['order', 'title']
