from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


MAX_LENGTH = 255


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    Copied from django.contrib.auth.models.AbstractUser.
    The changes performed is add department info and methods
     to user
    """
    username = models.CharField(
        _('username'),
        max_length=MAX_LENGTH,
        unique=True,
        help_text=_('Required. %s characters or fewer. Letters, digits and @/./+/-/_ or / only.') % MAX_LENGTH,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    full_name = models.CharField(_('full name'), max_length=80, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_connected = models.DateTimeField(_('date last connected to service'), blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    weixin_nickname = models.CharField(max_length=60, null=True, blank=True, db_index=True)
    weixin_img = models.CharField(max_length=255, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the full name for the user.
        """
        return self.full_name

    def get_short_name(self):
        """
        Returns full name as short name for the user.
        """
        return self.full_name

    def get_all_permissions(self, obj=None):
        return sorted(super(User, self).get_all_permissions(obj))