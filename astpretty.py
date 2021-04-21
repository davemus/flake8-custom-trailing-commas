raise ValidationError('error message')
raise rest_framework.serializers.ValidationError('error message')
raise ValidationError({'spam': 'eggs'})
raise ValidationError(['eggs'])
