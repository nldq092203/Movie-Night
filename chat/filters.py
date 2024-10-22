from django_filters import rest_framework as filters
from chat.models import ChatGroup, GroupMessage
from django.db.models import Q

class ChatGroupFilter(filters.FilterSet):
    group_name = filters.CharFilter(field_name='group_name', lookup_expr='icontains')
    groupchat_name = filters.CharFilter(field_name='groupchat_name', lookup_expr='icontains')
    member_email = filters.CharFilter(field_name='members__user__email', lookup_expr='icontains', label='Member Email')
    groupchat_name_or_member_email = filters.CharFilter(method='filter_by_groupchat_name_or_member_email', label="Search by Group Name or Member Email")

    class Meta:
        model = ChatGroup
        fields = ['group_name', 'groupchat_name', 'member_email']

    def filter_by_groupchat_name_or_member_email(self, queryset, name, value):
        """
        Custom filter to search by groupchat_name or members' email.
        """
        return queryset.filter(
            Q(groupchat_name__icontains=value) | 
            Q(membership__user__email__icontains=value) 
        ).distinct()

class GroupMessageFilter(filters.FilterSet):
    body = filters.CharFilter(field_name='body', lookup_expr='icontains')

    class Meta:
        model = GroupMessage
        fields = ['body']