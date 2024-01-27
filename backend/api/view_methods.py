from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response


def create_obj(serializer, data, context=None):
    save_serializer = serializer(data=data, context=context)
    save_serializer.is_valid(raise_exception=True)
    save_serializer.save()
    return Response(save_serializer.data, status=status.HTTP_201_CREATED)


def create_file(request, ingredients):
    first_name = request.user.first_name
    last_name = request.user.last_name
    text = f'Список покупок пользователя {first_name} {last_name}\n'
    for ingredient in ingredients:
        text += (
            f'{ingredient["ingredient__name"]}: '
            f'{ingredient["amount"]}'
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
    response = FileResponse(
        text,
        as_attachment=True,
        content_type='text/plain',
    )
    return response


def mapping_delete(queryset, message):
    if queryset.exists():
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'errors': message}, status=status.HTTP_400_BAD_REQUEST)
