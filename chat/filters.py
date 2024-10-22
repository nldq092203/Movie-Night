from django_filters import rest_framework as filters
from chat.models import ChatGroup, GroupMessage
from django.db.models import Q

class ChatGroupFilter(filters.FilterSet):
    """
    This filter class is used for filtering chat groups based on various attributes such as:
    
    - `group_name`: A partial search on the group's unique name.
    - `groupchat_name`: A partial search on the group's display name (visible to users).
    - `member_email`: A partial search for chat groups based on a member's email.
    - `groupchat_name_or_member_email`: A custom filter that allows searching for chat groups either by 
      the group's display name (`groupchat_name`) or by a member's email.
    """

    # Partial search on the group_name field (case-insensitive)
    group_name = filters.CharFilter(field_name='group_name', lookup_expr='icontains')

    # Partial search on the groupchat_name field (case-insensitive)
    groupchat_name = filters.CharFilter(field_name='groupchat_name', lookup_expr='icontains')

    # Partial search on the member's email (case-insensitive)
    member_email = filters.CharFilter(field_name='members__user__email', lookup_expr='icontains', label='Member Email')

    # Custom filter to search either by groupchat name or member's email
    groupchat_name_or_member_email = filters.CharFilter(
        method='filter_by_groupchat_name_or_member_email', 
        label="Search by Group Name or Member Email"
    )

    class Meta:
        """
        The `Meta` class defines the model that this filter applies to and the fields that can be filtered.
        """
        model = ChatGroup  # The model being filtered is the ChatGroup model
        fields = ['group_name', 'groupchat_name', 'member_email']  # Defines the fields we can filter by

    def filter_by_groupchat_name_or_member_email(self, queryset, name, value):
        """
        Custom filter method to allow searching for groups based on either the groupchat's display name
        (`groupchat_name`) or the email of a member in the group.
        
        - `queryset`: The current queryset of chat groups being filtered.
        - `name`: The name of the filter (not used here).
        - `value`: The search term provided by the user.
        
        This method returns a filtered queryset where the `groupchat_name` contains the search value 
        or where a member's email contains the search value.
        """
        return queryset.filter(
            Q(groupchat_name__icontains=value) |  # Matches groupchat name
            Q(membership__user__email__icontains=value)  # Matches member email
        ).distinct()  # Ensures no duplicate results
    
class GroupMessageFilter(filters.FilterSet):
    body = filters.CharFilter(field_name='body', lookup_expr='icontains')

    class Meta:
        model = GroupMessage
        fields = ['body']