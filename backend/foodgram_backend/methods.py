from rest_framework import status
from rest_framework.response import Response


def create_obj(serializer, data, context=None):
    save_serializer = serializer(data=data, context=context)
    if save_serializer.is_valid():
        save_serializer.save()
        return Response(save_serializer.data, status=status.HTTP_201_CREATED)
    return Response(save_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def create_file(request, ingredients):
    text = (
        'Список покупок пользователя'
        f'{request.user.first_name} {request.user.last_name}\n'
    )
    for ingredient in ingredients:
        text += f'{ingredient["recipe__recipes__ingredient__name"]}: '(
            f'{ingredient["amount"]}'
            f'{ingredient["recipe__recipes__ingredient__measurement_unit"]}\n'
        )

    with open(
        (
            f'Список покупок пользователя'
            f'{request.user.first_name} {request.user.last_name}.txt'
        ),
        'w+',
        encoding='utf-8',
    ) as file:
        file.write(text)
        return file


def mapping_delete(queryset, message):
    if queryset.exists():
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'errors': message}, status=status.HTTP_400_BAD_REQUEST)
