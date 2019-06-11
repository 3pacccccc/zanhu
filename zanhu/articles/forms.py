from django import forms
from markdownx.fields import MarkdownxFormField

from .models import Article


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    edited = forms.BooleanField(widget=forms.HiddenInput(), initial=False, required=False)
    content = MarkdownxFormField()
    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'tags']
