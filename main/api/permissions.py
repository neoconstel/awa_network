from rest_framework import permissions

IsAdmin = permissions.IsAdminUser
IsAuthenticated = permissions.IsAuthenticated
IsAuthenticatedElseReadOnly = permissions.IsAuthenticatedOrReadOnly


class IsAdminElseReadOnly(permissions.IsAdminUser):
    '''The request allows full access if user is admin, else it only allows
    read-only access'''

    def has_permission(self, request, view):
        # if this is a GET, OPTIONS, or HEAD request
        if request.method in permissions.SAFE_METHODS:
            return True

        admin_permission = request.user and request.user.is_staff
        return admin_permission


class IsArtworkAuthorElseReadOnly(permissions.BasePermission):
    '''The request allows full access if user is the ArtworkAuthor, else it only
    allows read-only access'''

    def has_object_permission(self, request, view, obj):
        # if this is a GET, OPTIONS, or HEAD request
        if request.method in permissions.SAFE_METHODS:
            return True

        user_permission = request.user and obj.artist.user == request.user
        return user_permission or request.user.is_staff


class IsArtistUserElseReadOnly(permissions.BasePermission):
    '''The request allows full access if user is the Artist, else it only
    allows read-only access'''

    def has_object_permission(self, request, view, obj):
        # if this is a GET, OPTIONS, or HEAD request
        if request.method in permissions.SAFE_METHODS:
            return True

        user_permission = request.user and obj.user == request.user
        return user_permission or request.user.is_staff
        

class IsCommentAuthorElseReadOnly(permissions.BasePermission):
    '''The request allows full access if user is the CommentAuthor, else it only
    allows read-only access'''
    def has_object_permission(self, request, view, obj):
        # if this is a GET, OPTIONS, or HEAD request
        if request.method in permissions.SAFE_METHODS:
            return True

        user_permission = request.user and obj.user == request.user
        return user_permission or request.user.is_staff


class IsEnabledReviewAuthorOrApprovedReadonly(permissions.BasePermission):
    '''The request allows full access if user is in Reviewers group and review 
    owner, else it only allows read-only access (provided that the review is
    approved) otherwise access isn't granted at all'''

    def has_object_permission(self, request, view, obj):
        # if this is a GET, OPTIONS, or HEAD request AND review is approved
        if request.method in permissions.SAFE_METHODS and obj.approved:
            return True

        user_permission = request.user and obj.user == request.user \
            and request.user.groups.get(name='Reviewers') != None
        return user_permission or request.user.is_staff \
                or request.user.is_superuser
    