from rest_framework import serializers


class TaskInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(
        required=False, allow_null=True, min_value=1, max_value=10
    )
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class TaskOutputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(required=False, allow_null=True)
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    score = serializers.FloatField()
    priority_label = serializers.CharField()
    reasons = serializers.ListField(child=serializers.CharField())

    urgency_score = serializers.FloatField()
    importance_score = serializers.FloatField()
    effort_score = serializers.FloatField()
    dependency_score = serializers.FloatField()
