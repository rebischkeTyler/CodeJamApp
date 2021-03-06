from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from donate.models import Donate, Category, SubCategory, Request, DonationMatch, RequestMatch
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie.authentication import SessionAuthentication
from django.db import IntegrityError
from tastypie.exceptions import BadRequest


class MultiPartResource(object):
    def deserialize(self, request, data, format=None):
        print(format)
        if not format:
            format = request.Meta.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            print(data)
            return data
        return super(MultiPartResource, self).deserialize(request, data, format)

class CategoryResource(ModelResource):

    class  Meta:
        queryset = Category.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()

        # resource_name = "category"

class SubCategoryResource(ModelResource):
    category = fields.ForeignKey(CategoryResource, 'category', null=True, full=True)

    class Meta:
      queryset = SubCategory.objects.all()
      filtering = {
            'category' : ALL_WITH_RELATIONS,
            }
      resource_name = 'subcategory'




class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'email', 'username', 'id']
        allowed_methods = ['get', 'post']
        resource_name = 'user'
        # authentication = SessionAuthentication
        authorization = Authorization()

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/register%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('register'), name='api_register'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')
        print(username, password)

        user = authenticate(username=username, password=password)

        print(user)

        if user:
            if user.is_active:
                login(request, user)
                u = User.objects.get(username=username)
                return self.create_response(request, {
                    'success': True,
                    'u': u,
                    'userId': user.id,
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                    }, HttpForbidden )
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
                }, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(UserResource, self).obj_create(bundle)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('Username already exists')

        return bundle

class DonateResource(MultiPartResource, ModelResource):
    category = fields.ForeignKey(CategoryResource, 'category', null=True, full=True)
    subcategory = fields.ForeignKey(SubCategoryResource, 'subcategory', null=True, full=True)
    author = fields.ForeignKey(UserResource, 'author', null=True, full=True)

    class Meta:
        queryset = Donate.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()
        filtering = {
            "author": ('exact')
        }

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/not_interested%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('not_interested'), name="api_not_interested"),
            ]

    def not_interested(self, request, **kwargs):
        print(request.GET.get('user', ))
        self.method_check(request, allowed=['get'])
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        queryset = Donate.objects.exclude(donateobj___interested=request.user)
        print('queryset variable', queryset)
        
        return self.create_response(request, { 'data': queryset})



    def obj_create(self, bundle, request=None, **kwargs):
        print(bundle)
        return super(DonateResource, self).obj_create(bundle, author=bundle.request.user)

    def build_schema(self):
        base_schema = super(DonateResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({'choices': f.choices,})
        return base_schema

class RequestResource(ModelResource):
    category = fields.ForeignKey(CategoryResource, 'category', null=True, full=True)
    subcategory = fields.ForeignKey(SubCategoryResource, 'subcategory', null=True, full=True)
    author = fields.ForeignKey(UserResource, 'author', null=True, full=True)

    class Meta:
        queryset = Request.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()
        filtering = {
            "author": ('exact')
        }


    def obj_create(self, bundle, **kwargs):
        return super(RequestResource, self).obj_create(bundle, author=bundle.request.user)

    def build_schema(self):
        base_schema = super(RequestResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
          if f.name in base_schema['fields'] and f.choices:
            base_schema['fields'][f.name].update({'choices': f.choices,})
        return base_schema

class DonationMatchResource(ModelResource):
    donate = fields.ForeignKey(DonateResource, 'donate', null=True, full=True)
    interested = fields.ForeignKey(UserResource, 'interested', null=True, full=True)

    class Meta:
        filtering = {
            "interested": ('exact'), 
            "donate": ('exact'),
            "approve_contact":('exact')
        }
        queryset = DonationMatch.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()

    def obj_create(self, bundle, **kwargs):
        return super(DonationMatchResource, self).obj_create(bundle, interested=bundle.request.user)

class RequestMatchResource(ModelResource):
    request = fields.ForeignKey(RequestResource, 'request', null=True, full=True)
    interested = fields.ForeignKey(UserResource, 'interested', null=True, full=True)

    class Meta:
        filtering = {
            "interested": ('exact'),
             "request": ('exact')
        }
        queryset = RequestMatch.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()

    def obj_create(self, bundle, **kwargs):
        return super(RequestMatchResource, self).obj_create(bundle, interested=bundle.request.user)