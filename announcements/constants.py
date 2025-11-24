"""
Announcements Constants
Centralized constants for the announcements module
"""

# Priority Levels (matching model choices)
PRIORITY_INFO = 'info'
PRIORITY_WARNING = 'warning'
PRIORITY_URGENT = 'urgent'

PRIORITY_CHOICES = [
    (PRIORITY_INFO, 'Information'),
    (PRIORITY_WARNING, 'Warning'),
    (PRIORITY_URGENT, 'Urgent'),
]

# Success Messages
SUCCESS_ANNOUNCEMENT_CREATED = "Announcement created successfully!"
SUCCESS_ANNOUNCEMENT_UPDATED = "Announcement updated successfully!"
SUCCESS_ANNOUNCEMENT_DELETED = "Announcement deleted successfully!"

# Error Messages
ERROR_ANNOUNCEMENT_NOT_FOUND = "Announcement not found."
ERROR_PERMISSION_DENIED = "You don't have permission to perform this action."
ERROR_INVALID_DATA = "Please correct the errors below."

# View Names (for URL reverse)
VIEW_ANNOUNCEMENT_LIST = 'announcement_list'
VIEW_ANNOUNCEMENT_DETAIL = 'announcement_detail'
VIEW_ANNOUNCEMENT_CREATE = 'announcement_create'
VIEW_ANNOUNCEMENT_UPDATE = 'announcement_update'
VIEW_ANNOUNCEMENT_DELETE = 'announcement_delete'

# Pagination
ANNOUNCEMENTS_PER_PAGE = 10

# Priority Badge Classes (Bootstrap)
PRIORITY_BADGE_CLASSES = {
    PRIORITY_INFO: 'info',
    PRIORITY_WARNING: 'warning',
    PRIORITY_URGENT: 'danger',
}
