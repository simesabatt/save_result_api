from django import forms

class ImagePathForm(forms.Form):
    image_path = forms.CharField(label='画像ファイルPath', max_length=255)
    debug_mode = forms.BooleanField(required=False, label="デバッグモード")
