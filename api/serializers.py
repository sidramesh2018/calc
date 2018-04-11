from contracts.models import Contract
from rest_framework import serializers


class ContractSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        return Contract.objects.bulk_create([
            Contract(**item) for item in validated_data
        ])


class EducationLevelField(serializers.Field):
    def get_attribute(self, obj):
        return obj

    def to_representation(self, obj):
        return obj.get_education_level_display()

    def to_internal_value(self, data):
        edu_code = Contract.get_education_code(data)

        if not edu_code:
            raise serializers.ValidationError(
                f'Invalid education level: {data}'
            )

        return edu_code


class ContractSerializer(serializers.ModelSerializer):
    # TODO: Figure out whether we actually support a null value for
    # this in the DB. Right now the model claims it can be null or
    # blank, which isn't recommended for strings in Django.
    education_level = EducationLevelField(allow_null=True)

    class Meta:
        model = Contract
        fields = ('id', 'idv_piid', 'vendor_name', 'labor_category',
                  'education_level', 'min_years_experience',
                  'hourly_rate_year1', 'current_price', 'next_year_price',
                  'second_year_price', 'schedule', 'sin', 'contractor_site',
                  'business_size')
        list_serializer_class = ContractSerializer
