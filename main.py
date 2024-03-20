"""

Точка входа в которой на коленке собран алгоритм
Движение каретки имитируется в carriage_imitation.
Подключается один тестовый лидар, для подключения уже должен быть поднят сокет-сервер
на порту 50007, для этого запускаем socket_server из tests

После получения и обработки сообщений данные летят в построение графика
можно сохранить их в файл, сохранив coords

"""


import asyncio

from contextlib import suppress

from app import Carriage, lidar_worker, process_messages

from app.tests.test_plot import build_slices_plot


async def simple_test_carriage(carriage: Carriage):
    async for stage in carriage.move():
        print(stage)


async def carriage_imitation(*args):
    for stage in ["started", "moved", "stopped", "started", "moved", "stopped", "returned"]:
        print(f">>> Каретка на этапе: {stage.upper()}")
        await asyncio.sleep(1)
        if stage == "returned":
            for task in args:
                task.cancel()


async def scan_anode():
    message_queue = asyncio.Queue()

    lidar_task_1 = asyncio.create_task(lidar_worker(1, "", 50007, message_queue))

    carriage_move_task = asyncio.create_task(carriage_imitation(lidar_task_1))
    message_processing_task = asyncio.create_task(process_messages(message_queue))

    with suppress(asyncio.CancelledError):
        await lidar_task_1

    await carriage_move_task
    coords = await message_processing_task  # после обработки всех сообщений получаем List[List[tuple]]

    build_slices_plot(coords)


async def main():
    await scan_anode()


if __name__ == '__main__':
    asyncio.run(main())
