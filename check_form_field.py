#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multibliz_pos.settings')
django.setup()

from sales.forms import ReturnForm

form = ReturnForm()
print('Refund Amount field configuration:')
refund_field = form.fields['refund_amount']
print(f'  Widget type: {type(refund_field.widget).__name__}')
print(f'  Required: {refund_field.required}')
print(f'  Min value: {refund_field.widget.attrs.get("min")}')
print(f'  Step: {refund_field.widget.attrs.get("step")}')
print(f'  Initial: {refund_field.initial}')

# Render the field
print('\nRendered HTML (truncated):')
rendered = str(form['refund_amount'])
print(rendered[:200])
