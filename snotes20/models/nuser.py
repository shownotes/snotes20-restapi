import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models, transaction
from django.core.mail import send_mail
from django.core import validators
from django.utils import timezone
from django.core.validators import RegexValidator, ValidationError
from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import login, authenticate


def get_random_color():
    # close enough to fast..
    while True:
        cc = hex(random.getrandbits(28))[2:8].upper()
        try:
            validate_user_color(cc)
            return cc
        except:
            pass


def get_color_luminosity(color):
    # based on etherpad-lite (apache)
    # https://github.com/ether/etherpad-lite/blob/7b9fd81284a6e2191d007769c899907ea3f64232/src/static/js/colorutils.js#L111-L115
    c = [
        int(color[0:2], 16) / 255,
        int(color[2:4], 16) / 255,
        int(color[4:6], 16) / 255
    ]

    return c[0] * 0.30 + c[1] * 0.59 + c[2] * 0.11


def validate_user_color(color):
    lum = get_color_luminosity(color)

    if lum < 0.5:
        raise ValidationError('color too dark')


class NUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('username', max_length=30, unique=True,
        validators=[validators.RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.', 'invalid')])

    email = models.EmailField('email', unique=True)
    is_staff = models.BooleanField('is_staff', default=False)
    is_active = models.BooleanField('is_active', default=False)
    date_joined = models.DateTimeField('date_joined', default=timezone.now)
    date_login = models.DateTimeField('date_login', null=True, blank=True)
    color = models.CharField(max_length=6, default=get_random_color,
                             validators=[
                                 RegexValidator(regex='^[A-F0-9]{6}$', message='No color', code='nocolor'),
                                 validate_user_color
                             ])

    migrated = models.BooleanField(default=True)
    showpad_password = models.CharField(max_length=500, null=True, blank=True, default=None)
    bio = models.CharField(max_length=400, default='', blank=True)
    pw_reset_token = models.CharField(max_length=30, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        if not self.pw_reset_token:
            self.pw_reset_token = None
        if not self.showpad_password:
            self.showpad_password = None
        super(NUser, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def set_password(self, raw_password):
        self.migrated = True
        self.showpad_password = None

        super(NUser).set_password(raw_password)

    def set_password_keep_session(self, request, raw_password):
        self.set_password(raw_password)
        self.save()

        auth_user = authenticate(username=self.username, password=raw_password)
        login(request, auth_user)

    def email_user(self, subject, message, from_email=None, recipient=None, **kwargs):
        if recipient is None:
            recipient = self.email
        send_mail(subject, message, from_email, [recipient], **kwargs)

    def _email_user_template(self, tpl, context, lang, recipient=None):
        options = settings.EMAILS[tpl]
        siteurl = settings.SITEURL

        context['username'] = self.username
        context['siteurl'] = siteurl

        c = Context(context)

        text_content = render_to_string(tpl + '_' + lang + '.txt', c)
        self.email_user(options['subject'][lang], text_content, recipient=recipient)

    def add_email_token(self, email):
        token = '%030x' % random.randrange(16**30)
        email_token = NUserEmailToken(user=self, email=email, token=token)
        email_token.save()
        return email_token

    def check_email_token(self, token):
        return self.email_tokens.get(token=token)

    def apply_email_token(self, token_obj):
        self.email = token_obj.email
        self.is_active = True
        token_obj.delete()
        self.save()

    def email_user_activation(self, lang, token):
        ctx = { 'token': token }
        self._email_user_template('activation', ctx, lang)

    def email_new_mail_confirmation(self, lang, token, email):
        ctx = { 'token': token }
        self._email_user_template('newmail_confirmation', ctx, lang, recipient=email)

    def set_pw_reset_token(self):
        token = '%030x' % random.randrange(16**30)
        self.pw_reset_token = token
        self.save()

    def check_pw_reset_token(self, token):
        return self.pw_reset_token is not None and\
               token is not None and\
               self.pw_reset_token == token

    def apply_pw_reset_token(self, password):
        print(password)
        self.pw_reset_token = None
        self.set_password(password)
        self.save()

    def email_pw_reset(self, lang):
        ctx = {'token': self.pw_reset_token}
        self._email_user_template('pwreset', ctx, lang)

class NUserEmailToken(models.Model):
    user = models.ForeignKey(NUser, related_name='email_tokens')
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=30)

    class Meta:
        verbose_name = "Email token"


class NUserSocialType(models.Model):
    name = models.SlugField(primary_key=True)
    human_name = models.CharField(max_length=20)
    icon = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.human_name

    def save(self, *args, **kwargs):
        if not self.icon:
            self.icon = None
        super(NUserSocialType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Social Type"


class NUserSocial(models.Model):
    user = models.ForeignKey(NUser, db_index=True, related_name="socials")
    type = models.ForeignKey(NUserSocialType, db_index=True)
    value = models.CharField(max_length=20)

    def __str__(self):
        return self.type.human_name + "(" + self.value + ")"

    class Meta:
        unique_together = ('user', 'type')
        verbose_name = "Social"
