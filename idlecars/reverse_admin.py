'''
adminreverse from here http://djangosnippets.org/snippets/2032/
changed for working with ForeignKeys and updated for Django 1.8
'''
'''
reverseadmin
============
Module that makes django admin handle OneToOneFields in a better way.

A common use case for one-to-one relationships is to "embed" a model
inside another one. For example, a Person may have multiple foreign
keys pointing to an Address entity, one home address, one business
address and so on. Django admin displays those relations using select
boxes, letting the user choose which address entity to connect to a
person. A more natural way to handle the relationship is using
inlines. However, since the foreign key is placed on the owning
entity, django admins standard inline classes can't be used. Which is
why I created this module that implements "reverse inlines" for this
use case.

Example:

    from django.db import models
    class Address(models.Model):
        street = models.CharField(max_length = 255)
        zipcode = models.CharField(max_length = 10)
        city = models.CharField(max_length = 255)
    class Person(models.Model):
        name = models.CharField(max_length = 255)
        business_addr = models.ForeignKey(Address,
                                             related_name = 'business_addr')
        home_addr = models.OneToOneField(Address, related_name = 'home_addr')
        other_addr = models.OneToOneField(Address, related_name = 'other_addr')


You use reverseadmin in the following way:

    from django import forms
    from django.contrib import admin
    from django.db import models
    from models import Person
    from reverseadmin import ReverseModelAdmin
    class AddressForm(forms.FormModel):
        class Meta:
            model = Address
    class PersonAdmin(ReverseModelAdmin):
        inline_type = 'tabular'
        inline_reverse = (
            'business_addr',
            ('home_addr', AddressForm), 
            ('other_addr', {
                'form': OtherForm
                'exclude': ()
            })
        )

    admin.site.register(Person, PersonAdmin)

inline_type can be either "tabular" or "stacked" for tabular and
stacked inlines respectively.

The module was designed to work with Django 1.1.1 but was updated for 1.8 in a
GitHub gist.
'''
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.utils import flatten_fieldsets
from django.db.models import OneToOneField, ForeignKey
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.functional import curry
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class ReverseInlineFormSet(BaseModelFormSet):
    model = None
    parent_fk_name = ''
    def __init__(self,
            data = None,
            files = None,
            instance = None,
            prefix = None,
            queryset = None,
            save_as_new = False):
        self.mem_instance = instance
        # sometimes object does not exist
        try:
            object = getattr(instance, self.parent_fk_name)
        except ObjectDoesNotExist:
            object = None

        if object:
            qs = self.model.objects.filter(pk = object.id)
        else:
            qs = self.model.objects.filter(pk = -1)
            self.extra = 1
        super(ReverseInlineFormSet, self).__init__(data, files,
                                                  prefix = prefix,
                                                  queryset = qs)
        for form in self.forms:
            parent_related = getattr(instance.__class__, self.parent_fk_name)
            if not parent_related.field.null:
                form.empty_permitted = False


    def save_new_objects(self,commit):
        """
        The save_new_objects method is overwritten since the id of the new objects has to be
        passed to the parent object. Otherwise the new objects will not be connected
        to theirs "should be parent object".
        """
        super(ReverseInlineFormSet, self).save_new_objects(commit)
        for dream in self.new_objects:
            setattr(self.mem_instance, self.parent_fk_name, dream)
        return self.new_objects

def reverse_inlineformset_factory(parent_model,
                                  model,
                                  parent_fk_name,
                                  form = ModelForm,
                                  fields = None,
                                  exclude = None,
    formfield_callback = lambda f: f.formfield()):
    kwargs = {
           'form': form,
           'formfield_callback': formfield_callback,
           'formset': ReverseInlineFormSet,
           'extra': 0,
           'can_delete': False,
           'can_order': False,
           'fields': fields,
           'exclude': exclude,
           'max_num': 1,
    }
    FormSet = modelformset_factory(model, **kwargs)
    FormSet.parent_fk_name = parent_fk_name
    return FormSet

class ReverseInlineModelAdmin(InlineModelAdmin):
    '''
    Use the name and the help_text of the owning models field to
    render the verbose_name and verbose_name_plural texts.
    '''
    def __init__(self,
            parent_model,
            parent_fk_name,
            model, admin_site,
            inline_type):
        self.template = 'admin/edit_inline/%s.html' % inline_type
        self.parent_fk_name = parent_fk_name
        self.model = model
        field_descriptor = getattr(parent_model, self.parent_fk_name)
        field = field_descriptor.field

        self.verbose_name_plural = field.verbose_name.title()
        self.verbose_name = field.help_text
        if not self.verbose_name:
            self.verbose_name = self.verbose_name_plural
        super(ReverseInlineModelAdmin, self).__init__(parent_model, admin_site)

    def get_formset(self, request, obj = None, **kwargs):
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = (exclude + kwargs.get("exclude", [])) or None
        defaults = {
                "form": self.form,
                "fields": fields,
                "exclude": exclude,
                "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return reverse_inlineformset_factory(self.parent_model,
                           self.model,
                           self.parent_fk_name,
                           **defaults)


class ReverseModelAdmin(ModelAdmin):
    '''
    Patched ModelAdmin class.
    '''
    def __init__(self, model, admin_site):

        super(ReverseModelAdmin, self).__init__(model, admin_site)
        if self.exclude is None:
            self.exclude = []

        inline_instances = []
        for field_name in self.inline_reverse:

            kwargs = {}
            if isinstance(field_name, tuple):
                if isinstance(field_name[1], dict):
                    kwargs = field_name[1]
                elif isinstance(field_name[1], ModelForm):
                    kwargs['form'] = field_name[1]
                field_name = field_name[0]

            field = model._meta.get_field(field_name)
            if isinstance(field, (OneToOneField, ForeignKey)):
                name = field.name
                parent = field.related.model
                inline = ReverseInlineModelAdmin(
                    model,
                    name,
                    parent,
                    admin_site,
                    self.inline_type,
                )
                if kwargs:
                    inline.__dict__.update(kwargs)
                inline_instances.append(inline)
                self.exclude.append(name)
        self.inline_instances = [inline_class(self.model, self.admin_site) for inline_class in self.inlines] # new approach for inline_instances
        self.inline_instances = inline_instances + self.inline_instances

    def get_inline_instances(self, request, *args, **kwargs):
        """
        ModelAdmin's method is overridden here for setting inline instances the way we need in inverse inlines.
        It is necessary for compatibility with changes in Django 1.4
        """
        return self.inline_instances

    def save_model(self, *args, **kwargs):
        """ Since the inline objects has to be saved first, the main object saving has to be postponed."""
        pass

    def response_add(self, request, obj, post_url_continue=None):
        """The response_add() is overridden to save the main object."""
        obj.save()
        return super(ReverseModelAdmin, self).response_add(request,obj, post_url_continue=None)

    def response_change(self, request, obj):
        """The response_change() is overridden to save the main object."""
        obj.save()
        return super(ReverseModelAdmin, self).response_change(request,obj)
