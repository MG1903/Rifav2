from django import forms
from django.core.exceptions import ValidationError
import re

class CompraForm(forms.Form):
    nombre = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=False)
    telefono = forms.CharField(max_length=15, required=False)
    numeros_seleccionados = forms.CharField(widget=forms.HiddenInput())
    metodo_pago = forms.ChoiceField(choices=[('fisico', 'Pago Físico'), ('online', 'Pago Online')])
    codigo_pago = forms.CharField(max_length=10, required=True)

    def clean(self):
        cleaned_data = super().clean()
        codigo_pago = cleaned_data.get("codigo_pago")
        email = cleaned_data.get("email")
        telefono = cleaned_data.get("telefono")

        if not email and not telefono:
            self.add_error(None, "Debes ingresar al menos un contacto (email o teléfono).")

        if codigo_pago:
            if not self.validar_codigo_pago(codigo_pago):
                self.add_error('codigo_pago', "El código de pago debe tener 10 dígitos")

    def validar_codigo_pago(self, codigo):
        regex = re.compile(r'^[A-Za-z]{3}[0-9]{7}$')
        if not regex.match(codigo):
            return False

        pares = 0
        impares = 0
        numeros = codigo[3:]

        for char in numeros:
            if int(char) % 2 == 0:
                pares += 1
            else:
                impares += 1

        return pares > impares