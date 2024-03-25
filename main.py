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
from app.carriage import CarriageParams, MoveStages
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


async def carriage_move(*args, carriage_params: CarriageParams):
    async with Carriage(params=carriage_params) as carriage:
        async for stage in carriage.move():
            print(stage)
            if stage == MoveStages.MOVED.value:
                for task in args:
                    task.cancel()


async def scan_anode():
    # message_queue1 = asyncio.Queue()
    # message_queue2 = asyncio.Queue()
    #
    # lidar_task_1 = asyncio.create_task(lidar_worker(1, "192.168.0.3", 2111, message_queue1))
    # lidar_task_2 = asyncio.create_task(lidar_worker(1, "192.168.0.2", 2111, message_queue2))

    carriage_move_task = asyncio.create_task(carriage_move(
        # lidar_task_1,
        # lidar_task_2,
        carriage_params=CarriageParams(port="COM5", baudrate=57600)
    ))

    # message_processing_task1 = asyncio.create_task(process_messages(message_queue1))
    # message_processing_task2 = asyncio.create_task(process_messages(message_queue2))
    #
    # with suppress(asyncio.CancelledError):
    #     await lidar_task_1
    #     await lidar_task_2

    await carriage_move_task

    # coords1 = await message_processing_task1  # после обработки всех сообщений получаем List[List[tuple]]
    # coords2 = await message_processing_task2

    # with open("test1.txt", "w") as file:
    #     file.write(str(coords1))
    # with open("test2.txt", "w") as file:
    #     file.write(str(coords2))


async def main():
    await scan_anode()


if __name__ == '__main__':
    asyncio.run(main())
