from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskInputSerializer, TaskOutputSerializer
from .scoring import analyze_tasks, DEFAULT_STRATEGY, STRATEGIES


class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/

    Body:
    {
      "tasks": [ ... ],
      "strategy": "smart_balance"
    }
    """

    def post(self, request, *args, **kwargs):
        tasks_data = request.data.get("tasks", [])
        strategy = request.data.get("strategy", DEFAULT_STRATEGY)

        input_serializer = TaskInputSerializer(data=tasks_data, many=True)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enriched = analyze_tasks(input_serializer.validated_data, strategy_name=strategy)
        output_serializer = TaskOutputSerializer(enriched, many=True)

        return Response({
            "strategy": strategy,
            "strategies_available": list(STRATEGIES.keys()),
            "tasks": output_serializer.data,
        }, status=status.HTTP_200_OK)


class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/?strategy=smart_balance

    For the assignment I keep this simple and use a sample set.
    In a real app this would use stored user tasks.
    """

    def get(self, request, *args, **kwargs):
        strategy = request.query_params.get("strategy", DEFAULT_STRATEGY)

        # Demo tasks - to keep focus on algorithm, not persistence
        sample_tasks = [
            {
                "id": "demo_1",
                "title": "Fix login bug",
                "due_date": "2025-11-30",
                "estimated_hours": 3,
                "importance": 9,
                "dependencies": [],
            },
            {
                "id": "demo_2",
                "title": "Write documentation",
                "due_date": "2025-12-15",
                "estimated_hours": 5,
                "importance": 6,
                "dependencies": [],
            },
            {
                "id": "demo_3",
                "title": "Refactor payment module",
                "due_date": "2025-11-28",
                "estimated_hours": 8,
                "importance": 8,
                "dependencies": [],
            },
        ]

        enriched = analyze_tasks(sample_tasks, strategy_name=strategy)
        top3 = enriched[:3]

        output_serializer = TaskOutputSerializer(top3, many=True)
        return Response({
            "strategy": strategy,
            "tasks": output_serializer.data,
            "note": "For the assignment this uses demo tasks; in a real system this would use user-specific stored tasks."
        }, status=status.HTTP_200_OK)
